"""
Discord Bot
Python programozás
2025.tavasz
Seregély Dominik
"""
import datetime
import asyncio
import os
import discord
import yt_dlp
from discord.ext import commands
from dotenv import load_dotenv
from Soundboard import Soundboard
from MusicDownload import MusicDownload
from Ringtone import RingtoneMaker
from Top10 import Top10
from MusicPlayer import MusicPlayer


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    """Ready függvény"""
    print(f'Bejelentkezve, mint {bot.user}!')


@bot.event
async def on_message(message):
    """Üzenet figyelő"""
    if not bot.user or message.author == bot.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello!')

    await bot.process_commands(message)


@bot.command()
async def download(ctx):
    """Zene letöltése funkció"""
    await ctx.send("Milyen formátumban? `mp3` vagy `mp4`?")

    def check(m):
        return (m.author == ctx.author and
                m.channel == ctx.channel and
                m.content.lower() in ['mp3', 'mp4'])

    try:
        msg = await bot.wait_for(
            'message', check=check, timeout=30)
        format_choice = msg.content.lower()
        await ctx.send(f"`{format_choice} formátum kiválasztva!`."
                       f" Most már küldheted a Youtube linket!")

        def link_check(m):
            return (m.author == ctx.author
                    and m.channel == ctx.channel
                    and "youtube.com" in m.content)

        link_msg = await bot.wait_for(
            'message', check=link_check, timeout=60)
        youtube_url = link_msg.content

        await ctx.send("Letöltés elkezdve!")

        try:
            md = MusicDownload()
            if format_choice == "mp3":
                file_path = md.download_audio(youtube_url)
            else:
                file_path = md.download_video(youtube_url)

            if file_path:
                await ctx.send(f"Letöltés befejezve!: {file_path}")
            else:
                await ctx.send("Valami probléma történt a letöltés során.")

        except yt_dlp.DownloadError as e:
            await ctx.send(f"Error: {e}")

    except asyncio.TimeoutError:
        await ctx.send("Túl sokáig tartott válaszolnod."
                       " Próbáld újra `!download` paranccsal.")


@bot.command()
async def top10(ctx):
    """Top 10 zene letöltése txt fájlba"""

    def check(m):
        return (m.author == ctx.author
                and m.channel == ctx.channel
                and m.content.lower() in ['igen', 'nem'])

    t = Top10()
    try:

        t.get_top_10_songs()

        await ctx.send("Top 10 zene sikeresen lekérve!")
        await ctx.send("Leakarod tölteni őket? Igen/Nem")
        msg = await bot.wait_for('message', check=check, timeout=30)
        answer = msg.content.lower()
        if answer == "igen":
            md = MusicDownload()
            date = datetime.datetime.today().strftime('%Y-%m-%d')
            with open("top_10_songs.txt.", "r", encoding="UTF-8") as f:
                for line in f:
                    line = line.split(",")
                    if len(line) == 3:
                        song_link = line[2]
                        md.download_audio(song_link, date)
            await ctx.send("Zenék sikeresen letöltve!")

    except yt_dlp.DownloadError as e:
        await ctx.send(f"Hiba történt: {e}")


@bot.command()
async def ringtone(ctx):
    """Zene vágás"""
    await ctx.send("Kérlek tölts fel egy mp3 fájlt vagy"
                   " írd be egy már létező mp3 fájlt nevét"
                   " a /music mappában pl.`zene.mp3`")

    def file_or_text_check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for(
            'message', check=file_or_text_check, timeout=60)

        # mp3 fájl neve stringként
        if msg.content and msg.content.lower().endswith('.mp3'):
            filename = msg.content.strip()
            input_path = os.path.join('music', filename)

            if not os.path.exists(input_path):
                await ctx.send(f"A(z) `{filename}` "
                               f"nem találtam a /music mappában")
                return

        # mp3 fájl feltöltve
        elif msg.attachments and msg.attachments[0].filename.endswith('.mp3'):
            attachment = msg.attachments[0]
            filename = attachment.filename
            input_path = os.path.join('music', filename)

            if not os.path.exists("music"):
                os.makedirs("music")

            await attachment.save(input_path)
            await ctx.send(f"A(z) `{filename}` sikeresen feltöltve és mentve.")

        else:
            await ctx.send("Rossz input, kérlek próbáld újra!")
            return

        await ctx.send("Most írd be a levágás kezdetének és "
                       "végének idejét másodpercben, pl így: `30 60`")

        def time_check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        time_msg = await bot.wait_for('message', check=time_check, timeout=30)
        try:
            start_sec, end_sec = map(int, time_msg.content.strip().split())
        except ValueError:
            await ctx.send("Nem jó formátum. "
                           "Kérlek így írd be az időket: `30 60`.")
            return

        output_filename = f"cut_{filename}"
        output_path = os.path.join("music", "ringtones", output_filename)

        ring = RingtoneMaker()
        ring.make_ringtone(input_path, output_path, start_sec, end_sec)

        await ctx.send(f"Itt van a levágott videó {start_sec} másodperctől"
                       f" {end_sec} másodpercig:",
                       file=discord.File(output_path))

    except asyncio.TimeoutError:
        await ctx.send("Túl sokáig vártál. Kérlek "
                       "próbáld úrja !ringtone paranccsal.")
    except FileNotFoundError as e:
        await ctx.send(f"Error: {e}")

# MusicPlayer funkció
music_player = MusicPlayer(bot)


@bot.command()
async def join(ctx):
    """Bot csatlakoztatása a hangcsatornába"""
    await music_player.join_channel(ctx)


@bot.command()
async def play(ctx, filename: str):
    """Zeneszám lejátszása"""
    await music_player.play(ctx, filename)


@bot.command()
async def pause(ctx):
    """Zene lejátszásának megállítása"""
    await music_player.pause(ctx)


@bot.command()
async def resume(ctx):
    """Zene lejátszásának folytatása"""
    await music_player.resume(ctx)


@bot.command()
async def stop(ctx):
    """Zene lejátszás megállítása és kilépés a hangcsatornából"""
    await music_player.stop(ctx)


@bot.command()
async def skip(ctx):
    """Zene kihagyása"""
    await music_player.skip(ctx)


@bot.command()
async def shuffle(ctx, folder: str = "music"):
    """Lejátszási lista keverése"""
    await music_player.shuffle(ctx, folder)


@bot.command()
async def playlist(ctx, folder: str = "music"):
    """Lejátszási lista elindítása"""
    await music_player.playlist(ctx, folder)


@bot.command()
async def volume(ctx, level: int):
    """Hangerő beállítás"""
    await music_player.set_volume(ctx, level)

soundboard = Soundboard(bot)


@bot.command()
async def sbjoin(ctx):
    """Soundboard"""
    await soundboard.send_soundboard(ctx)


@bot.command()
async def sbleave(ctx):
    """Kilépés a soundboardból"""
    await soundboard.leave(ctx)


# bot futtatása
bot.run(TOKEN)
