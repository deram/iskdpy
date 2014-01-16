import logging
logger = logging.getLogger(__name__)

import glob

from ..source import Source, thread
from .. import types
import os

register=Source.register

@register('LocalSource')
class LocalSource(Source):
	def __init__(self, config):
		super(LocalSource, self).__init__()
		self.local_dir=config['local_dir']
		self.display_name=config['display_name']
		self.files=""
		if not os.path.exists(self.local_dir):
			os.makedirs(self.local_dir)


	#def get_display():

	@thread.decorate
	def update_display(self):
		files=glob.glob('%s/*.*' % self.local_dir)
		if ( self.files != files ):
			logger.info("Contents of '%s' changed, rebuilding display..." % (self.local_dir))
			self.files=files
			slides=[]
			groups=[]
			for item in files:
				if item.endswith(('avi', 'mp4', 'mov', 'mkv')):
					slidetype='video'
				else:
					slidetype='image'
				slide=types.Slide({'id':item,'type':slidetype, 'filename':item.replace('\\','/'), 'position':len(slides)+1, 'updated_at':1})
				slide.set_attrib('foo', item)
				slides.append(slide)
			groups.append(types.Group(slides=slides))
			presentation=types.Presentation(groups=groups, attribs={'total_slides':len(slides)})
			self.display=types.Display(presentation=presentation)
			return True
		return False

	@thread.decorate
	def update_slide(self, slide):
		return slide

	@thread.decorate
	def connect(self):
		return True

	@thread.decorate
	def slide_done(self, slide):
		return True


if __name__ == "__main__":
	#from pprint import pprint
	source=Source.factory('LocalSource')()
	source.connect()
	source.update_display()
	print "%s" % source.display
