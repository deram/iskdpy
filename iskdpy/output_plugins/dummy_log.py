import logging
logger = logging.getLogger(__name__)

import time

from ..output import OutputPlugin

@OutputPlugin.register()
class DummyLog(OutputPlugin):
	def __init__(self):
		super(DummyLog, self).__init__()

	def run(self):
		logger.info("started")
		while True:
			self.task()
			time.sleep(0)

	def set_slide(self, slide, *args, **kwargs):
		logger.info("started %s", slide)

	#def refresh_slide_cache(self, slide):

	#def task(self):

if __name__ == "__main__":
	#from pprint import pprint
	pass
