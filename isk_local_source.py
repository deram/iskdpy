import config
import file
import glob

from isk_source import Source
from isk_types import *

register=Source.register

@register('LocalSource')
class LocalSource(Source):
	def __init__(self, local_dir="local", display_name=config.display_name):
		super(LocalSource, self).__init__()
		self.local_dir=local_dir
		self.display_name=display_name
		self.files=""

	#def get_display():

	def update_display(self):
		files=glob.glob('%s/*.*' % self.local_dir)
		if ( self.files != files ):
			slides=[]
			groups=[]
			for item in files:
				slides.append(Slide({'filename':item, 'position':len(slides)+1}))
			groups.append(Group(slides=slides))
			presentation=Presentation(groups=groups, attribs={'total_slides':len(slides)})
			self.display=Display(presentation=presentation)
		return True

	def update_slide(self, slide):
		return slide

	def connect(self):
		return True

	def slide_done(self, slide):
		return True


if __name__ == "__main__":
	from pprint import pprint
	source=Source.factory('LocalSource')()
	source.connect()
	source.update_display()
	print "%s" % source.display
