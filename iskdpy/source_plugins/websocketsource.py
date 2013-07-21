from ..utils.auth_http import *
from ..utils import file
import json
import pyglet.resource

from ..utils.websocket_rails import WebsocketRails, Event, Channel, NOP
from ..source import Source
from ..types import *

import os

register=Source.register

@register('WebsocketSource')
class WebsocketSource(Source):
	def __init__(self, config):
		super(WebsocketSource, self).__init__(config)
		self.server=config['server']
		self.cache_path=config['cache_path']
		self.displayid=None
		self.display_name=config['display_name']
		self.http=AuthHttp(config['user'], config['passwd'])
		self.socket=WebsocketRails('%s/websocket' % self.server.replace('http', 'ws'))
		self.channel=None
		if not os.path.exists(self.cache_path):
			os.makedirs(self.cache_path)

	#def get_display():

	def update_display(self):
		return True

	def display_data_cb(self, data):
		print 'received display_data'
		if self.__is_display_updated(data):
			self.display=self.__create_display_tree(data)
			return True
		return False

	def goto_slide_cb(self, data):
		print 'received goto_slide'
		if 'slide' in data.keys():
			if data['slide']=='next':
				self.control.goto_next_slide()
			elif data['slide']=='previous':
				self.control.goto_previous_slide()
		else:		
			self.control.goto_slide(data['group_id'], data['slide_id'])

	def update_slide(self, slide):
		if (not slide.is_uptodate()) and slide.is_ready():
			print "Updating: %s" % slide
			if self.__get_slide(slide):
				self.__set_slide_timestamp(slide)
				self.__invalidate_cached_slide(slide)
				pyglet.resource.reindex()
		return slide

	def connect(self):
		def connect_cb(data):
			self.displayid=data.get('id')
			self.display=self.__create_display_tree(data)
		data = {'display_name': self.display_name}
		self.socket.send(Event.simple('iskdpy.hello', data, connect_cb))
		self.socket.run_all()
		if (self.displayid>0):
			self.channel=self.socket.channel('display_%d' % self.displayid).subscribe()
			self.channel.actions.update({
				'data': self.display_data_cb,
				'goto_slide': self.goto_slide_cb,
				'current_slide': NOP
				})
			return True
		return False
		
	def run_control(self):
		self.socket.run()

	def slide_done(self, slide):
		if (slide.is_override()):
			data = {'display_id': self.displayid, 
				'slide_id': slide.get_attrib('id'),
				'override_queue_id': slide.get_attrib('override_queue_id') }
		else:
			data = {'display_id': self.displayid, 
				'group_id': slide.get_attrib('group_id'), 
				'slide_id': slide.get_attrib('id') }
		self.socket.send(Event.simple('iskdpy.current_slide', data))

	def get_path(self):
		return self.cache_path

	def __invalidate_cached_slide(self, slide):
		filename=slide.get_filename()
		if filename in pyglet.resource._default_loader._cached_images:
			pyglet.resource._default_loader._cached_images.pop( filename )


	def __is_display_updated(self, data):
		try:
			updated_at=self.display.get_updated_at()
			return (data['updated_at'] > updated_at)
		except:
			return True
	
	def __create_display_tree(self, data):
		presentation_data=data.pop('presentation')
		groups=[]
		for group in presentation_data.pop('groups', []):
			slides=[]
			for slide in group.pop('slides', []):
				s=Slide(attribs=slide)
				s.set_attrib('filename', '%s/%d.%s' % (self.cache_path, s.get_id(), s.get_suffix()))
				s.set_attrib('group_id', group.get('id'))
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
	import config
	source=Source.factory('WebsocketSource')(config.sources[0])
	source.connect()
	source.update_display()
	#source._WebsocketSource__fill_cache()
	while not source.display:
		source.run_control()
	print "%s" % source.display

