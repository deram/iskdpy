import logging
logger = logging.getLogger(__name__)

import gc
import pyglet

from ..output import OutputPlugin, thread

from .. import config
from .. import presenter
from ..types import Slide

@OutputPlugin.register()
class CocosOutput(OutputPlugin):
	def __init__(self):
		super(CocosOutput, self).__init__()
		self.slide=None

	@thread.decorate
	def run(self):
		logger.info("importing")
		from cocos.director import director
		from .cocos_scene.graphics import SlideScene
		from .cocos_scene.control import RemoteControlLayer

		logger.info("started")
		director.init(**config.window)
		if ( config.scale_down ):
			director.window.set_size(640, 360)
		if ( config.fullscreen ):
			director.window.set_fullscreen(True)
		if ( config.font_files ):
			for font in config.font_files:
				pyglet.resource.add_font(font)
		director.window.set_mouse_visible(False)
		RemoteControlLayer().set_task(self.task)
		self.slide=Slide()
		self.scene=SlideScene(self.slide)
		director.run(self.scene)
		logger.info("ended")
		thread.end()

	@thread.decorate
	def set_slide(self, slide, *args, **kwargs):
		logger.debug("Slide received %s" % slide)
		if slide.get_id() == self.slide.get_id():
			self.scene.set_slide(slide, 'update')
		else:
			self.scene.set_slide(slide)
		self.slide=slide
		gc.collect()
		del gc.garbage[:]

	@thread.decorate
	def refresh_slide_cache(self, slide):
		filename=slide.get_filename()
		if filename in pyglet.resource._default_loader._cached_images:
			pyglet.resource._default_loader._cached_images.pop( filename )
		pyglet.resource.reindex()

	def task(self):
		super(CocosOutput, self).task()

if __name__ == "__main__":
	#from pprint import pprint
	pass
