import logging
logger = logging.getLogger(__name__)

import time

from ..output import OutputPlugin, thread

register=OutputPlugin.register

@register('DummyLog')
class DummyLog(OutputPlugin):
	def __init__(self):
		super(DummyLog, self).__init__()

	def run(self):
		logger.info("started")
		while True:
			self.task()
			time.sleep(0)

	@thread.decorate
	def set_slide(self, slide, *args, **kwargs):
		logger.info("started %s" % slide)
		pass

	#def refresh_slide_cache(self, slide):

	def task(self):
		thread.work_one(block=True)

if __name__ == "__main__":
	#from pprint import pprint
	pass
