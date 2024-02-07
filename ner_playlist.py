import json
import logging
import os
import openai
from typing import Optional
from IPython.display import display, Markdown
from tenacity import retry, wait_random_exponential, stop_after_attempt
from dotenv import dotenv_values
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load variables from .env into a dictionary
env_vars = dotenv_values(".env")

# Set your OpenAI API key
openai.api_key = env_vars.get("KEY")

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

OPENAI_MODEL = 'gpt-4-turbo'
# Initialize Spotipy client

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))
#parse from spotify 
user_country = "TZ"


# Spotify recommendation parameters
parameters = {
    "limit": 20,  # The target size of the list of recommended tracks (default: 20, min: 1, max: 100)
    "market": "",  # An ISO 3166-1 alpha-2 country code for filtering tracks by market
    "seed_artists": "",  # Comma-separated Spotify IDs for seed artists
    "seed_genres": "",  # Comma-separated genres for seed recommendations
    "seed_tracks": "",  # Comma-separated Spotify IDs for seed tracks
}

tunable_parameters = { 
                          # Tunable track attributes:
    "min_acousticness": None,  # Minimum acousticness value (0 - 1)
    "max_acousticness": None,  # Maximum acousticness value (0 - 1)
    "target_acousticness": None,  # Target acousticness value (0 - 1)
    "min_danceability": None,  # Minimum danceability value (0 - 1)
    "max_danceability": None,  # Maximum danceability value (0 - 1)
    "target_danceability": None,  # Target danceability value (0 - 1)
    "min_duration_ms": None,  # Minimum duration of track in milliseconds
    "max_duration_ms": None,  # Maximum duration of track in milliseconds
    "min_energy": None,  # Minimum energy value (0 - 1)
    "max_energy": None,  # Maximum energy value (0 - 1)
    "target_energy": None,  # Target energy value (0 - 1)
    "min_instrumentalness": None,  # Minimum instrumentalness value (0 - 1)
    "max_instrumentalness": None,  # Maximum instrumentalness value (0 - 1)
    "target_instrumentalness": None,  # Target instrumentalness value (0 - 1)
    "min_key": None,  # Minimum key value (0 - 11)
    "max_key": None,  # Maximum key value (0 - 11)
    "target_key": None,  # Target key value (0 - 11)
    "min_liveness": None,  # Minimum liveness value (0 - 1)
    "max_liveness": None,  # Maximum liveness value (0 - 1)
    "target_liveness": None,  # Target liveness value (0 - 1)
    "min_loudness": None,  # Minimum loudness value
    "max_loudness": None,  # Maximum loudness value
    "target_loudness": None,  # Target loudness value
    "min_mode": None,  # Minimum mode value (0 - 1)
    "max_mode": None,  # Maximum mode value (0 - 1)
    "target_mode": None,  # Target mode value (0 - 1)
    "min_popularity": None,  # Minimum popularity value (0 - 100)
    "max_popularity": None,  # Maximum popularity value (0 - 100)
    "target_popularity": None,  # Target popularity value (0 - 100)
    "min_speechiness": None,  # Minimum speechiness value (0 - 1)
    "max_speechiness": None,  # Maximum speechiness value (0 - 1)
    "target_speechiness": None,  # Target speechiness value (0 - 1)
    "min_tempo": None,  # Minimum tempo value
    "max_tempo": None,  # Maximum tempo value
    "target_tempo": None,  # Target tempo value
    "min_time_signature": None,  # Minimum time signature value
    "max_time_signature": None,  # Maximum time signature value
    "target_time_signature": None,  # Target time signature value
    "min_valence": None,  # Minimum valence value (0 - 1)
    "max_valence": None,  # Maximum valence value (0 - 1)
    "target_valence": None,  # Target valence value (0 - 1)
}



def system_message(labels):
    return f"""
You are an expert in Natural Language Processing. Your task is to identify common Named Entities (NER) in a given text.
The possible common Named Entities (NER) types are exclusively: ({", ".join(labels)})."""

def assisstant_message():
    return f"""
EXAMPLE:
    Text: 'I want an upbeat groovy playlist for my Afro-beats themed party, my friends want to hear some burna boy, Asake & lots of Amapiano vibes. I want 15 songs max, make sure to include mnike and ojuelegba'
    '
    {{
    "market": "{user_country}",  # An ISO 3166-1 alpha-2 country code for filtering tracks by market
    "seed_artists": "Wizkid, Burna Boy, Asake",  # Comma-separated Spotify IDs for seed artists
    "seed_genres": "Afro-beats, Amapiano",  # Comma-separated genres for seed recommendations
    "seed_tracks": "mnike, ojuolegba",  # Comma-separated Spotify IDs for seed tracks
    }}
--"""

def user_message(text):
    return f"""
TASK:
    Text: {text}
"""
        
# Function to get Spotify track ID from track name
def get_spotify_track_ids(seed_tracks):
    track_ids = []

    # Iterate over each track name in the array
    for track_name in seed_tracks:
        # Search for the track
        results = sp.search(q=track_name, limit=1, type='track')

        # Check if any tracks were found
        if results['tracks']['items']:
            # Extract the Spotify ID of the first track found
            spotify_id = results['tracks']['items'][0]['uri']
            track_ids.append(spotify_id)
        else:
            # If no tracks were found, append None to the list
            track_ids.append(None)
    
    return track_ids



