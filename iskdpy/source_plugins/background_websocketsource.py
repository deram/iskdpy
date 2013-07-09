from multiprocessing.pool import ThreadPool

from . import websocketsource

from ..source import Source
from ..types import *
parent=Source.factory('WebsocketSource')

register=Source.register
@register('BackgroundWebsocketSource')
class BackgroundWebsocketSource(parent):
	def __init__(self, config):
		super(BackgroundWebsocketSource, self).__init__(config)
		self.pool=ThreadPool()
	#def get_display():
	#def update_display():

	def display_data_cb(self, data):
		ret=super(BackgroundWebsocketSource, self).display_data_cb(data)
		if ret:
			print 'get_slides'
			self.__get_slides()
		return ret

	#def update_slide(self, slide):

	#def connect(self):

	#def slide_done(self, slide):

	#def get_path(self):
	
	def __get_slides(self):
		def worker(slide):
			if slide.is_ready():
				self.update_slide(slide)
		self.pool.map_async(worker, self.display.get_all_slides().values())
