from objects import *
import simpleaudio as sa


scansound = sa.WaveObject.from_wave_file("assets/scanning.wav")
clicksound = sa.WaveObject.from_wave_file("assets/clicking.wav")


sounds = [scansound, clicksound]
# the audio object will serve as the primary mechanism by which all sounds
# are loaded and deployed.



def threaded_audio():
    timed = timer()
    start = True
    was_open = False
    warble = sa.play_buffer(scansound, 2, 2, 44100)

    while not configure.status[0] == "quit":
        if configure.audio[0]:

            if configure.dr_open[0]:
                if not warble.is_playing():
                    warble = sa.play_buffer(scansound, 2, 2, 44100)
            else:
                if warble.is_playing():
                    warble.stop()
