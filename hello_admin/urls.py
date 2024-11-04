from django.conf import settings

from django.conf.urls.static import static
from django.urls import path, include
from hello_admin.views import *

app_name = "hello_admin"

urlpatterns = [
    path('', home_page, name='home'),
    path('login/', login_page, name='login'),
    path('logout/', logout_user, name='logout'),
    path('<int:user_id>/update_role/', update_role, name='update_role'),
    path('<int:user_id>/update_profile/', update_profile, name='update_profile'),
    path('<int:user_id>/change_password/', change_password, name='change_password'),
    path('<int:user_id>/delete_user/', delete_user, name='delete_user'),
    path('create_user/', create_user, name='create_user'),

    path('<int:user_id>/ban_user/', ban_user, name='ban_user'),
    path('<int:user_id>/unban_user/', unban_user, name='unban_user'),
]