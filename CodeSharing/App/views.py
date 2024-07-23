from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views.generic import TemplateView
from django.template import loader
from django.contrib.auth import logout, authenticate, login
from django.core.paginator import Paginator, EmptyPage
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.http import HttpResponseForbidden
from django.utils.http import url_has_allowed_host_and_scheme
from .models import File, Comment, ResetCodes, User
from .forms import SearchForm
from .utils.resetcodesutils import autodelcodes
from .utils.genrand import grnd
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# from .commentutils.comments_utils import display_replies


def admin_check(user):
    return user.is_staff


# Create your views here.
def Main(request):
    context = {
        "is_authenticated": request.user.is_authenticated,
    }
    return render(request, "Main.html", context)


def search(request):
    search_input = request.GET.get("search_input", "")
    page_size = request.GET.get("page_size", 10)
    page_number = request.GET.get("page", 1)
    msg = ""
    stsearch = ""
    msgdisply = False
    try:
        if search_input:
            search_results = File.objects.filter(title__icontains=search_input)
            if not search_results.exists():
                msg = f"There aren't any results for '{search_input}'"
                context = {
                    "displaymsg": True,
                    "msg": msg,
                    "form": SearchForm(
                        initial={"search_input": search_input, "page_size": page_size}
                    ),
                }
                return render(request, "search.html", context)
            else:
                paginator = Paginator(search_results, page_size)
                page_obj = paginator.get_page(page_number)
                total_pages = paginator.num_pages
        else:
            msgdisply = True
            page_obj = None
            total_pages = 0

        form = SearchForm(
            initial={"search_input": search_input, "page_size": page_size}
        )

        context = {
            "displaymsg": msgdisply,
            "form": form,
            "msg": msg,
            "stsearch": page_obj,
            "currentPage": int(page_number),
            "totalPages": total_pages,
        }

        return render(request, "search.html", context)
    except (EmptyPage, ZeroDivisionError, ValueError):
        msg = "the page size is invalid"
        context = {
            "displaymsg": True,
            "form": SearchForm(
                initial={"search_input": search_input, "page_size": page_size}
            ),
            "msg": msg,
            "stsearch": None,
        }
        return render(request, "search.html", context)


def get_success_url(request):
    redirect_to = request.POST.get("next", request.GET.get("next")) or "/"
    url_is_safe = url_has_allowed_host_and_scheme(
        url=redirect_to,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    )
    if url_is_safe:
        return redirect_to
    else:
        if request.POST["next"]:
            return resolve_url(request.POST["next"])
        raise ImproperlyConfigured("No URL to redirect to. Provide a next_page.")


def loginV(request):
    if request.user.is_authenticated == True:
        return redirect("/")
    if request.method == "POST":
        conetxt = {}
        if (
            request.POST["username"].strip() != ""
            and request.POST["password"].strip() != ""
        ):
            user = authenticate(
                request,
                username=request.POST["username"],
                password=request.POST["password"],
            )
            if user is not None:
                login(request, user)
                return redirect(get_success_url(request))
            else:
                context = {
                    "error": True,
                    "e": "The username or password you entered is incorrect. Please try again.",
                }
        else:
            context = {
                "error": True,
                "e": "The username or password you entered is incorrect. Please try again.",
            }

        return render(request, "login.html", context)

    context = {
        "error": False,
    }
    return render(request, "login.html", context)


def signupV(request):
    if request.user.is_authenticated == True:
        return redirect("/")
    context = {}
    if request.method == "POST":
        if (
            request.POST["username"].strip() != ""
            and request.POST["email"].strip() != ""
            and request.POST["password"].strip() != ""
            and request.POST["firstname"].strip() != ""
            and request.POST["lastname"].strip() != ""
        ):
            if len(request.POST["username"]) > 150:
                context = {
                    "error": True,
                    "e": "The username can not be longer than 150 characters.",
                }
                return render(request, "signup.html", context)
            if len(request.POST["email"]) < 254:
                try:
                    validate_email(request.POST["email"])
                except ValidationError as E:
                    context = {"error": True, "e": "Enter a valid email address."}
                    return render(request, "signup.html", context)
            else:
                context = {
                    "error": True,
                    "e": "The email address can not be longer than 254 characters.",
                }
                return render(request, "signup.html", context)
            if len(request.POST["firstname"]) > 150:
                context = {
                    "error": True,
                    "e": "The first name can not be longer than 150 characters.",
                }
                return render(request, "signup.html", context)
            if len(request.POST["lastname"]) > 150:
                context = {
                    "error": True,
                    "e": "The last name can not be longer than 150 characters.",
                }
                return render(request, "signup.html", context)
            if User.objects.filter(username=request.POST["username"]).exists() == True:
                context = {
                    "error": True,
                    "e": "The username you selected is not available. Please choose a different one.",
                }
                return render(request, "signup.html", context)
            if User.objects.filter(email=request.POST["email"]).exists() == True:
                context = {
                    "error": True,
                    "e": "The email you selected is not available. Please choose a different one.",
                }
                return render(request, "signup.html", context)
            user = User.objects.create_user(
                username=request.POST["username"],
                email=request.POST["email"],
                password=request.POST["password"],
                first_name=request.POST["firstname"],
                last_name=request.POST["lastname"],
            )
            user.save()
            login(request, user)
            return redirect("/")
        else:
            context = {
                "error": True,
                "e": "The email, username, first name, last name, or password cannot be empty or contain only spaces. Please try again.",
            }
            return render(request, "signup.html", context)
    context = {
        "error": False,
    }

    return render(request, "signup.html", context)


