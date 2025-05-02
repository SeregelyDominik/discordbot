# bot.py
import os
import discord
from dotenv import load_dotenv
import yt_dlp
import bs4
import requests

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class Client(discord.Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def on_ready(self):
        print(f'Logged in as {self.user}!')
        try:
            download_audio('https://www.youtube.com/watch?v=Oa_RSwwpPaA')
        except Exception as e:
            print(f"Download failed: {e}")

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('hello'):
            await message.channel.send('Hello!')


        elif message.content.startswith('!download'):

            url = message.content.split(' ', 1)[1] if ' ' in message.content else None

            if url:

                try:

                    filepath = download_audio(url)

                    if filepath and os.path.exists(filepath):

                        await message.channel.send(

                            "Here's your MP3:",

                            file=discord.File(filepath)

                        )

                    else:

                        await message.channel.send("Download finished but file not found.")

                except Exception as e:

                    await message.channel.send(f"Download failed: {e}")

            else:

                await message.channel.send("Please provide a YouTube URL.")
        elif message.content.startswith('!top'):
            pass


def download_audio(url):
    if not os.path.exists('music'):
        os.makedirs('music')

    mp3_path_holder = {}

    def hook(d):
        if d['status'] == 'finished':
            # yt_dlp gives us a temp file path, we'll replace its extension with .mp3
            base, _ = os.path.splitext(d['filename'])
            mp3_path_holder['path'] = base + '.mp3'

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'music/%(title)s.%(ext)s',
        'ffmpeg_location': r'C:\Program Files\FFMPEG\ffmpeg-7.1.1-essentials_build\bin',  # Set this if ffmpeg isn't in PATH
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return mp3_path_holder.get('path')

def top():
    URL = r"https://charts.youtube.com/charts/TopSongs/global/weekly"
    resp = requests.get(URL)
    print(resp.text)
    pass










intents = discord.Intents.all()
intents.message_content = True

client = Client(intents=intents)
client.run(TOKEN)

download_audio('https://music.youtube.com/watch?v=RVDCeVG90Rg')