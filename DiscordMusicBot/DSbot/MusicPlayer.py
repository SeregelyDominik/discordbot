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
        self.current_folder = "music"

    async def join_channel(self, ctx):
        """bot beléptetése csatornába"""

        if not ctx.author.voice:
            await ctx.send("Nem vagy belépve hangcsatornába discordon.")
            return None

        voice_channel = ctx.author.voice.channel
        vc = ctx.voice_client

        if vc and vc.channel != voice_channel:
            await vc.move_to(voice_channel)
        elif not vc:
            vc = await voice_channel.connect()

        return vc

    async def play(self, ctx, filename: str):
        """egyetlen szám lejátszása"""
        vc = ctx.voice_client
        if not vc:
            await ctx.send("Nem vagyok belépve hangcsatornába"
                           " discordon. Használd a !join parancsot!")
            return

        filepath = f"music/{filename}"
        if not os.path.isfile(filepath):
            await ctx.send("Nem találtam a zenét.")
            return

        vc.stop()  # megállítja az audiot ha van

        # audio elindítása
        source = discord.FFmpegPCMAudio(filepath, executable="ffmpeg")
        audio = discord.PCMVolumeTransformer(source, volume=self.volume_level)

        vc.play(audio)
        await ctx.send(f"Most a `{filename}`-t játszom"
                       f" `{int(self.volume_level * 100)}% hangerőn`.")

    async def play_next(self, ctx):
        """következő szám letjátszása"""
        vc = ctx.voice_client
        if not vc:
            return

        if self.music_queue:
            next_file = self.music_queue.popleft()
            source = discord.FFmpegPCMAudio(os.path.join(self.current_folder, next_file))
            audio = discord.PCMVolumeTransformer(source,
                                                 volume=self.volume_level)

            def after_playing(error):
                fut = self.play_next(ctx)
                asyncio.run_coroutine_threadsafe(fut, self.bot.loop)

            vc.play(audio, after=after_playing)
            await ctx.send(f"Most játszom: `{next_file}`-t")
        else:
            await vc.disconnect()
            await ctx.send("Lejátszási lista végére értünk.")

    async def shuffle(self, ctx, folder="music"):
        """Tetszőleges mappából beolvassa az mp3
         fájlokat és random sorrendben lejátszza őket"""
        self.current_folder = folder
        files = [f for f in os.listdir(self.current_folder) if f.endswith(".mp3")]
        if not files:
            await ctx.send("Nincsenek mp3 fájlok a music mappában")
            return

        random.shuffle(files)
        self.music_queue = deque(files)
        self.is_shuffling = True

        await ctx.send(f"Megkevertem és elkezdtem"
                       f" lejátszani a lejátszásilistát"
                       f" `{len(files)}` számmal.")
        await self.play_next(ctx)

    async def playlist(self, ctx, folder="music"):
        """Tetszőleges mappából beolvassa az mp3 fájlokat és lejátszza őket"""
        self.current_folder = folder
        files = [f for f in os.listdir(self.current_folder) if f.endswith(".mp3")]
        if not files:
            await ctx.send("Nincsenek mp3 fájlok a music mappában")
            return

        self.music_queue = deque(files)
        self.is_shuffling = True

        await ctx.send(f"Elkezdtem lejátszani"
                       f" a lejátszási listát `{len(files)}` számmal.")
        await self.play_next(ctx)

    async def pause(self, ctx):
        """Zene megállítása"""
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await ctx.send("Zene megállítva.")
        else:
            await ctx.send("Nem játszódott éppen semmi")

    async def resume(self, ctx):
        """Zene folytatása"""
        vc = ctx.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await ctx.send("Zene folytatva.")
        else:
            await ctx.send("Nem volt zene megállítva")

    async def stop(self, ctx):
        """Zene megállítása és kilépés a hangcsatornából"""
        vc = ctx.voice_client
        if vc:
            vc.stop()
            await vc.disconnect()
            await ctx.send("Megállítottam a zenét és kiléptem.")
        else:
            await ctx.send("Nem voltam hangcsatornában.")

    async def skip(self, ctx):
        """Zeneszám kihagyása a lejátszásból"""
        vc = ctx.voice_client
        if vc and vc.is_playing():
            vc.stop()
            await ctx.send("Zeneszám kihagyva.")
        else:
            await ctx.send("Éppen nem szólt semmi.")

    async def set_volume(self, ctx, level: int):
        """Hangerő beállítása"""
        if level < 0 or level > 100:
            await ctx.send("A hangerőnek 0 és 100 között kell lennie")
            return

        self.volume_level = level / 100.0
        vc = ctx.voice_client

        if (vc and vc.source and isinstance(vc.source,
                                            discord.PCMVolumeTransformer)):
            vc.source.volume = self.volume_level

        await ctx.send(f"Hangerő `{level}%-ra állítva`.")
