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
    query = query.strip()
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
    for item in results[:50]:
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
    
    cache.set(cache_key, items, timeout=60 * 60  *24 * 7)  # Cache for 7 days
    return items[:10]  # Return top 10 results


def search_artist(query: str):
    query = query.strip()
    cache_key = f"deezer_artist:{query}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    res = requests.get(
        "https://api.deezer.com/search/artist",
        params={"q": query}
    )
    
    results = res.json().get("data", [])
    data = []
    for item in results[:50]:  # Limit to top 50 results
        data.append({
            "name": item["name"],
            "id": item["id"],
            "url": item["link"],
            "image": item["picture_medium"],
            "rank": item.get("nb_fan", 0)  # Using number of fans as a rank metric
        })
    if not data:
        return []
    items = sorted(data, key=lambda x: x.get("rank", 0), reverse=True)
    cache.set(cache_key, items, timeout=60 * 60  *24 * 7)  # Cache for 7 days
    return items[:10]  # Return top 10 results
    




async def music_search_view(request, query):
    query_lower = query.lower()

    tracks = await search_engine(query)
    artists = await sync_to_async(search_artist)(query)

    # Tag types
    for t in tracks:
        t["type"] = "track"

    for a in artists:
        a["type"] = "artist"
    # Let's create an algorithimn that determines the best results based on the query and the rank of the music, we can also give more weight to the music that starts with the query, then the music that contains the query, then the music that has any word in the query, and then the rest. We can also give more weight to the music that has a higher rank. We can also give more weight to the music that has a higher rank if it starts with the query. We can also give more weight to the music that has a higher rank if it contains the query. We can also give more weight to the music that has a higher rank if it has any word in the query.

    def score(item):
        name = item["name"].lower()
        if name == query_lower:
            return 1000

        # Starts with query
        if name.startswith(query_lower):
            return 800

        if query_lower in name:
            return 500


        if any(word in name for word in query_lower.split()):
            return 200

        return 0

    combined = tracks + artists 

    combined_sorted = sorted(
        combined,
        key=lambda x: (score(x), x.get("rank", 0)),
        reverse=True
    )

    return JsonResponse({
        "results": combined_sorted[:10]
    })

def music_exists_view(request, song_name) -> bool:
    # Check if the song exists in our database or via API
    # For simplicity, we'll just check via the search engine
    results = async_to_sync(search_engine)(song_name)
    exists = any(song for song in results if song["name"].lower() == song_name.lower())
    if exists:
        return True
    return False


def search_music(request):
    # instead of having a seperate music search for each function, we can just make a function that primarily handles them for better reusability and less code repetition. We can also make it so that the search engine is more dynamic and can be used for other purposes as well, such as searching for artists or albums.
    query = request.GET.get('search', '')
    
    referer = request.META.get('HTTP_REFERER', '/')


    if not query:
        messages.warning(request, "Please enter a search query.")
        return redirect(referer)
        # We also want to also use like search first index
    result_query = async_to_sync(search_engine)(query)
    if not result_query:
        messages.warning(request, "No results found for your query.")
        return render(request, 'base/home.html')
    else:
        search_index =  result_query[0]
        # Check if music exists actually, because
        # we could end up with a situation where the search result has nothing right
        if len(result_query) == 0 or not music_exists_view(request, search_index["name"]):
            messages.warning(request, "No results found for your query.")
            return redirect(referer)
        
        
        # We also need to make a new redirect route, we need to check if we're searching the artist or the music, if artist, then we redirect to the artist page, if music, then we redirect to the music player page. We can also make it so that if the search result is an artist, we show the top 5 songs of that artist in the search results for better user experience.
        if search_index["type"] == "artist":
            return redirect('artist_page', artist_name=search_index["name"])
        else:
            return redirect('music_player', music_name=search_index["name"])
        
