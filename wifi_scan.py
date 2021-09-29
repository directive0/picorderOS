# PicorderOS Wifi Module Proto
print("Loading Wifi Scanner Module")

from wifi import Cell, Scheme



class Wifi_Scan(object):

    def __init__(self):
        pass

    def update():
        this = list(Cell.all('wlan0'))
        return this
