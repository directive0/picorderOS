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
    warble = scansound.play()
    click = clicksound.play()

    click.stop()
    warble.stop()

    while not configure.status[0] == "quit":
        if configure.audio[0]:

            if configure.dr_opening[0]:
                click = clicksound.play()
                configure.dr_opening[0] = False

            if configure.dr_open[0]:
                if not warble.is_playing():
                    warble = scansound.play()
            else:
                if warble.is_playing():
                    warble.stop()
