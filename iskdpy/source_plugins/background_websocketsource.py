import logging
logger = logging.getLogger(__name__)

from multiprocessing.pool import ThreadPool

from . import websocketsource
from ..source import SourcePlugin

@SourcePlugin.register()
class BackgroundWebsocketSource(websocketsource.WebsocketSource):
	def __init__(self, config):
		super(BackgroundWebsocketSource, self).__init__(config)
		self.pool=ThreadPool(1)
	#def get_display():
	#def update_display():
	
	def _display_data_cb(self, data):
		ret=super(BackgroundWebsocketSource, self)._display_data_cb(data)
		if ret:
			logger.debug('get_slides')
			self.__get_slides()
		return ret

	#def update_slide(self, slide):

	#def connect(self):

	#def slide_done(self, slide):

	#def get_path(self):
	
	def __get_slides(self):
		def worker(slide):
			if slide.ready:
				self.update_slide(slide)
		#self.pool.map_async(worker, self.display.get_all_slides().values())
		for i in self.display.all_slides.values():
			worker(i)
