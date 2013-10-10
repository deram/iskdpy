import logging
logger = logging.getLogger(__name__)

from cocos.director import director
from .scene.graphics import SlideScene

from . import source_plugins
from . import config
from . import presenter

def setup_logger():
	logging.basicConfig(filename='iskdpy.log', 
						level=logging.DEBUG,
						format='%(asctime)s %(name)-32s %(levelname)-8s %(message)s',
						datefmt='%H:%M:%S'
						)
	root=logging.getLogger()

	console = logging.StreamHandler()
	console.setLevel(logging.DEBUG)

	formatter = logging.Formatter('%(name)s: %(levelname)-8s %(message)s')
	console.setFormatter(formatter)

	root.addHandler(console)

def main():
	setup_logger()

	logger.info('Started')
	slide=presenter.get_empty_slide()
	
	director.init(**config.window)
	if ( config.scale_down ):
		director.window.set_size(640, 360)
	if ( config.fullscreen ):
		director.window.set_fullscreen(True)
	director.window.set_mouse_visible(False)

	director.run(SlideScene(slide) )
	logger.info('Stopped')
