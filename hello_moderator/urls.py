from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from hello_moderator.views import *


app_name = "hello_moderator"

urlpatterns = [
    path('', home_page, name='home'),
    path('login/', login_page, name='login'),
    path('logout/', logout_user, name='logout'),
    path('posts/', all_post, name='posts'),
    path('activities/', all_activities, name='activities'),
    
    # POST ACTIONS
    path('post/<int:post_id>/approve/', approve_post, name='approve_post'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),

    path('post/<int:post_id>/ban/', ban_post, name='ban'),
    path('post/<int:post_id>/unban/', unban_post, name='unban'),

    path('post/<int:post_id>/disable_comment/', disable_comment_on_post, name='disable_comment'),
    path('post/<int:post_id>/enable_comment/', enable_comment_on_post, name='enable_comment'),

    path('report/<int:post_id>/view/', report_detail, name='report_detail'),
    path('report/<int:report_id>/delete/', delete_report, name='delete_report'),

    # ACTIVITY ACTIONS
    path('activity/<int:activity_id>/delete/', delete_activity, name='delete_activity'),
]