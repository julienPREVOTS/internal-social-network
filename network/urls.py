
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_post", views.create_post, name="create_post"),
    path("user_profile/<int:user_id>", views.user_profile, name="user_profile"),
    path("following", views.following, name="following"),
    path("like_post/<int:post_id>", views.like_post, name="like_post"),
    path("edit_post/<int:post_id>", views.edit_post, name="edit_post"),
    path("follow_user/<int:user_id>", views.follow_user, name="follow_user")
]
