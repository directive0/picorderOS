from object import *
import simpleaudio as sa


scan_sound = sa.WaveObject.from_wave_file("assets/scanning.mp3")

sounds = [scan_sound]
# the audio object will serve as the primary mechanism by which all sounds
# are loaded and deployed.

# sounds are loaded into a lists
# object plays sound n

class Audio(object):
    def __init__(self):
        pass

    def play(self,item):
