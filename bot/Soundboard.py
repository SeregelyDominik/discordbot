import discord
import os
from discord.ui import Button, View

class SoundboardView(View):
    def __init__(self, sound_files, vc_getter):
        super().__init__(timeout=None)
        self.sound_files = sound_files
        self.vc_getter = vc_getter
        for label, filename in sound_files.items():
            self.add_item(SoundButton(label=label, file=filename, vc_getter=self.vc_getter))

class SoundButton(Button):
    def __init__(self, label, file, vc_getter):
        super().__init__(label=label, style=discord.ButtonStyle.primary)
        self.file = file
        self.vc_getter = vc_getter

    async def callback(self, interaction: discord.Interaction):
        vc = self.vc_getter(interaction.guild)
        if not vc or not vc.is_connected():
            await interaction.response.send_message("❌ Not connected to a voice channel.", ephemeral=True)
            return

        if vc.is_playing():
            vc.stop()

        filepath = os.path.join("sounds", self.file)
        vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=filepath))
        await interaction.response.send_message(f"🔊 Playing: {self.file}", ephemeral=True)

class Soundboard:
    def __init__(self, bot, sound_dir="sounds"):
        self.bot = bot
        self.sound_dir = sound_dir
        self.sound_files = self._load_sound_files()

    def _load_sound_files(self):
        files = {}
        for file in os.listdir(self.sound_dir):
            if file.endswith(".mp3"):
                name = os.path.splitext(file)[0].capitalize()
                files[name] = file
        return files

    def get_voice_client(self, guild):
        return guild.voice_client

    async def join_voice_channel(self, ctx):
        if ctx.author.voice:
            return await ctx.author.voice.channel.connect()
        return None

    async def send_soundboard(self, ctx):
        vc = ctx.guild.voice_client
        if not vc:
            vc = await self.join_voice_channel(ctx)
        if not vc:
            await ctx.send("❌ You're not in a voice channel.")
            return

        view = SoundboardView(self.sound_files, self.get_voice_client)
        await ctx.send("🎛️ Choose a sound to play:", view=view)

    async def leave(self, ctx):
        vc = ctx.voice_client
        if vc:
            await vc.disconnect()
            await ctx.send("👋 Disconnected from voice.")
        else:
            await ctx.send("❌ I'm not connected to a voice channel.")
