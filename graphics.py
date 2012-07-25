from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.scenes.transitions import *
#from isk_transitions import *
from cocos.actions import *
from cocos.sprite import Sprite
import pyglet
from pyglet import gl, font

from pyglet.window import key

from isk_presenter import CurrentPresenter
    
class ControlLayer(Layer):

    is_event_handler = True     #: enable pyglet's events

    def __init__( self ):
        super(ControlLayer, self).__init__()
        self.push_all_handlers()

        self.text_title = pyglet.text.Label("Slideshow testing",
            font_size=32,
            font_name="Franklin Gothic Heavy",
            x=1280,
            y=director.get_window_size()[1],
            anchor_x=font.Text.RIGHT,
            anchor_y=font.Text.TOP )

    def draw( self ):
        self.text_title.draw()

    def on_key_press( self, k , m ):
        if k == key.ENTER:
            self.do(CallFunc(self.parent.change_slide))
            return True


class SlideLayer(Layer):
    def __init__( self, file):
        super( SlideLayer, self ).__init__()
        g = Sprite( file, anchor=(0,0) )
        self.add( g )

class SlideScene(Scene):
    def __init__(self, filename=""):
        super(SlideScene, self).__init__()
        self.scheduled_event=False
        if (not filename):
       	    self.slide=CurrentPresenter().get_next()
            filename=self.slide.get_cachefile()
        self.add(ColorLayer(50,30,0,255), z=-10)
        self.add(SlideLayer(filename), z=0)
        self.add(ControlLayer(), z=10)

    def on_enter(self):
	if (not self.scheduled_event):
            self.scheduled_event = True
            duration=self.slide.get_duration()
            self.schedule_interval(self.change_slide, duration)
        return super(SlideScene, self).on_enter()

    def change_slide(self, dt=0):
        transition=FadeBLTransition #FadeTransition
        director.replace(transition(SlideScene(), 1.25))
