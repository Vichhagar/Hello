from django.conf import settings

from django.conf.urls.static import static
from django.urls import path, include
from .views import *


app_name = "hello_public"

urlpatterns = [
    path('', home_page, name='home'),
    path('login/', login_page, name='login'),
    path('logout/', logout_user, name='logout'),
    path('register/', register, name='register'),
    path('requestaccount/', request_account, name='requestaccount'),
    path('register/', register, name='register'),

    # Post
    path('post/create/', create_post, name='create_post'),
    path('post/<int:post_id>/', post_detail, name='post_detail'),
    path('post/<int:post_id>/like/', add_like, name='add_like'),
    path('post/<int:post_id>/save/', add_save, name='add_save'),
    path('post/<int:post_id>/edit/', edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', delete_post, name='delete_post'),

    path('post/<int:post_id>/report/', create_report, name='create_report'),
    # path('post/<int:post_id>/add_comment/', add_comment, name='add_comment'),

    # this is for comment
    path('post/add_reply/<int:comment_id>/', add_reply, name='add_reply'),
    path('comments/<int:comment_id>/edit/', edit_comment, name='edit_comment'),
    path('comments/<int:comment_id>/delete/', delete_comment, name='delete_comment'),

    path('reply/<int:reply_id>/edit/', edit_reply, name='edit_comment'),
    path('reply/<int:reply_id>/delete/', delete_reply, name='delete_comment'),

    path('comment/moderator/<int:comment_id>/delete/', moderator_delete_comment, name='moderator_delete_comment'),
    path('reply/moderator/<int:reply_id>/delete/', moderator_delete_reply, name='moderator_delete_reply'),

    # ACTIVITIES URLs
    # path('activities/', activity_list, name='activity_list'),
    path('activity/create/', create_activity, name='activity_create'),
    path('activity/<int:pk>/', activity_detail, name='activity_detail'),
    path('activity/<int:pk>/edit/', edit_activity, name='activity_edit'),
    path('activity/<int:pk>/join/', join_activity, name='activity_join'),
    path('activity/<int:pk>/leave/', leave_activity, name='activity_leave'),
    path('activity/<int:pk>/delete/', delete_activity, name='delete_activity'),

    path('activity/<int:activity_id>/add_discussion_message/', add_discussion_message, name='add_discussion_message'),
    path('all_activities/', activity_list, name='activities'),


    # path('post/<int:post_id>/load_comments/', load_comments, name='load_comments'),

    # USER DASHBOARD
    path('dashboard/', user_dashboard, name='user_dashboard'),
    path('other_dashboard/<int:user_id>/', other_user_dashboard, name='other_user_dashboard'),
    path('saved_posts/', saved_posts, name='saved_posts'),
    path('all_notification/', all_notification, name='all_notification'),

    # USER ACTIONS
    path('delete_account/', delete_account, name='delete_account'),
    path('update_account_password/', update_password, name='update_password'),
    path('update_account_profile/', edit_profile, name='edit_profile'),

    # NOTIFICATION
    path('get_notification/', get_notifications, name='get_notification'),
    path('notifications/mark_as_read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),
    # path('message/<int:notification_id>/', get_notification_message, name='get_message'),

    # IGNORE NOTIFICATION
        path('ignore-notification/add/<int:user_id>/', add_ignore, name='add_ignore'),
        path('ignore-notification/remove/<int:user_id>/', remove_ignore, name='remove_ignore'),

    path('activity_location_suggestions/', ActivityLocationSuggestionsView.as_view(), name='activity_location_suggestions'),
]

handler404 = 'hello_public.views.error_404'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, 
                        document_root=settings.MEDIA_ROOT)