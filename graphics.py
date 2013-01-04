from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
#from cocos.scenes.transitions import *
from isk_transitions import *
from cocos.actions import *
from cocos.sprite import Sprite
import pyglet
from pyglet import gl, font
from datetime import datetime
from time import strftime

from pyglet.window import key

from isk_presenter import CurrentPresenter
    
class ControlLayer(Layer):

    is_event_handler = True     #: enable pyglet's events

    def __init__( self, clock=True ):
        super(ControlLayer, self).__init__()
        self.scheduled_event=False
        self.push_all_handlers()
        self.clock=clock
        now=datetime.now()
        self.text_title = pyglet.text.Label(now.strftime("%H:%M:%S") ,
            color=(0,0,0,255),
            font_size=40,
            font_name="Franklin Gothic Heavy",
            bold=True,
            x=1280-35,
            y=130,
            anchor_x=font.Text.RIGHT,
            anchor_y=font.Text.TOP )

    def draw( self ):
        if (self.clock):
			self.text_title.draw()

    def on_key_press( self, k , m ):
        if k == key.ENTER:
            self.do(CallFunc(self.parent.change_slide))
            return True

    def on_enter(self):
	if (not self.scheduled_event):
            self.scheduled_event = True
            if (self.clock):
                self.schedule(self.change_time)
        return super(ControlLayer, self).on_enter()

    def change_time(self, dt=0):
        now=datetime.now()
        self.text_title.begin_update()
        self.text_title.text=now.strftime("%H:%M:%S")
        self.text_title.end_update()



class SlideLayer(Layer):
    def __init__( self, file):
        super( SlideLayer, self ).__init__()
        g = Sprite( file, anchor=(0,0) )
        self.add( g )

class VideoLayer (Layer):
    def __init__(self, video_name):
        super(VideoLayer, self).__init__()

        source = pyglet.media.load(video_name)
        format = source.video_format
        if not format:
            print 'No video track in this source.'
            return

        self.media_player = pyglet.media.Player()
        self.media_player.queue(source)
        self.media_player.play()

    def draw(self):
        self.media_player.get_texture().blit(0, 0)



class SlideScene(Scene):
    def __init__(self, filename="", type=""):
        super(SlideScene, self).__init__()
        self.scheduled_event=False
        if (not filename):
       	    slide=CurrentPresenter().get_next()
            self.filename=slide.get_cachefile()
            self.duration=slide.get_duration()
            self.clock=slide.get_clock()
        else:
            self.filename=filename
            self.duration=100
            self.clock=True
            
        self.add(ColorLayer(255,255,255,255), z=-10)

	if (type=="Video"):
            self.add(VideoLayer(self.filename), z=0)
	else:
            self.add(SlideLayer(self.filename), z=0)

        self.add(ControlLayer(self.clock), z=10)

    def on_enter(self):
	if (not self.scheduled_event):
            self.scheduled_event = True
            self.schedule_interval(self.change_slide, self.duration)
        return super(SlideScene, self).on_enter()

    def change_slide(self, dt=0):
        transition=FadeBLTransition #FadeTransition
        director.replace(transition(SlideScene(), 1.25))


