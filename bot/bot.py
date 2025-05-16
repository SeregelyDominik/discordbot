# bot.py
import asyncio
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import datetime
from Soundboard import Soundboard
from pydub import AudioSegment
from collections import deque
from discord import PCMVolumeTransformer

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
    print(f'Bejelentkezve, mint {bot.user}!')


@bot.event
async def on_message(message):
    if not bot.user or message.author == bot.user:
        return

    if message.content.startswith('hello'):
        await message.channel.send('Hello!')

    await bot.process_commands(message)


@bot.command()
async def download(ctx):
    await ctx.send("Milyen formátumban? `mp3` vagy `mp4`?")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['mp3', 'mp4']

    try:
        msg = await bot.wait_for('message', check=check, timeout=30)
        format_choice = msg.content.lower()
        await ctx.send(f"`{format_choice} formátum kiválasztva!`. Most már küldheted a Youtube linket!")

        def link_check(m):
            return m.author == ctx.author and m.channel == ctx.channel and "youtube.com" in m.content

        link_msg = await bot.wait_for('message', check=link_check, timeout=60)
        youtube_url = link_msg.content

        await ctx.send(f"Letöltés elkezdése innen:\n{youtube_url}")

        try:
            md = MusicDownload()
            if format_choice == "mp3":
                file_path = md.download_audio(youtube_url)
            else:
                file_path = md.download_video(youtube_url)

            if file_path:
                await ctx.send(f"Letöltés befejezve: {file_path}")
            else:
                await ctx.send("Valami probléma történt a letöltés során.")

        except Exception as e:
            await ctx.send(f"Error: {e}")

    except asyncio.TimeoutError:
        await ctx.send("Túl sokáig tartott válaszolnod. Próbáld újra `!download` paranccsal.")

@bot.command()
async def top10(ctx):

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['igen', 'nem']

    t = Top10()
    try:

        t.get_top_10_songs()

        await ctx.send("Top 10 zene sikeresen lekérve!")
        await ctx.send("Leakarod tölteni őket? Igen/Nem")
        msg = await bot.wait_for('message', check=check, timeout=30)
        answer = msg.content.lower()
        if answer == "i":
            md = MusicDownload()
            date = datetime.datetime.today().strftime('%Y-%m-%d')
            with open("top_10_songs.txt.", "r") as f:
                for line in f:
                    line = line.split(",")
                    if len(line) == 3:
                        song_link = line[2]
                        md.download_audio(song_link, date)
            await ctx.send("Zenék sikeresen letöltve!")


    except Exception as e:
        await ctx.send(f"Hiba történt: {e}")


@bot.command()
async def ringtone(ctx):
    await ctx.send("Please **upload an MP3 file** or type the **name of an existing `.mp3` file** in the `music/` folder (e.g., `song.mp3`).")

    def file_or_text_check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    try:
        msg = await bot.wait_for('message', check=file_or_text_check, timeout=60)

        # Case 1: MP3 filename string
        if msg.content and msg.content.lower().endswith('.mp3'):
            filename = msg.content.strip()
            input_path = os.path.join('music', filename)

            if not os.path.exists(input_path):
                await ctx.send(f"❌ File `{filename}` not found in the `music/` folder.")
                return

        # Case 2: Uploaded MP3 file
        elif msg.attachments and msg.attachments[0].filename.endswith('.mp3'):
            attachment = msg.attachments[0]
            filename = attachment.filename
            input_path = os.path.join('music', filename)

            if not os.path.exists("music"):
                os.makedirs("music")

            await attachment.save(input_path)
            await ctx.send(f"✅ File `{filename}` uploaded and saved.")

        else:
            await ctx.send("❌ Invalid input. Please upload a `.mp3` file or provide the name of an existing `.mp3` in `music/`.")
            return

        # Ask for start and end time
        await ctx.send("Now enter the **start and end time in seconds**, like this: `30 60`")

        def time_check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        time_msg = await bot.wait_for('message', check=time_check, timeout=30)
        try:
            start_sec, end_sec = map(int, time_msg.content.strip().split())
        except ValueError:
            await ctx.send("❌ Invalid time format. Please enter two numbers like `30 60`.")
            return

        output_filename = f"cut_{filename}"
        output_path = os.path.join("music", "ringtones", output_filename)

        # Cut the MP3
        ring = RingtoneMaker()
        ring.make_ringtone(input_path, output_path, start_sec, end_sec)

        await ctx.send(f"🎧 Here's your cut MP3 from {start_sec}s to {end_sec}s:", file=discord.File(output_path))

    except asyncio.TimeoutError:
        await ctx.send("⏳ You took too long. Please try `!cutmp3` again.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")

# Create an instance of MusicPlayer
music_player = MusicPlayer(bot)

@bot.command()
async def join(ctx):
    """Join the user's voice channel."""
    await music_player.join_channel(ctx)

@bot.command()
async def play(ctx, filename: str):
    """Play a specific song from the music folder."""
    await music_player.play(ctx, filename)

@bot.command()
async def pause(ctx):
    """Pause the current song."""
    await music_player.pause(ctx)

@bot.command()
async def resume(ctx):
    """Resume the paused song."""
    await music_player.resume(ctx)

@bot.command()
async def stop(ctx):
    """Stop playback and disconnect from the voice channel."""
    await music_player.stop(ctx)

@bot.command()
async def skip(ctx):
    """Skip the current song."""
    await music_player.skip(ctx)

@bot.command()
async def shuffle(ctx):
    """Shuffle the music queue."""
    await music_player.shuffle(ctx)

@bot.command()
async def volume(ctx, level: int):
    """Set the playback volume (0 to 100)."""
    await music_player.set_volume(ctx, level)



soundboard = Soundboard(bot)

@bot.command()
async def soundboard_cmd(ctx):
    await soundboard.send_soundboard(ctx)

@bot.command()
async def leave(ctx):
    await soundboard.leave(ctx)


# ✅ Just run the bot
bot.run(TOKEN)

