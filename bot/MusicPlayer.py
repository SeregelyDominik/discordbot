import discord
import os
import random
import asyncio
from collections import deque


class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.music_queue = deque()
        self.volume_level = 1.0  # Default volume (100%)
        self.is_shuffling = False

    async def join_channel(self, ctx):
        """Connect the bot to the user's voice channel."""
        if not ctx.author.voice:
            await ctx.send("❌ You're not in a voice channel.")
            return None

        voice_channel = ctx.author.voice.channel
        vc = ctx.voice_client

        if vc and vc.channel != voice_channel:
            await vc.move_to(voice_channel)
        elif not vc:
            vc = await voice_channel.connect()

        return vc

    async def play(self, ctx, filename: str):
        """Play a specific file."""
        vc = ctx.voice_client
        if not vc:
            await ctx.send("❌ I'm not in a voice channel. Use `!join` first.")
            return

        filepath = f"music/{filename}"
        if not os.path.isfile(filepath):
            await ctx.send("❌ File not found.")
            return

        vc.stop()  # Stop current audio if playing

        source = discord.FFmpegPCMAudio(filepath, executable="ffmpeg")
        audio = discord.PCMVolumeTransformer(source, volume=self.volume_level)

        vc.play(audio)
        await ctx.send(f"🎶 Now playing: `{filename}` at volume `{int(self.volume_level * 100)}%`.")

    async def play_next(self, ctx):
        """Play the next song in the queue."""
        vc = ctx.voice_client
        if not vc:
            return

        if self.music_queue:
            next_file = self.music_queue.popleft()
            source = discord.FFmpegPCMAudio(os.path.join("music", next_file))
            audio = discord.PCMVolumeTransformer(source, volume=self.volume_level)

            def after_playing(error):
                fut = self.play_next(ctx)
                asyncio.run_coroutine_threadsafe(fut, self.bot.loop)

            vc.play(audio, after=after_playing)
            await ctx.send(f"🎵 Now playing: `{next_file}`")
        else:
            await vc.disconnect()
            await ctx.send("✅ Playlist finished.")

    async def shuffle(self, ctx):
        """Shuffle the music queue."""
        music_folder = "music"
        files = [f for f in os.listdir(music_folder) if f.endswith(".mp3")]
        if not files:
            await ctx.send("❌ No MP3 files found in `music/` folder.")
            return

        random.shuffle(files)
        self.music_queue = deque(files)
        self.is_shuffling = True

        await ctx.send(f"🔀 Shuffled and starting playlist with `{len(files)}` tracks.")
        await self.play_next(ctx)

    async def pause(self, ctx):
        """Pause the music."""
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send("⏸️ Paused.")
        else:
            await ctx.send("❌ Nothing is playing.")

    async def resume(self, ctx):
        """Resume paused music."""
        vc = ctx.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send("▶️ Resumed.")
        else:
            await ctx.send("❌ Nothing is paused.")

    async def stop(self, ctx):
        """Stop the music and disconnect."""
        vc = ctx.voice_client
        if vc:
            vc.stop()
            await vc.disconnect()
            await ctx.send("🛑 Stopped playback and left the channel.")
        else:
            await ctx.send("❌ I'm not connected to a voice channel.")

    async def skip(self, ctx):
        """Skip the current song."""
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.stop()  # Triggers the after_playing function to play the next track
            await ctx.send("⏭️ Skipped.")
        else:
            await ctx.send("❌ Nothing is playing.")

    async def set_volume(self, ctx, level: int):
        """Set the volume."""
        if level < 0 or level > 100:
            await ctx.send("❌ Volume must be between 0 and 100.")
            return

        self.volume_level = level / 100.0
        vc = ctx.voice_client

        if vc and vc.source and isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source.volume = self.volume_level

        await ctx.send(f"🔊 Volume set to `{level}%`.")