def logoutV(request):
    if request.user.is_authenticated == True:
        logout(request)
        return redirect("/login")

    return redirect("/login")


@login_required
def upload_file(request):
    if request.method == "POST":
        title = request.POST["title"]
        lang = request.POST["lang"]
        content = request.POST["content"]
        info = request.POST["info"]
        if title.strip() != "":
            file = File(
                title=title, content=content, user=request.user, lang=lang, info=info
            )
            file.save()
            return redirect("/myfiles")
        else:
            context = {
                "error": True,
                "e": "The title cannot be empty or contain only spaces. Please try again.",
            }
            return render(request, "signup.html", context)
    context = {
        "error": False,
    }
    return render(request, "upload_file.html", context)


def view_file(request):
    fileid = request.GET.get("id")
    if (fileid.strip() == "") or (not fileid):
        context = {"error": True, "e": "You must to enter an id."}
        return render(request, "view_file.html", context)
    if not (
        (fileid.isdigit()) and (int(fileid) == float(fileid)) and (int(fileid) > 0)
    ):
        context = {"error": True, "e": "The id must be a valid number."}
        return render(request, "view_file.html", context)
    fileid = int(fileid)
    if File.objects.filter(id=fileid).exists() == False:
        context = {"error": True, "e": "The file doesn't exist."}
        return render(request, "view_file.html", context)
    file = File.objects.get(id=fileid)
    # lang = "(auto)"
    filename = file.title
    username = file.user.username
    lang = file.lang
    code = file.content
    description = file.info
    langclass = "language-" + lang
    commentslink = f"/comments?id={fileid}"
    commentsnum = len(Comment.objects.filter(linkedto=file))
    context = {
        "error": False,
        "filename": filename,
        "code": code,
        "username": username,
        "lang": lang,
        "description": description,
        "commentslink": commentslink,
        "commentsnum": commentsnum,
        "langclass": langclass,
    }
    return render(request, "view_file.html", context)


@login_required
def my_files(request):
    try:
        items_per_page = request.GET.get("itemsPerPage", 5)
        files_list = File.objects.filter(user=request.user)
        paginator = Paginator(files_list, items_per_page)

        page_number = request.GET.get("page")
        files = paginator.get_page(page_number)
        context = {
            "msg": False,
            "msgcontent": "",
            "files": files,
            "items_per_page": items_per_page,
        }
        return render(request, "my_files.html", context)
    except (EmptyPage, ZeroDivisionError, ValueError):
        return redirect("/myfiles")


@login_required
def delete_file(request, file_id):
    if File.objects.filter(id=file_id).exists() == False:
        return redirect("/myfiles")
    file = get_object_or_404(File, id=file_id)
    if file.user != request.user:
        return HttpResponseForbidden()
    file.delete()
    return redirect("/myfiles")


def comments(request):
    fileid = request.GET["id"]
    if File.objects.filter(id=fileid).exists() == False:
        return redirect("/search")
    if request.user.is_authenticated:
        if request.method == "POST":
            if "commentcontenttosubmit" in request.POST:
                content = request.POST["commentcontenttosubmit"]
                if content:
                    if "parentCommentId" in request.POST:
                        parentCommentId = request.POST["parentCommentId"]
                        Comment.objects.create(
                            user=request.user,
                            linkedto=File.objects.get(id=fileid),
                            comment=content,
                            parentComment=Comment.objects.get(id=parentCommentId),
                        )
                    else:
                        Comment.objects.create(
                            user=request.user,
                            linkedto=File.objects.get(id=fileid),
                            comment=content,
                        )
            elif "edit_content" in request.POST:
                comment_id = request.POST["comment_id"]
                if (
                    request.user == Comment.objects.get(id=comment_id)
                ) or request.user.is_staff:
                    content = request.POST["edit_content"]
                    comment = get_object_or_404(Comment, id=comment_id)
                    if comment.user == request.user:
                        comment.comment = content
                        comment.save()
                else:
                    return HttpResponseForbidden()
            elif "comment_id" in request.POST:
                comment_id = request.POST["comment_id"]
                if request.user == Comment.objects.get(id=comment_id).user:
                    comment = get_object_or_404(Comment, id=comment_id)
                    if comment.user == request.user or request.user.is_staff:
                        comment.delete()
                else:
                    return HttpResponseForbidden()
    else:
        return redirect("/login")

    comments = Comment.objects.filter(linkedto=fileid)
    title = File.objects.get(id=fileid).title

    context = {
        "comments": comments,
        "title": title,
        "fileid": fileid,
    }
    return render(request, "comments.html", context)


