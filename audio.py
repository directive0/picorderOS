from objects import *
import simpleaudio as sa
print("Loading Audio Thread")

scansound = sa.WaveObject.from_wave_file("assets/scanning.wav")
clicksound = sa.WaveObject.from_wave_file("assets/clicking.wav")
beepsound = sa.WaveObject.from_wave_file("assets/beep.wav")
alarmsound = sa.WaveObject.from_wave_file("assets/alarm.wav")


sounds = [scansound, clicksound]
# the audio object will serve as the primary mechanism by which all sounds
# are loaded and deployed.



def threaded_audio():
    timed = timer()
    start = True
    was_open = False
    warble = scansound.play()
    click = clicksound.play()
    alarm = alarmsound.play()

    click.stop()
    warble.stop()
    alarm.stop()

    while not configure.status[0] == "quit":
        if configure.audio[0]:

            if configure.dr_opening[0]:
                click = clicksound.play()
                configure.dr_opening[0] = False

            if configure.dr_closing[0]:
                click = clicksound.play()
                configure.dr_closing[0] = False

            if configure.beep_ready[0]:
                beep = beepsound.play()
                configure.beep_ready[0] = False


            # controls the main tricorder sound loop
            if configure.dr_open[0]:
                if not warble.is_playing():
                    warble = scansound.play()
            else:
                if warble.is_playing():
                    warble.stop()

            if configure.alarm_ready[0]:
                if not alarm.is_playing():
                    alarm = alarmsound.play()
                configure.alarm_ready[0] = False
        else:
            warble.stop()
