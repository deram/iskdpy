from multiprocessing.pool import ThreadPool

import isk_network_source

from isk_source import Source
from isk_types import *
parent=Source.factory('NetworkSource')

register=Source.register
@register('BackgroundNetworkSource')
class BackgroundNetworkSource(parent):
	def __init__(self, config):
		super(BackgroundNetworkSource, self).__init__(config)
		self.pool=ThreadPool()

	#def get_display():

	def update_display(self):
		ret=super(BackgroundNetworkSource, self).update_display()
		if ret:
			self.__get_slides()
		return ret

	#def update_slide(self, slide):

	#def connect(self):

	#def slide_done(self, slide):

	#def get_path(self):
	
	def __get_slides(self):
		def worker(slide):
			self.update_slide(slide)
		self.pool.map_async(worker, self.display.get_all_slides().values())
