from ..utils import file
import glob

from ..source import Source
from ..types import *

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

	def update_display(self):
		files=glob.glob('%s/*.*' % self.local_dir)
		if ( self.files != files ):
			print "Contents of '%s' changed, rebuilding display..." % (self.local_dir)
			self.files=files
			slides=[]
			groups=[]
			for item in files:
                                if item.endswith(('avi', 'mp4', 'mov', 'mkv')):
                                        type='video'
                                else:
                                        type='image'
                                slide=Slide({'id':item,'type':type, 'filename':item.replace('\\','/'), 'position':len(slides)+1, 'updated_at':1})
                                slide.set_attrib('foo', item)
				slides.append(slide)
			groups.append(Group(slides=slides))
			presentation=Presentation(groups=groups, attribs={'total_slides':len(slides)})
			self.display=Display(presentation=presentation)
			return True
		return False

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
