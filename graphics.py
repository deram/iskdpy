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

        self.text_title = pyglet.text.Label("Slideshow testing",
            font_size=32,
            x=5,
            y=director.get_window_size()[1],
            anchor_x=font.Text.LEFT,
            anchor_y=font.Text.TOP )

    def draw( self ):
        self.text_title.draw()

    def on_key_press( self, k , m ):
        transition=FadeTRTransition
        if k == key.ENTER:
            director.replace( transition( SlideScene(CurrentSlideshow().get_next()), 1.25))
            return True


class SlideLayer(Layer):
    def __init__( self, file):
        super( SlideLayer, self ).__init__()
        g = Sprite( file, anchor=(0,0) )
        self.add( g )

class SlideScene(Scene):
    def __init__(self, filename=""):
        super(SlideScene, self).__init__()
        global slideshow
        self.add(ColorLayer(50,30,0,255))
        if (not filename):
            filename=CurrentSlideshow().get_next()
        self.add(SlideLayer(filename))
        self.add(ControlLayer())

