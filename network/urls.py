
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_post",views.create_post,name="create_post"),
    path("profile/<str:username>",views.profile,name="profile"),
    path("following",views.following,name="following"),
    path("edit_post/<int:post_id>",views.edit_post,name="edit_post"),
    path("delete/<int:post_id>",views.delete,name="delete"),

    #API
    path("like/<int:post_id>",views.like,name="like"),
    path("follow/<str:username>/<str:mission>",views.follow,name="follow")
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
