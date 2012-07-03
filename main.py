from cocos.director import director
from cocos.scenes.transitions import *
from graphics import SlideScene
from pprint import pprint
from slideshow import CurrentSlideshow

if __name__ == "__main__":
    director.init(height=720, width=1280, resizable=True)
#    director.window.set_fullscreen(True)

    director.run( SlideScene() )

