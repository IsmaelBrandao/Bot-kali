# File: utils/music_utils.py
import re
from services.spotify_service import get_spotify_song_info
from services.youtube_service import get_youtube_song_info

async def extract_song_info(query: str) -> dict:
    """
    Verifica se a query é uma URL (Spotify, YouTube, etc.) ou um termo de busca,
    e retorna um dicionário com as informações da música.
    """
    if re.match(r'https?://', query):
        if "spotify" in query.lower():
            return await get_spotify_song_info(query)
        elif "youtube" in query.lower():
            return await get_youtube_song_info(query)
        else:
            # Se a URL não estiver reconhecida, utiliza o YouTube por padrão.
            return await get_youtube_song_info(query)
    else:
        # Trata a query como termo de busca no YouTube.
        return await get_youtube_song_info(query)