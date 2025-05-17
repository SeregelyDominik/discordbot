import unittest
import mock
from mock.mock import MagicMock, AsyncMock
import os
import discord

import Ringtone
from Top10 import Top10
from MusicDownload import MusicDownload
from MusicPlayer import MusicPlayer


class TestRingtone(unittest.TestCase):
    @mock.patch('Ringtone.AudioSegment')
    def test_ringtonemaker_hosszabb(self, mock_audiosegment):
        # magicmock
        mock_audio = MagicMock()
        # hossz
        mock_audio.__len__.return_value = 30000  # 30 seconds
        # fájl betöltésének szimulálása
        mock_audiosegment.from_mp3.return_value = mock_audio
        # rossz input check
        with self.assertRaises(ValueError):
            r = Ringtone.RingtoneMaker()
            r.make_ringtone("input.mp3", "output.mp3", 25, 35)

    @mock.patch('Ringtone.AudioSegment')
    def test_ringtonemaker_negativ(self, mock_audiosegment):
        # magicmock
        mock_audio = MagicMock()
        # hossz
        mock_audio.__len__.return_value = 30000  # 30 seconds
        # fájl betöltésének szimulálása
        mock_audiosegment.from_mp3.return_value = mock_audio
        # rossz input check
        with self.assertRaises(ValueError):
            r = Ringtone.RingtoneMaker()
            r.make_ringtone("input.mp3", "output.mp3", -2, -4)

    @mock.patch('Ringtone.AudioSegment')
    def test_ringtonemaker_helyes(self, mock_audiosegment):
        # magicmock
        mock_audio = MagicMock()
        # vágás helyett csak visszadja önmagát
        mock_audio.__getitem__.return_value = mock_audio
        # export elkerülése (hogy ne csináljon feleslegesen mp3 fájlt)
        mock_audio.export = MagicMock()
        # fájl betöltésének szimulálása
        mock_audiosegment.from_mp3.return_value = mock_audio
        # fájl/zene hossza
        mock_audio.__len__.return_value = 60000  # 60 mp millimpben

        instance = Ringtone.RingtoneMaker()
        instance.make_ringtone("input.mp3", "output.mp3", start=10, end=20)

        # meghívódott a helyes fájllal
        mock_audiosegment.from_mp3.assert_called_once_with("input.mp3")
        # jó helyen (időben) vágott
        mock_audio.__getitem__.assert_called_once_with(slice(10000, 20000))
        # jó helyre jó formátumban lett "elmentve"
        mock_audio.export.assert_called_once_with("output.mp3", format="mp3")


