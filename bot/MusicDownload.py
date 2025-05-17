import os
import yt_dlp


class MusicDownload:
    def download_audio(self, url, folder_name=None):
        """Mp3 fájl letöltése YT-ról"""
        # mappa-check
        if folder_name:

            folder_path = os.path.join('music', folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)  # mappa létrehozása, ha nem létezett
        else:
            # default érték
            folder_path = 'music'

        mp3_path_holder = {}

        # segédfüggvény fájl útvonal követéshez
        def hook(d):
            if d['status'] == 'finished':
                # webm helyett mp3
                base, _ = os.path.splitext(d['filename'])
                mp3_path_holder['path'] = base + '.mp3'

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(folder_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return mp3_path_holder.get('path')
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None

    def download_video(self, url):
        """Mp4 fájl letöltése Yt-ról"""
        if not os.path.exists('videos'):
            os.makedirs('videos')

        mp4_path_holder = {}

        def hook(d):
            if d['status'] == 'finished':
                base, _ = os.path.splitext(d['filename'])
                mp4_path_holder['path'] = base + '.mp4'

        # Force MP4 format by specifying 'mp4' in the format option
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': 'videos/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'progress_hooks': [hook],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return mp4_path_holder.get('path')
        except Exception as e:
            print(f"Error downloading video: {e}")
            return None
