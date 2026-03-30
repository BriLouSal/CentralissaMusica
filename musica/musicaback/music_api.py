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
import spotipy
from spotipy.oauth2 import SpotifyOAuth



import requests

load_dotenv()




SPOTIFY_API = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_SECRET_KEY = os.getenv('SPOTIFY_SECRET_KEY')





# Connect Spotify API, like we have with 
@login_required
def spotify_connect(request):
    link_generator  = SpotifyOAuth(
        client_id=SPOTIFY_API,
        client_secret=SPOTIFY_SECRET_KEY,
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="user-read-email playlist-read-private user-top-read",
    )
    return redirect(link_generator.get_authorize_url)


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



def music_db(music: str):
    pass