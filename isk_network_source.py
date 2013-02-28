from auth_http import *
import file
import json
import pyglet.resource

from isk_source import Source
from isk_types import *

register=Source.register

@register('NetworkSource')
class NetworkSource(Source):
	def __init__(self, config):
		super(NetworkSource, self).__init__(config)
		self.server=config['server']
		self.cache_path=config['cache_path']
		self.displayid=None
		self.display_name=config['display_name']
		self.http=AuthHttp(config['user'], config['passwd'])

	#def get_display():

	def update_display(self):
		if (not self.display):
			json_data=self.__get_json(reload=True)
		else:
			json_data=self.__get_json()
		if (json_data):
			data = json.loads(json_data, "utf8")
			if (data):
				self.display=self.__create_display_tree(data)
				#print "DEBUG display:\n%s" % self.display
				return True
		return False

	def update_slide(self, slide):
		if (not slide.is_uptodate()):
			print "Updating: %s" % slide
			if self.__get_slide(slide):
				self.__set_slide_timestamp(slide)
				self.__invalidate_cached_slide(slide)
				pyglet.resource.reindex()
				#print "Got slide and reindexed"
				#print pyglet.resource.get_cached_image_names()
		#else:
		#       set_slide_timestamp(slide) # in case of errors, this might be useful
		return slide

	def connect(self):
		self.displayid=self.__post_hello(self.display_name)
		return (self.displayid>0)

	def slide_done(self, slide):
		if (slide.is_override()):
			return self.__post_override_slide(slide)
		else:
			return self.__post_current_slide(slide)

	def get_path(self):
		return self.cache_path

	def __invalidate_cached_slide(self, slide):
		filename=slide.get_filename()
		if filename in pyglet.resource._default_loader._cached_images:
			pyglet.resource._default_loader._cached_images.pop( filename )

	
	def __create_display_tree(self, data):
		presentation_data=data.pop('presentation')
		groups=[]
		for group in presentation_data.pop('groups', []):
			slides=[]
			for slide in group.pop('slides', []):
				s=Slide(attribs=slide)
				s.set_attrib('filename', '%s/%d.%s' % (self.cache_path, s.get_id(), s.get_suffix()))
				slides.append(s)
			groups.append(Group(slides=slides, attribs=group))
		presentation = Presentation(groups=groups, attribs=presentation_data)
		slides=[]
		for slide in data.pop('override_queue', []):
			s=OverrideSlide(attribs=slide)
			s.set_attrib('filename', '%s/%d.%s' % (self.cache_path, s.get_id(), s.get_suffix()))
			slides.append(s)
		override=OverrideGroup(slides=slides)

		display=Display(presentation=presentation, override=override, attribs=data, name=self.display_name)
		return display

	def __post_hello(self, presenter_name):
		url='%s/displays/hello' % (self.server)
		data={"name": presenter_name}
		return int(self.http.post(url, data))

	def __post_current_slide(self, slide):
		url='%s/displays/%d/current_slide' % (self.server, self.displayid)
		data={"group": slide.get_groupid(), "slide": slide.get_id()}
		self.http.post(url, data)
	
	def __post_override_slide(self, slide):
		url='%s/displays/%d/slide_shown' % (self.server, self.displayid)
		data={"override": slide.get_override_id()}
		self.http.post(url, data)
	
	def __get_json(self, reload=False):
		location='%s/main.json' % self.cache_path
		url='%s/displays/%d?format=json' % (self.server, self.displayid)
		json_data = self.http.get_and_save(url, location)
		if json_data:
			return json_data
		elif reload:
			return file.read(location)
		else:
			return False

	def __get_slide(self, slide):
		location=slide.get_filename()
		id=slide.get_id()
		return self.http.get_and_save('%s/slides/%d/full' % (self.server, id), location)

	def __set_slide_timestamp(self, slide):
		time=slide.get_update_time()
		location=slide.get_filename()
		os.utime(location, (time,time))
	
	def __fill_cache(self):
		slides=self.display.get_all_slides()
		for slide in slides.values():
			self.update_slide(slide)
		return self.display


if __name__ == "__main__":
	from pprint import pprint
	source=Source.factory('NetworkSource')()
	source.connect()
	source.update_display()
	source._NetworkSource__fill_cache()
	print "%s" % source.display
