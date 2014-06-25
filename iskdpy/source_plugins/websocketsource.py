import logging
logger = logging.getLogger(__name__)

from ..utils.auth_http import AuthHttp
from ..utils import file
import json

from ..utils.websocket_rails import WebsocketRails, Event, NOP
from ..source import Source
from .. import types

import os

@Source.register()
class WebsocketSource(Source):
	def __init__(self, conf):
		super(WebsocketSource, self).__init__(conf)
		self.server=conf['server']
		self.cache_path=conf['cache_path']
		self.displayid=None
		self.display_name=conf['display_name']
		self.http=AuthHttp(conf['user'], conf['passwd'])
		self.socket=WebsocketRails('%s/websocket' % self.server.replace('http', 'ws'), 60)
		self.channel=None
		if not os.path.exists(self.cache_path):
			os.makedirs(self.cache_path)

	#def get_display():

	def update_display(self):
		if self.display:
			return True
		else:
			return False

	def _display_data_cb(self, data):
		if self.__is_display_updated(data):
			file.write(os.path.join(self.cache_path, "display.json"), json.dumps(data))
			self.display=self.__create_display_tree(data)
			logger.info('Received display_data. S:%d O:%d %s' % (self.display.get_presentation().get_total_slides(), 
																len(self.display.get_override()), 
																('manual' if self.display.is_manual() else '') ))
			logger.debug('\n%s' % (self.display) )
			self.get_callback()._display_updated()
			return True
		logger.debug('Received old display_data')
		return False

	def _goto_slide_cb(self, data):
		logger.debug('Received goto_slide %s' % data)
		if 'slide' in data.keys():
			if data['slide']=='next':
				self.get_callback()._goto_next_slide()
			elif data['slide']=='previous':
				self.get_callback()._goto_previous_slide()
		else:		
			self.get_callback()._goto_slide(data['group_id'], data['slide_id'])

	def update_slide(self, slide):
		if (not slide.is_uptodate()) and slide.is_ready():
			logger.info("Updating: %s" % slide)
			if self.__get_slide(slide):
				self.__set_slide_timestamp(slide)
				self.get_callback()._refresh_slide_cache(slide)
		return slide

	def connect(self):
		data = {'display_name': self.display_name}
		self.socket.send(Event.simple('iskdpy.hello', data, self._display_data_cb))
		self.socket.run_all()
		if (self.displayid>0):
			self.channel=self.socket.channel('display_%d' % self.displayid).subscribe()
			self.channel.actions.update({
				'data': self._display_data_cb,
				'goto_slide': self._goto_slide_cb,
				'current_slide': NOP
				})
			self.socket.start()
			return True
		return False
		
	def __socket_run(self):
		while True:
			self.socket.run()

	def slide_done(self, slide):
		logger.debug("slide_done: %s" % slide)
		if (slide.is_override()):
			data = {'display_id': self.displayid, 
				'slide_id': slide.get_attrib('id'),
				'override_queue_id': slide.get_attrib('override_queue_id') }
		else:
			data = {'display_id': self.displayid, 
				'group_id': slide.get_groupid(), 
				'slide_id': slide.get_id() }
		self.socket.send(Event.simple('iskdpy.current_slide', data))
		logger.debug("slide_done end")

	def get_path(self):
		return self.cache_path

	def __is_display_updated(self, data):
		if not self.displayid and 'id' in data: 
			self.displayid=data['id']
			return True #First time, data always used.
		try:
			return data['metadata_updated_at'] > self.display.get_metadata_updated_at()
		except:
			return True
	
	def __create_display_tree(self, data):
		presentation_data=data.pop('presentation')
		slides=[]
		for slide in presentation_data.pop('slides', []):
			s=types.Slide(attribs=slide)
			s.set_attrib('filename', '%s/%d.%s' % (self.cache_path, s.get_id(), s.get_suffix()))
			slides.append(s)
		presentation = types.Presentation(slides=slides, attribs=presentation_data)
		slides=[]
		for slide in data.pop('override_queue', []):
			s=types.OverrideSlide(attribs=slide)
			s.set_attrib('filename', '%s/%d.%s' % (self.cache_path, s.get_id(), s.get_suffix()))
			slides.append(s)
		override=slides

		display=types.Display(presentation=presentation, override=override, attribs=data, name=self.display_name)
		return display

	def __get_slide(self, slide):
		location=slide.get_filename()
		sid=slide.get_id()
		return self.http.get_and_save('%s/slides/%d/full' % (self.server, sid), location)

	def __set_slide_timestamp(self, slide):
		time=slide.get_update_time()
		location=slide.get_filename()
		os.utime(location, (time, time))
	
	def __fill_cache(self):
		slides=self.display.get_all_slides()
		for slide in slides.values():
			self.update_slide(slide)
		return self.display


if __name__ == "__main__":
	#from pprint import pprint
	import config
	source=Source.factory('WebsocketSource')(config.sources[0])
	source.connect()
	source.update_display()
	#source._WebsocketSource__fill_cache()
	print "%s" % source.display

