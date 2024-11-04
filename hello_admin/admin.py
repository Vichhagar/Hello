from django.contrib import admin

from django.conf import settings

from django.conf.urls.static import static
from django.urls import path, include
from .views import *


app_name = "hello_admin"

urlpatterns = [
    # path('', home_page, name='home'),
    # path('login/', login_page, name='login'),
    # path('logout/', logout_user, name='logout'),
]