"""
@user_passes_test(admin_check)
def users_table(request):
    return render(request, 'users_table.html')

@user_passes_test(admin_check)
def files_without_comments(request):
    return render(request, 'files_without_comments.html')
"""


def forgot_my_password(request):
    autodelcodes()
    if request.user.is_authenticated:
        return redirect("/")
    showmsg = False
    msg = ""
    if request.method == "POST":
        showmsg = True
        if request.POST["username"].strip() == "" or not "username" in request.POST:
            msg = "Enter username."
        else:
            uname = request.POST["username"]
            if User.objects.filter(username=uname).exists() == False:
                msg = "The username does not exist."
            else:
                usr = User.objects.get(username=uname)
                if (ResetCodes.objects.filter(user=usr)).exists() == False:
                    codetosend = grnd(15)
                    rcode = ResetCodes(user=usr, code=codetosend)
                    rcode.save()
                else:
                    codetosend = ResetCodes.objects.get(user=usr).code
                msgtitle = f"{uname}'s code for password reset in Code Sharing"
                htmlmsg = f"""
                    <div style="background-color: #f0f0f0; border-radius: 8px; padding: 20px; text-align: center;">
                        <h1 style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; font-size: 2rem;">{uname}'s code for password reset in Code Sharing</h1>
                        <div style="margin-top: 20px;">
                            <span style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #007bff; font-size: 1.5rem; font-weight: bold; border: 2px solid #007bff; padding: 10px 20px; border-radius: 8px;">{codetosend}</span>
                        </div>
                        <div style="margin-top: 20px;">
                            <p style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #666; font-size: 1rem;">This code is single-use and will expire 30 minutes after creation.</p>
                        </div>
                    </div>
                    """
                htmlmsg = MIMEText(htmlmsg, "html")
                emailmsg = MIMEMultipart("alternative")
                emailmsg.attach(htmlmsg)
                try:
                    # send_mail(subject=msgtitle, message=htmlmsg, from_email=settings.EMAIL_HOST_USER, recipient_list=[usr.email], fail_silently=False)
                    with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
                        smtp.starttls()
                        smtp.login(
                            settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD
                        )
                        smtp.sendmail(
                            settings.DEFAULT_FROM_EMAIL, usr.email, emailmsg.as_string()
                        )
                    msg = f"Password reset code sent to your email.\nThe code is for one time use and will expire in 30 minutes.\nThe code was sent from the following address: {settings.EMAIL_HOST_USER}"
                except smtplib.SMTPException:
                    msg = "Failed to send the email."
    context = {"showmsg": showmsg, "msg": msg}
    return render(request, "forgotpass.html", context)


def password_reset(request):
    autodelcodes()
    if request.user.is_authenticated:
        return redirect("/")
    showmsg = False
    msg = ""
    if request.method == "POST":
        e_code = request.POST["rescode"]
        if request.POST["password"].strip() == "":
            showmsg = True
            msg = "The password can not be empty."
        else:
            if (
                ResetCodes.objects.filter(
                    code=e_code,
                    user=User.objects.get(username=request.POST["username"]),
                ).exists()
                == False
            ):
                if request.POST["password"] == request.POST["passverify"]:
                    user = User.objects.get(username=request.POST["username"])
                    user.set_password(request.POST["password"])
                    user.save()
                    ResetCodes.objects.get(
                        code=e_code,
                        user=User.objects.get(username=request.POST["username"]),
                    ).delete()
                else:
                    showmsg = True
                    msg = "Passwords does not match."

            else:
                showmsg = True
                msg = "The code does not exist."
    context = {"showmsg": showmsg, "msg": msg}
    return render(request, "passreset.html", context)


@login_required
def change_password(request):
    showmsg = False
    msg = ""
    if request.method == "POST":
        showmsg = True
        if request.POST["password"].strip() == "":
            msg = "The password can not be empty."
        else:
            if request.POST["password"] == request.POST["passverify"]:
                if request.user.check_password(request.POST["currpass"]):
                    request.user.set_password(request.POST["password"])
                    request.user.save()
                    return redirect("/")
                else:
                    msg = "The current password is incorrect."
            else:
                msg = "Passwords does not match."
    context = {"showmsg": showmsg, "msg": msg}
    return render(request, "changepass.html", context)
