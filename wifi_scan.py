# PicorderOS Wifi Module Proto
print("Loading Wifi Scanner Module")

from wifi import Cell, Scheme



class Wifi_Scan(object):

    def __init__(self):
        pass

    def update():
        ap_list = list(Cell.all('wlan0'))
        return this

    def get_info(self,selection):
        ap_list = self.update()

        if selection <= (len(ap_list)-1):
            return (ap_list[selection].ssid, ap_list[selection].signal, ap_list[selection].wuality, ap_list[selection].frequency, ap_list[selection].bitrates, ap_list[selection].encrypted, ap_list[selection].channel, ap_list[selection].address, ap_list[selection].mode)
