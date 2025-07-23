# File: services/spotify_service.py
import os
import re
import asyncio
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

_client = None

def get_spotify_client():
    global _client
    if _client is None:
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        if not client_id or not client_secret:
            raise Exception("Credenciais do Spotify não configuradas no .env!")
        auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        _client = spotipy.Spotify(auth_manager=auth_manager)
    return _client

async def get_spotify_song_info(query: str) -> dict:
    """
    Extrai informações reais da faixa a partir de uma URL do Spotify ou de um termo de busca.
    
    Se `query` for uma URL do Spotify, extrai o Track ID (aceitando um segmento opcional como "intl-pt/") e obtém os dados via API.
    Se for apenas um termo de busca, realiza a busca e retorna a primeira ocorrência.
    """
    client = get_spotify_client()
    track_id = None

    # Se a query for uma URL contendo "spotify.com".
    # O regex abaixo permite opcionalmente o segmento "intl-pt/" antes de "track/".
    if "spotify.com" in query:
        pattern = r"spotify\.com/(?:intl-pt/)?track/([a-zA-Z0-9]+)"
        m = re.search(pattern, query)
        if m:
            track_id = m.group(1)
    
    if track_id:
        try:
            track_data = client.track(track_id)
        except Exception as e:
            raise Exception(f"Erro ao obter dados do Spotify: {e}")
    else:
        results = client.search(q=query, type='track', limit=1)
        if results and results['tracks']['items']:
            track_data = results['tracks']['items'][0]
        else:
            raise Exception("Não foi possível encontrar a música no Spotify.")
    
    # Processa os dados obtidos
    artist_names = ", ".join([artist["name"] for artist in track_data["artists"]])
    title = track_data["name"]
    duration_ms = track_data["duration_ms"]
    duration_sec = duration_ms // 1000
    thumbnail = track_data["album"]["images"][0]["url"] if track_data["album"]["images"] else ""

    return {
        "title": f"{title} - {artist_names}",
        "platform": "Spotify",
        "estimated_time": "00:00",  # (Opcional: você pode adicionar lógica para calcular)
        "duration": f"{duration_sec} sec",
        "thumbnail": thumbnail
    }