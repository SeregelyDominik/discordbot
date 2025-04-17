# bot.py
import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

class Client(discord.Client):
    async def on_ready(self):
        print(f'Logged in as {self.user}!')
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith('hello'):
            await message.channel.send('Hello!')



intents = discord.Intents.all()
intents.message_content = True

client = Client(intents=intents)
client.run(TOKEN)