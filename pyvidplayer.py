import pygame 
from pymediainfo import MediaInfo
from ffpyplayer.player import MediaPlayer
from os.path import exists, basename, splitext
from os import strerror
from errno import ENOENT


class Video:
    def __init__(self, path):
        self.path = path
        
        if exists(path):
            self.video = MediaPlayer(path)
            info = self.get_file_data()
            
            self.duration = info["duration"]
            self.frames = 0
            self.frame_delay = 1 / info["frame rate"]
            self.size = info["original size"]
            self.image = pygame.Surface((0, 0))
                        
            self.active = True
        else:
            raise FileNotFoundError(ENOENT, strerror(ENOENT), path)
        
    def get_file_data(self):
        info = MediaInfo.parse(self.path).video_tracks[0]
        return {"path":self.path,
                "name":splitext(basename(self.path))[0],
                "frame rate":float(info.frame_rate),
                "frame count":info.frame_count,
                "duration":info.duration / 1000,
                "original size":(info.width, info.height),
                "original aspect ratio":info.other_display_aspect_ratio[0]}
                
    def get_playback_data(self):
        return {"active":self.active,
                "time":self.video.get_pts(),
                "volume":self.video.get_volume(),
                "paused":self.video.get_pause(),
                "size":self.size}
        
    def restart(self):
        self.video.seek(0, relative=False, accurate=False)
        self.frames = 0
        self.active = True
        
    def close(self):
        self.video.close_player()
        self.active = False
    
    def set_size(self, size):
        self.video.set_size(size[0], size[1])
        self.size = size
    
    def set_volume(self, volume):
        self.video.set_volume(volume)
    
    def seek(self, seek_time, accurate=False):
        vid_time = self.video.get_pts()
        if vid_time + seek_time < self.duration and self.active:
            self.video.seek(seek_time)
            if seek_time < 0:
                while (vid_time + seek_time < self.frames * self.frame_delay):
                    self.frames -= 1
            
    def toggle_pause(self):
        self.video.toggle_pause()
        
    def update(self):
        updated = False
        while self.video.get_pts() > self.frames * self.frame_delay:
            frame, val = self.video.get_frame()
            self.frames += 1
            updated = True
        if updated:
            if val == "eof":
                self.active = False
            elif frame != None:
                self.image = pygame.image.frombuffer(frame[0].to_bytearray()[0], frame[0].get_size(), "RGB")
        return updated
        
    def draw(self, surf, pos, force_draw=True):
        if self.active:
            if self.update() or force_draw:
                surf.blit(self.image, pos)