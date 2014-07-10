import logging
logger = logging.getLogger(__name__)

import gc
import pyglet
from Queue import Queue, Empty

from ..output import OutputPlugin

from .. import config
from ..types import OverrideSlide

@OutputPlugin.register()
class CocosOutput(OutputPlugin):
	def __init__(self):
		super(CocosOutput, self).__init__()
		self.slide=None
		self.scene=None
		self.tasks=Queue()

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
		RemoteControlLayer().set_callback(self.get_callback())
		self.slide=OverrideSlide(**config.empty_slide)
		self.scene=SlideScene(self.slide)
		director.run(self.scene)
		# Destroy window if director exits
		director.window.set_mouse_visible(True)
		director.window.close()
		logger.info("ended")
		#thread.end()
		return True

	def cancel_transition(self):
		if self.scene:
			self.schedule_call(self.scene.cancel_transition)

	def set_slide(self, slide, *args, **kwargs):
		logger.debug("Slide received %s", slide)
		def helper(slide):
			if slide.id == self.slide.id:
				logger.debug("Slides are equal:\n	new	%s\n	old	%s", slide, self.slide)
				self.scene.set_slide(slide, 'update')
			else:
				logger.debug("Slides differ:\n	new	%s\n	old	%s", slide, self.slide)
				self.scene.set_slide(slide)
			self.slide=slide
			gc.collect()
			del gc.garbage[:]
		self.schedule_call(helper, slide)

	def refresh_slide_cache(self, slide):
		def helper(filename):
			if filename in pyglet.resource._default_loader._cached_images:
				pyglet.resource._default_loader._cached_images.pop( filename )
			pyglet.resource.reindex()
		self.schedule_call(helper, slide.filename)

	def task(self):
		#super(CocosOutput, self).task()
		try:
			if not self.tasks.empty():
				(func, args, kwargs)=self.tasks.get(block=False)
				func(*args, **kwargs)
		except Empty:
			pass

	def schedule_call(self, func, *args, **kwargs):
		self.tasks.put((func, args, kwargs))


if __name__ == "__main__":
	#from pprint import pprint
	pass
