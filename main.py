from cocos.director import director
from cocos.scenes.transitions import *
from graphics import SlideScene
from pprint import pprint
from slideshow import CurrentSlideshow
from config import *

if __name__ == "__main__":
    director.init(**window_config)
    if ( scale_down ):
        director.window.set_size(640, 360)
#    director.window.set_fullscreen(True)

    director.run(SlideScene() )

