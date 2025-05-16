import os
import yt_dlp

class MusicDownload:
    def download_audio(self, url, folder_name=None):
        if folder_name:
            # Create a subfolder inside 'music/' with the given folder name
            folder_path = os.path.join('music', folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)  # Create the folder if it doesn't exist
        else:
            # Default to 'music/' if no folder name is given
            folder_path = 'music'

        mp3_path_holder = {}

        def hook(d):
            if d['status'] == 'finished':
                # yt_dlp gives us a temp file path, we'll replace its extension with .mp3
                base, _ = os.path.splitext(d['filename'])
                mp3_path_holder['path'] = base + '.mp3'

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(folder_path, '%(title)s.%(ext)s'),
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

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            return mp3_path_holder.get('path')
        except Exception as e:
            print(f"Error downloading audio: {e}")
            return None

    def download_video(self, url):
        if not os.path.exists('videos'):
            os.makedirs('videos')

        mp4_path_holder = {}

        def hook(d):
            if d['status'] == 'finished':
                base, _ = os.path.splitext(d['filename'])
                mp4_path_holder['path'] = base + '.mp4'

        # Force MP4 format by specifying 'mp4' in the format option
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',  # Explicitly prefer MP4 for video and audio
            'outtmpl': 'videos/%(title)s.%(ext)s',
            'ffmpeg_location': r'C:\Program Files\FFMPEG\ffmpeg-7.1.1-essentials_build\bin',
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
