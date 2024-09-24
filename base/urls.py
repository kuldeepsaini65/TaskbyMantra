from django.contrib import admin
from django.urls import path, include
from base.views import *


urlpatterns = [
    path('signin', SignIn, name="SignIn"),
    path('signup', SignUp, name="SignUp"),
    path('logout', LogOut, name="LogOut"),
    path('', Home, name="home"),
]
