from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from . import views


urlpatterns = [
    path(
        "accounts/3rdparty/login/cancelled/",
        lambda request: redirect("signup"),
    ),
    path('home/', views.home, name='home'),
    
    path('', views.signup_page, name='signup'),  
    path('login/' , views.loginpage, name='login'),
]

if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]