from django.shortcuts import render, redirect, reverse
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.core.mail import send_mail, EmailMessage

from django.contrib.auth.decorators import login_required

from django.contrib import messages
from .models import EmailVerificationCode, Profile
from django.core.mail import send_mail
from random import randint
from django.conf import settings
# Create your views here.
from django.db.models.signals import post_save
from django.core.cache import cache

import threading

import secrets

import json
from django.http import JsonResponse

import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth



import requests

load_dotenv()




SPOTIFY_API = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_SECRET_KEY = os.getenv('SPOTIFY_SECRET_KEY')




SOUNDCHARTS_API_KEY = os.getenv('SOUNDCHARTS_API_KEY')
SOUNDCHARTS_APP_ID = os.getenv('SOUNDCHARTS_APP_ID')




# Reference: https://medium.com/@michaelmiller0998/extracting-song-data-from-spotify-using-spotipy-167728d0a924
def grab_uuid(music_name: str) -> str:
    # This is where we would grab the bpm of the music, and then we would use that to create a mix playlist for the user.
    # We're able to generaete like a mixed playlist or even compare if they're compaitable 
    
    # We're using soundchart APi for this endeavor
    headers = {
    'x-app-id':  SOUNDCHARTS_APP_ID,
    'x-api-key': SOUNDCHARTS_API_KEY,
    }
    url = f"https://customer.api.soundcharts.com/api/v2/song/search/{music_name}"
    
    
    params = {
    'offset': '0',
    'limit': '10',
    }
    response = requests.get(url, headers=headers, params=params)
    data = response.json()
    if not data.get('items'):
        return None
    song_id = data['items'][0]['uuid']
    return song_id



# Connect Spotify API, like we have with 
@login_required
def spotify_connect(request):
    link_generator  = SpotifyOAuth(
        client_id=SPOTIFY_API,
        client_secret=SPOTIFY_SECRET_KEY,
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="user-read-email playlist-read-private user-top-read",
    )
    return redirect(link_generator.get_authorize_url())


@login_required
def spotify_callback_to_views(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "No code provided"}, status=400)

    response = requests.post(
        os.getenv("SPOTIFY_TOKEN_URL"),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": os.getenv("SPOTIFY_REDIRECT_URI"),
            "client_id": SPOTIFY_API,
            "client_secret": SPOTIFY_SECRET_KEY,
        },
    )

    data = response.json()
    print("SPOTIFY RESPONSE:", data) 

    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")

    if not access_token:
        return JsonResponse(data, status=400)


    request.session["spotify_access_token"] = access_token
    request.session["spotify_refresh_token"] = refresh_token

    return redirect("home")  



def billboard_top_100(request):
    # Billboard API endpoint for the top 100 songs
    url = "https://billboard-api2.p.rapidapi.com/hot-100"

    headers = {
        "X-RapidAPI-Key": os.getenv("BILLBOARD_API_KEY"),
        "X-RapidAPI-Host": "billboard-api2.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return JsonResponse(data)
    else:
        return JsonResponse({"error": "Failed to fetch data from Billboard API"}, status=response.status_code)
