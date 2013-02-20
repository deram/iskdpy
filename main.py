from cocos.director import director
from cocos.scenes.transitions import *
from graphics import SlideScene
from pprint import pprint
import isk_types
import config
import isk_presenter


if __name__ == "__main__":
    slide=isk_presenter.Presenter.current().get_empty_slide()
    
    director.init(**config.window)
    if ( config.scale_down ):
        director.window.set_size(640, 360)
    if ( config.fullscreen ):
        director.window.set_fullscreen(True)
    director.window.set_mouse_visible(False)

    director.run(SlideScene(slide) )