class TestTop10Songs(unittest.TestCase):

    @mock.patch("Top10.requests.get")
    def test_get_top_10_songs_writes_file(self, mock_get):
        # Mock html oldal
        main_html = """
        <html><body>
        {}
        </body></html>
        """.format("".join([
            f'<a class="Name_name__1sQZg" '
            f'href="/song{i}"><span>Song {i}</span></a>' for i in range(10)
        ]))
        mock_main_response = MagicMock()
        mock_main_response.text = main_html

        # Mock html zene generator
        def generate_song_html(i):
            return f"""
            <html><body>
                <a aria-label="Google Music"
                href="https://music.youtube.com/watch?v=song{i}"></a>
                <div class="truncate text-lg text-gray-500">
                    <a class="text-tophit-blue dark:opacity-95">Artist {i}</a>
                </div>
            </body></html>
            """

        song_responses = []
        for i in range(10):
            resp = MagicMock()
            resp.text = generate_song_html(i)
            song_responses.append(resp)

        mock_get.side_effect = [mock_main_response] + song_responses

        instance = Top10()
        instance.get_top_10_songs()

        # létrejött a file
        self.assertTrue(os.path.exists("top_10_songs.txt"))

        with open("top_10_songs.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        # 10 sor
        self.assertEqual(len(lines), 10)
        # formátum is megfelelő
        self.assertEqual(lines[0].strip(), "Song 0,"
                                           " Artist 0,"
                                           " https://music."
                                           "youtube.com/watch?v=song0")

        os.remove("top_10_songs.txt")


class TestDownloadAudio(unittest.TestCase):

    url = ("https://www.youtube.com/watch?v="
           "tWoo8i_VkvI&pp=ygUMMzAgc2VjIHRpbWVy0gcJCY0JAYcqIYzv")

    def test_download_audio(self):
        # zene letöltése
        md = MusicDownload()
        md.download_audio(self.url)
        self.assertEqual(os.path.exists(r'music\30 SECOND TIMER.mp3'), True)
        # zene törlése
        os.remove(r'music\30 SECOND TIMER.mp3')


class TestMusicPlayerJoinChannel(unittest.IsolatedAsyncioTestCase):

    async def test_user_not_in_voice_channel(self):
        bot = MagicMock()
        player = MusicPlayer(bot)

        ctx = MagicMock()
        ctx.author.voice = None
        ctx.send = AsyncMock()

        result = await player.join_channel(ctx)

        ctx.send.assert_awaited_once_with(
            "Nem vagy belépve hangcsatornába discordon.")
        self.assertIsNone(result)

    async def test_bot_joins_voice_channel(self):
        bot = MagicMock()
        player = MusicPlayer(bot)

        mock_channel = AsyncMock()
        mock_voice_state = MagicMock(channel=mock_channel)
        ctx = MagicMock()
        ctx.author.voice = mock_voice_state
        ctx.voice_client = None
        mock_channel.connect = AsyncMock(return_value="connected_voice_client")

        result = await player.join_channel(ctx)

        mock_channel.connect.assert_awaited_once()
        self.assertEqual(result, "connected_voice_client")

    async def test_play_success(self):
        # test név
        test_filename = "test_song.mp3"

        # Mock objectek
        bot = MagicMock()
        mock_ctx = AsyncMock()
        mock_vc = MagicMock()
        mock_ctx.voice_client = mock_vc

        # Fgvény hívás
        player = MusicPlayer(bot)
        player.volume_level = 0.5

        with mock.patch('os.path.isfile', return_value=True), \
                mock.patch('discord.FFmpegPCMAudio') as mock_ffmpeg, \
                mock.patch('discord.PCMVolumeTransformer') as mock_vol:

            await player.play(mock_ctx, test_filename)

            # Assertek
            mock_vc.stop.assert_called_once()
            mock_ffmpeg.assert_called_once_with(
                f"music/{test_filename}", executable="ffmpeg")
            mock_vol.assert_called_once()
            mock_vc.play.assert_called_once()
            mock_ctx.send.assert_called_once_with(
                f"Most a `{test_filename}`-t játszom `50% hangerőn`.")

    async def test_pause_valid(self):
        player = MusicPlayer(bot=MagicMock())
        ctx = MagicMock()
        ctx.send = AsyncMock()

        vc = MagicMock()
        vc.is_playing.return_value = True
        ctx.voice_client = vc

        await player.pause(ctx)

        vc.pause.assert_called_once()
        ctx.send.assert_awaited_once_with("Zene megállítva.")

    async def test_resume_valid(self):
        player = MusicPlayer(bot=MagicMock())
        ctx = MagicMock()
        ctx.send = AsyncMock()

        vc = MagicMock()
        vc.is_paused.return_value = True
        ctx.voice_client = vc

        await player.resume(ctx)

        vc.resume.assert_called_once()
        ctx.send.assert_awaited_once_with("Zene folytatva.")

    async def test_skip_valid(self):
        player = MusicPlayer(bot=MagicMock())
        ctx = MagicMock()
        ctx.send = AsyncMock()

        vc = MagicMock()
        vc.is_playing.return_value = True
        ctx.voice_client = vc

        await player.skip(ctx)

        vc.stop.assert_called_once()
        ctx.send.assert_awaited_once_with("Zeneszám kihagyva.")

    async def test_set_volume_valid(self):
        player = MusicPlayer(bot=MagicMock())
        ctx = MagicMock()
        ctx.send = AsyncMock()

        transformer = MagicMock(spec=discord.PCMVolumeTransformer)
        vc = MagicMock()
        vc.source = transformer
        ctx.voice_client = vc

        await player.set_volume(ctx, 75)

        self.assertEqual(player.volume_level, 0.75)
        self.assertEqual(transformer.volume, 0.75)
        ctx.send.assert_awaited_once_with("Hangerő `75%-ra állítva`.")
