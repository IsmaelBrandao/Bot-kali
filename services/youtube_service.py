# File: services/youtube_service.py
import asyncio
import yt_dlp

async def get_youtube_song_info(query: str) -> dict:
    """
    Extrai informações de uma música (ou vídeo) a partir do YouTube,
    seja por link ou por termo de busca. Essa função usa yt_dlp e a opção
    'cookiesfrombrowser' para tentar acessar conteúdos com restrição de idade.
    """
    loop = asyncio.get_event_loop()
    ytdl_opts = {
        'quiet': True,
        'format': 'bestaudio',
        'default_search': 'ytsearch',
        'noplaylist': True,
        # Certifique-se de passar uma lista com o navegador desejado, por exemplo:
        'cookiesfrombrowser': ['firefox'],
    }
    with yt_dlp.YoutubeDL(ytdl_opts) as ytdl:
        info = await loop.run_in_executor(None, lambda: ytdl.extract_info(query, download=False))
        # Se for uma busca, pega a primeira entrada da lista
        video = info if 'entries' not in info else info['entries'][0]
        return {
            'title': video.get('title', 'Título desconhecido'),
            'platform': 'YouTube',
            'estimated_time': '00:00',  # se você desejar calcular a estimativa
            'duration': f"{video.get('duration', 0)} sec",
            'thumbnail': video.get('thumbnail', ''),
            'url': video.get('webpage_url', ''),
            'audio_url': video.get('url', '')
        }