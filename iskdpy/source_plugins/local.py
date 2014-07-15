import logging
logger = logging.getLogger(__name__)

import glob

from ..source import SourcePlugin
from .. import types
import os

@SourcePlugin.register()
class LocalSource(SourcePlugin):
	def __init__(self, config):
		super(LocalSource, self).__init__()
		self.local_dir=config['local_dir']
		self.display_name=config['display_name']
		self.files=""
		if not os.path.exists(self.local_dir):
			os.makedirs(self.local_dir)


	#def get_display():

	def update_display(self):
		files=glob.glob('%s/*.*' % self.local_dir)
		if ( self.files != files ):
			logger.info("Contents of '%s' changed, rebuilding display...", (self.local_dir))
			self.files=files
			slides=[]
			for item in files:
				if item.endswith(('avi', 'mp4', 'mov', 'mkv')):
					slidetype='video'
				else:
					slidetype='image'
				slide=types.Slide(id=item, type=slidetype, filename=item.replace('\\', '/'))
				print slide
				slides.append(slide)
			presentation=types.Presentation(slides=slides, total_slides=len(slides))
			self.display=types.Display(presentation=presentation)
			print self.display
			return True
		return False

	def update_slide(self, slide):
		return slide

	def connect(self):
		return True

	def slide_done(self, slide):
		return True


if __name__ == "__main__":
	#from pprint import pprint
	source=SourcePlugin.factory('LocalSource')()
	source.connect()
	source.update_display()
	print "%s" % source.display
