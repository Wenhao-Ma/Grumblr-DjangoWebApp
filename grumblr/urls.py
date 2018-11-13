from django.urls import path
from grumblr.views import *


urlpatterns = [
    path('login/', log_in, name='login'),
    path('register/', register, name='register'),
    path('activate/<str:username>/<str:token>', confirm_registration, name='confirm_reg'),
    path('home/<str:username>/', home, name='home'),
    path('home/<str:username>/edit/', edit, name='edit'),
    path('home/<str:username>/follow/', follow, name='follow'),
    path('home/<str:username>/unfollow/', unfollow, name='unfollow'),
    path('global/', glob, name='global'),
    path('global/get-posts', global_posts, name='global-posts'),
    path('global/update/<str:time>', global_update, name='global-update'),
    path('follower/', follower, name='follower'),
    path('delete/<int:id>/', delete_post, name='delete'),
    path('add_fav/<int:id>/', add_fav, name='fav'),
    path('delete_fav/<int:id>/', delete_fav, name='del_fav'),
    path('reset_password', reset_password_request, name='reset'),
    path('reset_password/<str:username>/<str:token>', confirm_password, name='confirm_pwd'),
    path('photo/<str:username>', get_photo, name='photo'),
    path('header/<str:username>', get_header, name='header_photo'),
    path('add-comment/<str:id>', add_comment),
    path('get-comment/<str:id>', get_comment),
    path('logout/', log_out, name='logout'),
]