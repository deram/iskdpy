from cocos.director import director
from cocos.scenes.transitions import *
from graphics import SlideScene
from pprint import pprint
import isk_types
import config


if __name__ == "__main__":
    import isk_network_source
    import isk_presenter
    isk_presenter.Presenter.current()
    
    director.init(**config.window)
    if ( config.scale_down ):
        director.window.set_size(640, 360)
    if ( config.fullscreen ):
        director.window.set_fullscreen(True)

    slide=isk_types.Slide({'filename': 'base.png', 'duration': 5, 'type': 'image', 'clock':False})

    director.run(SlideScene(slide) )

