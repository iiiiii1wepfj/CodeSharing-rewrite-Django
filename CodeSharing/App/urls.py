from django.urls import path

from .views import (
    Main,
    search,
    upload_file,
    my_files,
    forgot_my_password,
    loginV,
    logoutV,
    signupV,
    view_file,
    delete_file,
    comments,
    change_password,
    password_reset,
)

urlpatterns = [
    path("", Main, name="Main"),
    path("search", search, name="search"),
    path("uploadfile/", upload_file, name="upload_file"),
    path("myfiles/", my_files, name="my_files"),
    path("changepass/", change_password, name="change_password"),
    path("forgotpass/", forgot_my_password, name="forgot_password"),
    path("resetpass/", password_reset, name="password_reset"),
    path("login/", loginV, name="login"),
    path("logout/", logoutV, name="logout"),
    path("signup/", signupV, name="signup"),
    path("viewfile/", view_file, name="viewfile"),
    path("delete_file/<int:file_id>/", delete_file, name="delete_file"),
    path("comments", comments, name="comments"),
]
