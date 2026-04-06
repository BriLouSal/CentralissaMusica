from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings


from . import views, music_api, music_search_engine


urlpatterns = [
    path(
        "accounts/3rdparty/login/cancelled/",
        lambda request: redirect("signup"),
    ),
    path('home/', views.home, name='home'),
    
    path('', views.signup_page, name='signup'),  
    path('login/' , views.loginpage, name='login'),
    path('spotify/' , music_api.spotify_connect, name='spotify'),
    path('spotify/callback/', music_api.spotify_callback_to_views, name='spotify_callback'),
    path('music-search/autocomplete/<str:query>/', music_search_engine.music_search_view, name='search_views'),
    path('music-player/<str:music_name>/', views.music_player, name='music_player'),
    path('artist/<str:artist_name>/', views.artist_page, name='artist_page'),
]

if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]