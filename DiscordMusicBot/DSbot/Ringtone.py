from pydub import AudioSegment


class RingtoneMaker:

    def make_ringtone(self, inputfile, outputfile, start=0, end=30):
        """Mp3 fájl megvágása"""

        # mp3 betöltése
        audio = AudioSegment.from_mp3(inputfile)
        seconds = len(audio)//1000  # hossz masodpercben

        # kis hibakezelés
        if start < 0 or end < 0 or start > end or end > seconds:
            raise ValueError

        # idők
        start_time = start * 1000
        end_time = end * 1000

        # vágás
        cut_audio = audio[start_time:end_time]

        # mentés
        cut_audio.export(outputfile, format="mp3")
