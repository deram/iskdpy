import json
from pprint import pprint

class Slideshow():
    current=None
    def __init__(self, show=""):
        self.playlist_number=0
        self.slide_number=-1
        json_data=open("test.json").read()
        self.data = json.loads(json_data)
        #pprint(self.data)

    def get_playlists(self):
        return self.data['slideshow']['playlists']

    def get_playlist(self,num):
        return self.get_playlists()[num]

    def get_playlist_slides(self, num):
        return self.get_playlist(num)['slides']

    def get_slide(self, playlist, slide):
        return self.get_playlist_slides(playlist)[slide]

    def get_next(self):
        slideshowlen=len(self.get_playlists())
        playlistlen=len(self.get_playlist(self.playlist_number))
        self.slide_number += 1
        if ( self.slide_number == playlistlen ):
            self.slide_number = 0
            self.playlist_number += 1
        if ( self.playlist_number == slideshowlen ):
            self.slide_number = 0
            self.playlist_number = 0
        return self.get_slide(self.playlist_number, self.slide_number)['file'].encode('utf8')

def CurrentSlideshow():
    Slideshow.current
    if (not Slideshow.current):
        Slideshow.current = Slideshow()
    return Slideshow.current

