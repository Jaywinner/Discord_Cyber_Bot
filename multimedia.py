"""
Simple multimedia helper for sending short-form videos and optional audio streaming.

Usage:
    from multimedia import create_multimedia_embed
    embed, view = create_multimedia_embed("phishing", user_id)
    await channel.send(embed=embed, view=view)
"""

import logging
import discord
from discord.ui import View, Button
import asyncio
from typing import Tuple, Optional

logger = logging.getLogger("cyberbot.multimedia")

# Curated short-form videos per topic (YouTube short links or direct MP4 URLs)
# These are short educational clips chosen to align with the course topics.
SHORT_VIDEOS = {
    "phishing": [
        {"title": "What is Phishing? (Short Explainer)", "url": "https://www.youtube.com/watch?v=3GBmpqhQI8s"},
        {"title": "Phishing Explained (2 min)", "url": "https://www.youtube.com/watch?v=DwlOso5Wglo"}
    ],
    "social_engineering": [
        {"title": "Social Engineering (Short)", "url": "https://www.youtube.com/watch?v=sWlgT5yirO8"}
    ],
    "passwords": [
        {"title": "Passphrases & Password Tips (Short)", "url": "https://www.youtube.com/watch?v=Vn6CUZWkbgw"}
    ],
    "password_managers": [
        {"title": "Password Managers Explained (Short)", "url": "https://www.youtube.com/shorts/8-RJ6wBICqs"}
    ],
    "2fa": [
        {"title": "What is Two-Factor Authentication (Short)", "url": "https://www.youtube.com/shorts/UdHjTGzE1nI"}
    ],
    "network": [
        {"title": "Network Basics (Short)", "url": "https://www.youtube.com/shorts/hJrPvNfU3FQ"},
        {"title": "Network Fundamentals (Short Explainer)", "url": "https://www.youtube.com/watch?v=2GxYli9T8AM"}
    ],
    "videos": [
        {"title": "Intro to Cybersecurity (Short)", "url": "https://www.youtube.com/watch?v=DwlOso5Wglo"}
    ],
    "audio": [
        {"title": "Security Tip Audio (Short)", "url": "https://www.youtube.com/watch?v=DwlOso5Wglo"}
    ]
}


def _choose_video_for(content_type: str):
    """Pick a short video entry for the content type (chooses first by default)."""
    lst = SHORT_VIDEOS.get(content_type, [])
    if not lst:
        # fallback to a generic short
        return {"title": "Cybersecurity Short", "url": "https://www.youtube.com/watch?v=DwlOso5Wglo"}
    return lst[0]


def create_multimedia_embed(content_type: str, user_id: int) -> Tuple[discord.Embed, Optional[View]]:
    """Returns (embed, view) ready to send.
    The view contains two buttons:
      - Play Video: posts the chosen short video link (Discord will embed it)
      - Play Audio in Voice: attempts to stream audio via yt-dlp+ffmpeg (optional)
    """
    chosen = _choose_video_for(content_type)
    embed = discord.Embed(
        title=f"🎬 {chosen['title']}",
        description=f"Short learning clip about **{content_type}** — quick and fun! Click Play Video to open here or watch inline if your client supports it.",
        color=0x00AAFF
    )
    embed.add_field(name="Length", value="~30-120s (short-form)", inline=True)
    embed.add_field(name="Source", value=chosen["url"], inline=True)
    embed.set_footer(text="Tip: Use headphones for audio clarity. Use Play Audio in Voice to stream audio to a voice channel (if available).")

    view = View(timeout=120)

    async def _play_video_callback(interaction: discord.Interaction):
        try:
            if interaction.user.id != user_id:
                await interaction.response.send_message("This button is for the student who opened the content.", ephemeral=True)
                return

            await interaction.response.send_message(
                f"▶️ Opening short video: **{chosen['title']}**\n{chosen['url']}",
                ephemeral=False
            )
        except Exception:
            logger.exception("Failed to respond to Play Video button")
            try:
                await interaction.response.send_message("❌ Could not open the video. Try the link: " + chosen["url"], ephemeral=True)
            except Exception:
                logger.exception("Also failed to fallback-send video link")

    play_video = Button(label="▶️ Play Video", style=discord.ButtonStyle.primary)
    play_video.callback = _play_video_callback
    view.add_item(play_video)

    async def _play_audio_callback(interaction: discord.Interaction):
        try:
            if interaction.user.id != user_id:
                await interaction.response.send_message("This button is for the student who opened the content.", ephemeral=True)
                return

            voice_state = interaction.user.voice
            if voice_state is None or voice_state.channel is None:
                await interaction.response.send_message("❌ Join a voice channel first and then press this button.", ephemeral=True)
                return

            await interaction.response.send_message("🔊 Connecting to your voice channel and playing audio...", ephemeral=True)
            await _stream_audio_to_voice(interaction, chosen["url"], voice_state.channel)
        except Exception:
            logger.exception("Failed on Play Audio in Voice")
            try:
                await interaction.followup.send("❌ Could not play audio in voice. Ensure bot has permission and ffmpeg/yt-dlp are installed.", ephemeral=True)
            except Exception:
                logger.exception("Failed to send followup after audio failure")

    play_audio = Button(label="🔊 Play Audio in Voice", style=discord.ButtonStyle.secondary)
    play_audio.callback = _play_audio_callback
    view.add_item(play_audio)

    return embed, view


def _stream_audio_to_voice(interaction: discord.Interaction, url: str, voice_channel: discord.VoiceChannel):
    """Streams audio from the given URL into the provided voice channel.
    Requires yt-dlp and ffmpeg installed on host.
    """
    try:
        import yt_dlp as youtube_dl
    except Exception:
        logger.exception("yt_dlp not available; cannot stream audio")
        await interaction.followup.send("❌ Server is missing yt-dlp. Install yt-dlp to enable audio streaming.", ephemeral=True)
        return

    try:
        voice_client = discord.utils.get(interaction.client.voice_clients, guild=voice_channel.guild)
        if voice_client and getattr(voice_client.channel, 'id', None) != voice_channel.id:
            await voice_client.disconnect(force=True)
            voice_client = None

        if not voice_client or not voice_client.is_connected():
            voice_client = await voice_channel.connect()
    except Exception:
        logger.exception("Failed to connect to voice channel")
        await interaction.followup.send("❌ Failed to connect to the voice channel. Check bot permissions.", ephemeral=True)
        return

    ytdl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'skip_download': True
    }

    loop = asyncio.get_event_loop()

    def ytdl_extract():
        with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if 'url' in info:
                return info
            formats = info.get('formats', [])
            if formats:
                for f in formats:
                    if f.get('acodec') and f.get('url'):
                        return f
            return info

    try:
        info = await loop.run_in_executor(None, ytdl_extract)
        stream_url = info.get('url')
        title = info.get('title', 'audio')
    except Exception:
        logger.exception("yt-dlp extraction failed")
        await interaction.followup.send("❌ Could not extract audio stream from the URL.", ephemeral=True)
        return

    ffmpeg_options = {
        'options': '-vn'
    }

    try:
        if voice_client.is_playing():
            voice_client.stop()

        source = discord.FFmpegPCMAudio(stream_url, **ffmpeg_options)
        voice_client.play(source, after=lambda e: logger.info("Finished playing audio: %s", e) if e else None)
        await interaction.followup.send(f"▶️ Now playing audio: **{title}**", ephemeral=False)
    except Exception:
        logger.exception("Failed to play audio via FFmpeg")
        await interaction.followup.send("❌ Playback failed. Ensure ffmpeg is installed and accessible.", ephemeral=True)
