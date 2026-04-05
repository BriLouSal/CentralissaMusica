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
def search_engine(query: str):
    query = query.strip().upper()
    cache_key = f"deezer:{query}"

    cached = cache.get(cache_key)
    if cached:
        return cached

    if not query:
        return []

    res = requests.get(
        "https://api.deezer.com/search",
        params={"q": query}
    )

    results = res.json().get("data", [])

    data = []
    # Limit to 10 results for performance reasons

    for item in results[:10]:
        data.append({
            "name": item["title"],
            "artist": item["artist"]["name"],
            "album": item["album"]["title"],
            "type": "track",
            "id": item["id"],
            "url": item["link"],
            "image": item["album"]["cover_medium"],
            "rank": item.get("rank", 0),
        })

    if not data:
        return []
    # We should also sort via the most listened music
    
    items = sorted(data, key=lambda x: x.get("rank", 0), reverse=True)
    
    cache.set(cache_key, items, timeout=60 * 60 * 60 *24 * 7)  # Cache for 7 days
    return items



async def music_search_view(request, query):
    result = await search_engine(query)
    return JsonResponse({"results": result})



def music_exists_view(request, song_name) -> bool:
    # Check if the song exists in our database or via API
    # For simplicity, we'll just check via the search engine
    results = async_to_sync(search_engine)(song_name)
    exists = any(song for song in results if song["name"].lower() == song_name.lower())
    if exists:
        return True
    return False
