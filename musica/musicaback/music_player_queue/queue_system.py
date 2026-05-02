from django.shortcuts import render
import uuid

from django.shortcuts import render, redirect, reverse
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage

from django.contrib.auth.decorators import login_required

from django.contrib import messages
from ..models import EmailVerificationCode, Profile, Music
from django.core.mail import send_mail
from random import randint
from django.conf import settings
# Create your views here.
from django.db.models.signals import post_save
from django.core.cache import cache
from django.dispatch import receiver
import threading


import secrets

import json

from django.http import JsonResponse


from asgiref.sync import sync_to_async, async_to_sync


from allauth.socialaccount.signals import social_account_added

from datetime import datetime, date

from dateutil.relativedelta import relativedelta
import requests
from ..music_search_engine import search_engine, search_music
from ..auto_mixer import grab_music_bpm

from ..music.music_downloader import grab_music_download, safe_filename
from ..views import  grab_music_bpm
from ..music_search_engine import search_engine
from decimal import Decimal

from random import shuffle




# We wanna check if the songs are being played from the playlist 

# If not we can do a randomized playlist, and if the user does the repeat system, 
# then let the queue be that song


# Redirect it but the only problem is how do we make the redirection not obvious
# so we need high speed, I purpose threading for this endeavour

# Works when you click randomized button 
def randomized_playlist_request(request):
    # Grab the model from the playlist 
    playlist = list(Music.objects.get.all())
    if not playlist:
        return JsonResponse({"playlist": []})
    # We wanna shuffle it...
    shuffle(playlist)
    # Grab the playlist music
    playlist = playlist[:20]
    
    song = [
        {
            "title": song.title,
            "artist": song.artist,
            "image": song.images.url if song.images else None,
            "audio_url": song.audio_file.url if song.audio_file else None,
        }
        for song in playlist
    ]
    return JsonResponse({'playlist': playlist})
    
    
    
    

    

def create_random_playlist_sets(request, music_name: str, artist_name: str):
    # We want to populate the Music objects, because this is the key for the music generated playlist to be world-class, so I purpose we use deezer query
    # use our music that we have in our music_player and then generate it
    cache_key = f"deezer_metadata:{artist_name.lower()}:{music_name.lower()}"
    # Cache it so we don't spend too much on API calls that are frequent haha
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Time to use Django's ORM in order to filter the Musib object to find the exact artist and music naem and find it in the database
    
    song = Music.objects.filter(
        title__iexact=music_name,
        artist__iexact=artist_name
    ).first()
    
    if song and song.genre:
        data = {
            "title": song.title,
            "artist": song.artist,
            "genre": song.genre,
            "deezer_id": song.deezer_id,
            "image_url": song.image_url,
        }
        cache.set(cache_key, data, 60 * 60 * 24)
        return data
    data = get_song_data(music_name, artist_name)
    
    if data:
        # Store in our Database
        Music.objects.update_or_create(
            deezer_id=data['deezer_id'],
            defualts={
                "title": data["title"],
                "artist": data["artist"],
                "genre": data["genre"],
                "image_url": data["image_url"],

            }
        )
        cache.set(cache_key, data, 60 * 60 * 24)
    return data



def get_song_data(song_name: str, artist_name:str):
    query =  song_name 
    cache_key = f"deezer:{query}"
    
    if artist_name:
        query = f"{artist_name} {song_name}"

    search_res = requests.get(
        "https://api.deezer.com/search",
        params={"q": query}
    )
    
    search_data = search_res.json()
    tracks = search_data.get("data", [])
    
    track = tracks[0]
    
    album_id = track["album"]["id"]

    album_res = requests.get(
        f"https://api.deezer.com/album/{album_id}"
    )
    
    
    album_data = album_res.json()

    genres = album_data.get("genres", {}).get("data", [])

    genre_name = genres[0]["name"] if genres else "Unknown"


    return {
        "deezer_id": str(track["id"]),
        "title": track["title"],
        "artist": track["artist"]["name"],
        "album": track["album"]["title"],
        "album_id": str(album_id),
        "image_url": track["album"]["cover_medium"],
        "preview_url": track.get("preview"),
        "genre": genre_name,
    }
    
# For the playlist one, we gotta ensure that the previous url was actually from the playlist music :) So this is a TBD hehe, and I want to create like a 

