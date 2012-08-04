from cocos.director import director
from cocos.scenes.transitions import *
from graphics import SlideScene
from pprint import pprint
import config
import cache

if __name__ == "__main__":
    cache.post_hello(config.display_name)
    director.init(**config.window)
    if ( config.scale_down ):
        director.window.set_size(640, 360)
    if ( config.fullscreen ):
        director.window.set_fullscreen(True)
    director.run(SlideScene() )

