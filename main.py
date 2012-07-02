#
# cocos2d
# http://cocos2d.org
#
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.scenes.transitions import *
from cocos.actions import *
from cocos.sprite import Sprite
import pyglet
from pyglet import gl, font

from pyglet.window import key

    
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
        global transition, slide_number
        if k == key.ENTER:
            slide_number = (slide_number+1)%len(slides) 
            next = Scene(ColorLayer(50,30,0,255), SlideLayer(slides[slide_number] ), self)
            director.replace( transition( next, 1.25))
            return True


class SlideLayer(Layer):
    def __init__( self, file):
        super( SlideLayer, self ).__init__()

        g = Sprite( file, anchor=(0,0) )
        self.add( g )


if __name__ == "__main__":
    director.init(height=720, width=1280, resizable=True)
#    director.window.set_fullscreen(True)

    transition = FadeTRTransition

    slides=['slide_23_full.jpg', 'slide_28_full.jpg', 'slide_30_full.png']

    slide_number = 0
    g = SlideLayer(slides[slide_number])

    control = ControlLayer()
    controlScene1 = Scene(ColorLayer(30,30,0,0), g, control)
    
    director.run( controlScene1 )

