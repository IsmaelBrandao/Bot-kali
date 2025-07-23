# File: utils/embed_utils.py
import discord
import yaml
import os

# Carrega as configurações do arquivo config/settings.yaml
settings_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "settings.yaml")
with open(settings_path, "r", encoding="utf8") as config_file:
    SETTINGS = yaml.safe_load(config_file)

# Define os emojis padrão para cada plataforma (caso não sejam sobrescritos no YAML)
PLATFORM_EMOJIS = {
    "spotify": "<:SpotifyLogo:1369287765300219967>",
    "youtube": "<:youtubelogo:1369702623002886214>"
}

def format_time_value(time_val):
    """
    Se time_val é um inteiro (segundos), converte para o formato H:MM:SS ou MM:SS.
    Caso contrário, retorna o valor inalterado.
    """
    if isinstance(time_val, int):
        m, s = divmod(time_val, 60)
        if m >= 60:
            h, m = divmod(m, 60)
            return f"{h}:{m:02}:{s:02}"
        else:
            return f"{m:02}:{s:02}"
    return time_val

def create_now_playing_embed(song: dict, requester: str, requester_avatar: str = None) -> discord.Embed:
    """
    Cria um embed para exibir a faixa que está tocando.
    
    Estrutura:
      - Título fixo na barra superior: "<emoji> Tocando Agora" (o emoji é definido conforme a plataforma).
      - A descrição contém o título da faixa (em negrito e como link, se houver URL).
      - Se disponível, é exibida a thumbnail da faixa.
      - Footer: "Solicitado por {requester}" com o avatar (se fornecido).
    """
    url = song.get("url", "")
    # Detecta a plataforma: se o URL contiver "spotify.com", força a plataforma para "spotify".
    platform = song.get("platform", "unknown").lower()
    if "spotify.com" in url.lower():
        platform = "spotify"
    
    emoji = SETTINGS.get("platform_icons", {}).get(platform, PLATFORM_EMOJIS.get(platform, ""))
    embed_title = f"{emoji} Tocando Agora"
    song_title = song.get("title", "Título desconhecido")
    description = f"[**{song_title}**]({url})" if url else f"**{song_title}**"
    
    embed = discord.Embed(title=embed_title, description=description, color=discord.Color.green())
    if song.get("thumbnail"):
        embed.set_thumbnail(url=song["thumbnail"])
    
    if requester_avatar:
        embed.set_footer(text=f"Solicitado por {requester}", icon_url=requester_avatar)
    else:
        embed.set_footer(text=f"Solicitado por {requester}")
    
    return embed

def create_queue_added_embed(song: dict, estimated_time, track_length: str,
                               position: int, requester: str, requester_avatar: str = None) -> discord.Embed:
    """
    Cria um embed organizado para exibir que uma nova música foi adicionada à fila.
    
    Estrutura:
      - Título: Exibe o emoji da plataforma seguido de "Música Adicionada à Fila".
      - Descrição: Exibe o título da música (como link clicável, se houver URL).
      - Campo sem título contendo, em linhas separadas:
            • **Duração:** {track_length}
            • **Tempo Estimado:** {estimated_time} (em MM:SS ou H:MM:SS)
            • **Upcoming:** {upcoming} música(s) - número de músicas que faltam até essa posição (position - 1)
            • **Posição:** {position}
      - Se disponível, é exibida a thumbnail da faixa.
      - Footer: "Solicitado por {requester}" com o avatar (se fornecido).
    """
    url = song.get("url", "")
    platform = song.get("platform", "unknown").lower()
    if "spotify.com" in url.lower():
        platform = "spotify"
    
    emoji = SETTINGS.get("platform_icons", {}).get(platform, PLATFORM_EMOJIS.get(platform, ""))
    title = f"{emoji} Música Adicionada à Fila"
    song_title = song.get("title", "Título desconhecido")
    description = f"[**{song_title}**]({url})" if url else f"**{song_title}**"
    
    embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
    
    # Converte o tempo estimado se for numérico (em segundos)
    estimated_time_formatted = format_time_value(estimated_time)
    # Calcula o número de músicas que faltam até essa posição (assumindo que position é baseado em 1)
    upcoming = position - 1
    
    detalhes = (
        f"**Duração:** {track_length}\n"
        f"**Tempo Estimado:** {estimated_time_formatted}\n"
        f"**Upcoming:** {upcoming} música(s)\n"
        f"**Posição:** {position}"
    )
    # Adiciona um campo sem título (usando zero-width space)
    embed.add_field(name="\u200b", value=detalhes, inline=False)
    
    if song.get("thumbnail"):
        embed.set_thumbnail(url=song["thumbnail"])
    
    if requester_avatar:
        embed.set_footer(text=f"Solicitado por {requester}", icon_url=requester_avatar)
    else:
        embed.set_footer(text=f"Solicitado por {requester}")
    
    return embed

def create_queue_list_embed(queue: list, requester: str) -> discord.Embed:
    """
    Cria um embed para exibir a fila de faixas.
    
    Para cada faixa, exibe:
      - O emoji da plataforma.
      - O título da faixa (em negrito e como link clicável, se houver URL).
      - A duração da faixa.
    """
    embed = discord.Embed(title="🎼 **Fila de Músicas**",
                          description="Lista das próximas faixas na fila:",
                          color=discord.Color.purple())
    
    for idx, song in enumerate(queue, start=1):
        url = song.get("url", "")
        platform = song.get("platform", "unknown").lower()
        if "spotify.com" in url.lower():
            platform = "spotify"
        emoji = SETTINGS.get("platform_icons", {}).get(platform, PLATFORM_EMOJIS.get(platform, ""))
        song_title = song.get("title", "Título desconhecido")
        embed.add_field(name=f"{emoji} {idx}. [**{song_title}**]({url})",
                        value=f"Duração: {song.get('duration', '0:00')}",
                        inline=False)
    
    embed.set_footer(text=f"Solicitado por {requester}")
    return embed

# Alias para compatibilidade caso seu código utilize o nome 'create_song_embed'
create_song_embed = create_now_playing_embed