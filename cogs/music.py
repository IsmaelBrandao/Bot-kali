# File: cogs/music.py

import discord
from discord.ext import commands
from discord import app_commands
from utils.music_utils import extract_song_info
from utils.embed_utils import create_song_embed, create_queue_added_embed, create_queue_list_embed, format_time_value
from services.youtube_service import get_youtube_song_info
import asyncio
import datetime
from discord.ui import View, Button

ITEMS_PER_PAGE = 5

class QueuePaginator(View):
    def __init__(self, queue: list[dict], start_time: datetime.datetime | None):
        super().__init__(timeout=120)
        self.queue = queue
        self.start_time = start_time
        self.currently_playing = queue[0] if queue else None
        self.page = 0

        self.prev_button = Button(label="< Anterior", style=discord.ButtonStyle.primary)
        self.next_button = Button(label="Próximo >", style=discord.ButtonStyle.primary)
        self.prev_button.callback = self.on_prev
        self.next_button.callback = self.on_next
        self.add_item(self.prev_button)
        self.add_item(self.next_button)
        self.update_buttons()

    def update_buttons(self):
        total_pages = (len(self.queue) - 1) // ITEMS_PER_PAGE + 1
        self.prev_button.disabled = (self.page == 0)
        self.next_button.disabled = (self.page >= total_pages - 1)

    def build_embed(self, author_name: str, author_icon: str):
        # calcula tempo restante da faixa atual
        remaining_current = 0.0
        if self.currently_playing and self.start_time:
            total_sec = int(self.currently_playing.get("duration", "0").split()[0])
            elapsed = (datetime.datetime.utcnow() - self.start_time).total_seconds()
            remaining_current = max(total_sec - elapsed, 0.0)

        def fmt(sec: float) -> str:
            m, s = divmod(int(sec), 60)
            if m >= 60:
                h, m = divmod(m, 60)
                return f"{h:02}:{m:02}:{s:02}"
            return f"{m:02}:{s:02}"

        embed = discord.Embed(
            title="🎶 Fila de Músicas",
            description=f"Página {self.page+1}/{(len(self.queue)-1)//ITEMS_PER_PAGE+1}",
            color=discord.Color.blue()
        )

        cumulative = remaining_current
        start = self.page * ITEMS_PER_PAGE
        end = start + ITEMS_PER_PAGE

        for idx, song in enumerate(self.queue[start:end], start=start+1):
            try:
                dur_sec = int(song.get("duration", "0").split()[0])
            except:
                dur_sec = 0
            embed.add_field(
                name=f"{idx}. {song.get('title', 'Desconhecido')}",
                value=(
                    f"Plataforma: {song.get('platform', 'N/A')}\n"
                    f"Duração: {fmt(dur_sec)}\n"
                    f"Estimado: {fmt(cumulative)}"
                ),
                inline=False
            )
            cumulative += dur_sec

        embed.set_footer(text=f"Solicitado por {author_name}", icon_url=author_icon)
        return embed

    async def on_prev(self, interaction: discord.Interaction):
        self.page = max(self.page - 1, 0)
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.build_embed(interaction.user.name, interaction.user.display_avatar.url),
            view=self
        )

    async def on_next(self, interaction: discord.Interaction):
        total_pages = (len(self.queue) - 1) // ITEMS_PER_PAGE + 1
        self.page = min(self.page + 1, total_pages - 1)
        self.update_buttons()
        await interaction.response.edit_message(
            embed=self.build_embed(interaction.user.name, interaction.user.display_avatar.url),
            view=self
        )


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue: list[dict] = []
        self.loop_mode = False
        self.currently_playing = None
        self.start_time: datetime.datetime | None = None

    async def ensure_voice(self, interaction: discord.Interaction) -> discord.VoiceClient:
        if interaction.guild is None:
            await interaction.response.send_message("Este comando só pode ser usado em servidores.", ephemeral=True)
            return None

        member = interaction.guild.get_member(interaction.user.id)
        if member is None:
            await interaction.response.send_message("Não foi possível identificar você no servidor.", ephemeral=True)
            return None

        if not member.voice or not member.voice.channel:
            await interaction.response.send_message("Você precisa estar conectado a um canal de voz para usar este comando.", ephemeral=True)
            return None

        channel = member.voice.channel
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            try:
                voice_client = await channel.connect()
                print(f"[DEBUG] Conectado ao canal de voz: {channel.name}")
            except Exception as e:
                await interaction.response.send_message(f"Erro ao conectar ao canal de voz: {e}", ephemeral=True)
                print(f"[DEBUG] Erro ao conectar: {e}")
                return None
        elif voice_client.channel != channel:
            try:
                await voice_client.move_to(channel)
                print(f"[DEBUG] Bot movido para o canal: {channel.name}")
            except Exception as e:
                await interaction.response.send_message(f"Erro ao mover para o seu canal de voz: {e}", ephemeral=True)
                print(f"[DEBUG] Erro ao mover: {e}")
                return None

        return voice_client

    async def _play_song(self, voice_client: discord.VoiceClient):
        if not self.queue:
            print("[DEBUG] A fila está vazia. Nada para tocar.")
            return

        current_song = self.queue[0]
        self.currently_playing = current_song

        if "audio_url" not in current_song or not current_song["audio_url"]:
            print("[DEBUG] URL de áudio não encontrada na música:", current_song)
            return

        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        try:
            source = discord.FFmpegPCMAudio(current_song["audio_url"], **ffmpeg_options)
        except Exception as e:
            print("[DEBUG] Erro ao criar a fonte de áudio:", e)
            return

        self.start_time = datetime.datetime.utcnow()

        def after_play(error):
            if error:
                print("[DEBUG] Erro durante a reprodução:", error)
            self.bot.loop.create_task(self._after_song(voice_client))

        try:
            voice_client.play(source, after=after_play)
            print(f"[DEBUG] Reproduzindo: {current_song['title']}")
        except Exception as e:
            print("[DEBUG] Erro ao iniciar a reprodução:", e)

    async def _after_song(self, voice_client: discord.VoiceClient):
        if not self.loop_mode:
            if self.queue:
                self.queue.pop(0)

        if self.queue:
            await self._play_song(voice_client)
        else:
            await asyncio.sleep(1)
            self.currently_playing = None
            self.start_time = None
            print("[DEBUG] Fim da fila. Nada mais a reproduzir.")

    @app_commands.command(name="join", description="Faz o bot entrar no canal de voz do usuário")
    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice and interaction.user.voice.channel:
            channel = interaction.user.voice.channel
            voice_client = interaction.guild.voice_client
            if voice_client:
                try:
                    await voice_client.move_to(channel)
                except Exception as e:
                    await interaction.response.send_message(f"Erro ao mover para o canal: {e}", ephemeral=True)
                    return
            else:
                try:
                    await channel.connect()
                except Exception as e:
                    await interaction.response.send_message(f"Erro ao conectar ao canal: {e}", ephemeral=True)
                    return
            await interaction.response.send_message(f"Conectado ao canal: {channel.name}", ephemeral=True)
        else:
            await interaction.response.send_message("Você não está em um canal de voz.", ephemeral=True)

    @app_commands.command(name="leave", description="Faz o bot sair do canal de voz")
    async def leave(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client:
            try:
                await voice_client.disconnect()
                await interaction.response.send_message("Desconectado do canal de voz.", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Erro ao desconectar: {e}", ephemeral=True)
        else:
            await interaction.response.send_message("Não estou conectado a um canal de voz.", ephemeral=True)

    @app_commands.command(name="play", description="Toca uma música a partir de um link ou termo de busca")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        song = await extract_song_info(query)

        if song["platform"].lower() == "spotify":
            if " - " in song["title"]:
                track_name, artist = song["title"].split(" - ", 1)
                search_query = f"{track_name} {artist} audio"
            else:
                search_query = song["title"] + " audio"
            song = await get_youtube_song_info(search_query)
            if "open.spotify.com" in query.lower():
                song["platform"] = "spotify"

        self.queue.append(song)
        requester = interaction.user.name
        avatar = interaction.user.display_avatar.url
        voice_client = await self.ensure_voice(interaction)
        if voice_client is None:
            return

        if not voice_client.is_playing() and self.currently_playing is None:
            embed = create_song_embed(song, requester, avatar)
            await self._play_song(voice_client)
        else:
            position = len(self.queue)
            def convert_duration(ds: str) -> int:
                try:
                    if "sec" in ds:
                        return int(ds.split()[0])
                    parts = [int(p) for p in ds.split(":")]
                    if len(parts) == 2:
                        return parts[0]*60 + parts[1]
                    if len(parts) == 3:
                        return parts[0]*3600 + parts[1]*60 + parts[2]
                    return int(ds)
                except:
                    return 0

            cum = sum(convert_duration(s.get("duration","0:00")) for s in self.queue[:-1])
            embed = create_queue_added_embed(
                song,
                format_time_value(cum),
                format_time_value(convert_duration(song.get("duration","0:00"))),
                position,
                requester,
                avatar
            )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="skip", description="Pula a música atual")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await interaction.response.send_message("Música pulada.", ephemeral=True)
        else:
            await interaction.response.send_message("Nada tocando.", ephemeral=True)

    @app_commands.command(name="stop", description="Para a reprodução e limpa a fila")
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            vc.stop()
        self.queue.clear()
        self.currently_playing = None
        self.start_time = None
        await interaction.response.send_message("Fila limpa e reprodução parada.", ephemeral=True)

    @app_commands.command(name="resume", description="Retoma a reprodução (não implementado para FFmpeg)")
    async def resume(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and not vc.is_playing() and self.currently_playing:
            await interaction.response.send_message("Resume não disponível.", ephemeral=True)
        else:
            await interaction.response.send_message("Nada para retomar.", ephemeral=True)

    @app_commands.command(name="loop", description="Ativa ou desativa o loop da música atual")
    async def loop(self, interaction: discord.Interaction, mode: str):
        if mode.lower() == "on":
            self.loop_mode = True
            await interaction.response.send_message("Loop ativado.", ephemeral=True)
        elif mode.lower() == "off":
            self.loop_mode = False
            await interaction.response.send_message("Loop desativado.", ephemeral=True)
        else:
            await interaction.response.send_message("Use 'on' ou 'off'.", ephemeral=True)

    @app_commands.command(name="queue", description="Exibe a fila de músicas com paginação")
    async def queue_command(self, interaction: discord.Interaction):
        if not self.queue:
            await interaction.response.send_message("A fila está vazia.", ephemeral=True)
            return

        paginator = QueuePaginator(self.queue.copy(), self.start_time)
        embed = paginator.build_embed(interaction.user.name, interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed, view=paginator)

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))