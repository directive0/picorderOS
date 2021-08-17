from object import *
import simpleaudio as sa


scansound = sa.WaveObject.from_wave_file("assets/scanning.mp3")
clicksound = sa.WaveObject.from_wave_file("assets/scanning.mp3")


sounds = [scansound, clicksound]
# the audio object will serve as the primary mechanism by which all sounds
# are loaded and deployed.

# sounds are loaded into a lists
# object plays sound n

class Audio(object):
    def __init__(self):
        pass

    def play(self,item):
        sounds[item].play()

    def clock(self):
        pass


def threaded_audio():
    timed = timer()
    start = True

    
