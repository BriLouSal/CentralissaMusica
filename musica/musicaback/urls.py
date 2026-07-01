from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings



from . import views, music_api, music_search_engine,auto_mixer, rate_limit_auth, music_player
from .music_player_queue.queue_system import randomized_playlist_request, create_random_playlist_sets


from .music_player_queue.spatial_audio_setup import audio_analysis, spectral_masking

urlpatterns = [
    path(
        "accounts/3rdparty/login/cancelled/",
        lambda request: redirect("signup"),
    ),
    path('home/', views.home, name='home'),
    
    path('', views.signup_page, name='signup'),  
    
    path('login/' , views.loginpage, name='login'),
    
    path('timeout/', rate_limit_auth.timeout_view, name='timeout'),
    
    path('spotify/' , music_api.spotify_connect, name='spotify'),
    
    path('spotify/callback/', music_api.spotify_callback_to_views, name='spotify_callback'),
    
    path('music-search/autocomplete/<str:query>/', music_search_engine.music_search_view, name='search_views'),

    
    
    path('artist/<int:artist_id>/', views.artist_page, name='artist_page'),
    
    path('music/<str:artist_name>/<str:music_name>/', music_player.music_player, name='music_player'),
    
    path('album/<str:artist_name>/<str:album_name>/', views.album_page, name='album_view'),
    
    path('musica/randomized_playlist/', randomized_playlist_request, name='random_playlist'),
   
    path('musica/generate_random_query/<str:music_name>/<str:artist_name>/', create_random_playlist_sets, name='create_random_playlist_sets'),
    

    # Music setup
    
    path(
    'play_music/<str:artist_name>/<str:music_name>/',
    music_player.play_music,
    name='play_music'),
    
    path(
    'audio_analysis/<str:audio_name>/<str:artist_name>/',
    audio_analysis,
    name='audio_analysis'),
    
    path(
    'spectral_masking/<str:audio_name>/<str:artist_name>/',
    spectral_masking,
    name='spectral_masking'),
    
    
    
    # path('musica/slowed_music/<str:file_name>/<float:slowed_size>/', slowed_music, name='slowed_music'),
    
    
    
   
]

if settings.DEBUG:
    # Include django_browser_reload URLs only in DEBUG mode
    urlpatterns += [
        path("__reload__/", include("django_browser_reload.urls")),
    ]
    