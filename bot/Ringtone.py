from pydub import AudioSegment

class RingtoneException(Exception):
    pass

class RingtoneMaker:

    def make_ringtone(self, inputfile, outputfile, start=0, end=30):
        # Load the MP3 file
        audio = AudioSegment.from_mp3(inputfile)
        seconds = len(audio)//1000 #hossz masodpercben
        if (seconds-start) < end:
            raise RingtoneException()

        # Define start and end time in milliseconds
        start_time = start * 1000
        end_time =  end * 1000

        # Cut the audio segment
        cut_audio = audio[start_time:end_time]
        # Export the cut audio
        cut_audio.export(outputfile, format="mp3")

#ringtone = RingtoneMaker()
#ringtone.make_ringtone("input.mp3", 191, 1)
