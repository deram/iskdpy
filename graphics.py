from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.scenes.transitions import *
from cocos.actions import *
from cocos.sprite import Sprite
import pyglet
from pyglet import gl, font

from pyglet.window import key

from slideshow import CurrentSlideshow 
    
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
            filename=CurrentSlideshow().get_next()
        self.add(ColorLayer(50,30,0,255), z=-10)
        self.add(SlideLayer(filename), z=0)
        self.add(ControlLayer(), z=10)

    def on_enter(self):
	if (not self.scheduled_event):
            print "foo"
            self.scheduled_event = True
            self.schedule_interval(self.change_slide, 10)
        return super(SlideScene, self).on_enter()

#    def on_exit(self):
#        print self.scheduled_event
#        if (self.scheduled_event):
#            print "bar"
#            self.unschedule(self.change_slide)
#            self.scheduled_event=False


    def change_slide(self, dt=0):
        transition=FadeBLTransition #FadeTransition
        director.replace(transition(SlideScene(), 1.25))


