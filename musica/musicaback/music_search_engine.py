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
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from asgiref.sync import sync_to_async, async_to_sync



import requests

load_dotenv()



SPOTIFY_API = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_SECRET_KEY = os.getenv('SPOTIFY_SECRET_KEY')

# https://spotipy.readthedocs.io/en/2.26.0/ Reference

@sync_to_async
def spotifty_search_engine(data: str) -> dict:
    # Grab the data for this from the request -> data -> spotify_searc_engine, and since we have spotify
    # connected, we can use the spotify api to search for songs, artists, albums, and playlists, and we don't need to seperate it unlike KentroCherma, as we can just get the data for itself
    
    # Generate a cache key
    data = data.upper()
    cache_key = f"autocomplete:{data}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    
    if not data:
        return JsonResponse({"error": "No query provided"}, status=400)
    
    spotify_url = "https://api.spotify.com/v1/search"
    
    # USE my spotify client, and secret to be able to search for songs, artists, albums, and playlists, and we can just return the data for it, and we can use the spotify api to search for songs, artists, albums, and playlists, and we don't need to seperate it unlike KentroCherma, as we can just get the data for itself
    
    search = spotipy.Spotify.search(spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIFY_API, client_secret=SPOTIFY_SECRET_KEY, redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"))), q=data, type="track,artist,album,playlist", limit=5)
    
    data = []
    for item in search["tracks"]["items"]:
        data.append({
            "name": item["name"],
            "artist": item["artists"][0]["name"],
            "album": item["album"]["name"],
            "image": item["album"]["images"][0]["url"],
            "spotify_url": item["external_urls"]["spotify"],
            "type": "track"
        })
    for item in search["artists"]["items"]:
        data.append({
            "name": item["name"],
            "image": item["images"][0]["url"] if item["images"] else None,
            "spotify_url": item["external_urls"]["spotify"],
            "type": "artist"
        })
    for item in search["albums"]["items"]:
        data.append({
            "name": item["name"],
            "artist": item["artists"][0]["name"],
            "image": item["images"][0]["url"],
            "spotify_url": item["external_urls"]["spotify"],
            "type": "album"
        })
    for item in search["playlists"]["items"]:
        data.append({
            "name": item["name"],
            "owner": item["owner"]["display_name"],
            "image": item["images"][0]["url"] if item["images"] else None,
            "spotify_url": item["external_urls"]["spotify"],
            "type": "playlist"
        })
    return JsonResponse({"results": data})