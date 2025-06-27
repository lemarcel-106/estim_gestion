
from django.shortcuts import redirect, render
from django.urls import path
from django.conf import settings
from views.website.login import LoginView, LogoutView
from views.website.home import HomeView


urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('home/', HomeView.as_view(), name='home'),
    path('logout/', LogoutView.as_view(), name='logout'),
]

