from django import template
from ..models import Comment

register = template.Library()


@register.simple_tag(takes_context=True)
def calldisplayreplies(context, comment):
    return display_replies(
        comment=Comment.objects.get(id=comment),
        request=context["request"],
        csrftoken=context.get("csrf_token", ""),
        level=1,
    )


def display_replies(comment, request, csrftoken, level):
    replies = Comment.objects.filter(parentComment=comment)
    num_replies = replies.count()
    htmlcode = ""

    if num_replies > 0:
        for reply in replies:
            marginleft = f"{level*20}px"
            htmlcode += f"""
                <div style="background-color: #f9f9f9; padding: 20px; border-radius: 10px; margin-left: {marginleft}; margin-bottom: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <div style="display: flex; align-items: center;">
                        <p style="font-weight: bold; color: #333; margin-bottom: 5px;">{reply.user.username}</p>
            """

            if (
                (reply.user == request.user)
                or request.user.is_staff
                or (request.user == reply.linkedto.user)
            ):
                htmlcode += f"""
                    <form method="post" style="margin-left: 10px;">
                        <input type="hidden" name="csrfmiddlewaretoken" value="{csrftoken}"/>
                        <input type="hidden" name="comment_id" value="{reply.id}">
                        <button type="submit" class="btn btn-link"><i class="fa-regular fa-trash-can" style="font-size:26px;color:red; cursor: pointer;"></i></button>
                    </form>
                """

            if request.user == reply.user:
                htmlcode += f"""
                    <button type="button" onclick="editComment({ reply.id }, '{ reply.comment }')" style="background-color: #f9f9f9; border: none; margin-left: 10px; class="btn btn-link" data-bs-toggle="modal" data-bs-target="#editModal"><i class="fa-regular fa-pen-to-square" style="font-size:26px; color: #0d6efd;"></i></button>
                """
            htmlcode += "</div>"
            htmlcode += f"""
                <p dir="auto" style="font-size: 16px; color: #666; margin-top: 10px;">{reply.comment}</p>
            """

            if request.user.is_authenticated:
                htmlcode += f"""
                    <div>
                        <button type="button" onclick='toggleReplyForm({reply.id})' class="btn btn-primary btn-sm" style="margin-bottom: 10px; margin-left: {marginleft};">click to reply</button>
                    </div>
                    <form id="publishreplyform_{reply.id}" name="publishreplyform_{reply.id}" method="post" style="margin-bottom: 20px; display: none;" dir="auto">
                    <input type="hidden" name="csrfmiddlewaretoken" value="{csrftoken}"/>
                        <fieldset>
                            <div class="form-floating mb-3">
                                <textarea class="form-control" placeholder="content" dir="auto" name="commentcontenttosubmit" id="commentcontenttosubmit" style="height: 100px" required></textarea>
                                <label for="commentcontenttosubmit">reply content</label>
                            </div>
                            <input type="hidden" name="parentCommentId" id="parentCommentId" value='{reply.id}' />
                            <input type="submit" class="btn btn-primary btn-sm" name="submit" value="publish comment" style="padding: 5px 10px; border: none; cursor: pointer;"/>
                        </fieldset>
                    </form>
                """

            htmlcode += display_replies(reply, request, csrftoken, level + 1)
            htmlcode += "</div>"

    return htmlcode
