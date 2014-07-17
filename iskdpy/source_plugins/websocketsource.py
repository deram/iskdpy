import logging
logger = logging.getLogger(__name__)

from ..utils.auth_http import AuthHttp
import json

from ..utils.websocket_rails import WebsocketRails, Event, NOP
from ..source import SourcePlugin
from .. import types

import hashlib
import os

@SourcePlugin.register()
class WebsocketSource(SourcePlugin):
	def __init__(self, conf):
		super(WebsocketSource, self).__init__(conf)
		self.server=conf['server']
		self.cache_path=conf['cache_path']
		self.display_name=conf['display_name']

		self.sslopt={}
		if conf.get('ignore_hostname', False):
			from ..utils.websocket_rails import ignore_hostname_check
			logger.warning('SSL: Ignoring certificate hostname check')
			ignore_hostname_check(True)
		else:
			from ..utils.websocket_rails import ignore_hostname_check
			ignore_hostname_check(False)
		if conf.get('ignore_cert', False):
			import ssl
			logger.warning('SSL: Ignoring certificate check')
			self.sslopt["cert_reqs"]=ssl.CERT_NONE
		certs=conf.get('ca_certs', False)
		if certs and os.path.isfile(certs):
			logger.warning('SSL: Loading CA Certificates from %s', certs)
			self.sslopt["ca_certs"]=certs

		self.displayid=None
		self.dhash=None

		self.cookie=None
		self.channel=None

		# create authenticated http handler
		credentials={'username': conf['user'], 'password': conf['passwd']}
		login_url='%s/login?format=json' % self.server
		self.http=AuthHttp(login_url, credentials)
		logger.debug("AuthHttp result: %s", self.http.auth_result)
		if not self.http.auth_result:
			logger.info("Authentication failed, trying unauthenticated")
		
		# extract cookie in "key=val" format	
		cookie=self.http.get_cookie("_isk_session")
		if cookie:
			self.cookie= "%s=%s" % (cookie.name, cookie.value)

		# create websocket-rails connection, with the authenticated cookie
		header=["Content-Type:	application/json; charset=utf-8",
				"User-Agent: ISKdpy"]
		self.socket=WebsocketRails('%s/websocket' % self.server.replace('http', 'ws'), cookie=self.cookie, header=header, sslopt=self.sslopt, timeout=60)

		# create cache path if not excists
		if not os.path.exists(self.cache_path):
			os.makedirs(self.cache_path)

	#def get_display():

	def update_display(self):
		if self.display:
			return True
		else:
			return False

	def _display_data_cb(self, data):
		if 'username' in data:
			logger.info('Authenticated user: %s', data['username'])
		if self.__is_display_updated(data):
			try:
				with open(os.path.join(self.cache_path, "display.json"), 'w') as f:
					json.dump(data, f, indent=4, separators=(',', ': '), encoding="utf-8")
			except IOError:
				logger.exception('Failed to write display_data to backup file')
			self.display=self.__create_display_tree(data)
			logger.info('Received display_data. S:%d O:%d %s',
						self.display.presentation.total_slides,
						len(self.display.override_queue),
						('manual' if self.display.manual else ''))
			logger.debug('\n%s', self.display )
			try:
				self.get_callback()._display_updated(self.display)
			except AttributeError:
				logger.exception("Callback missing, running without factory?")
			return True
		logger.debug('Received old display_data')
		return False

	def _goto_slide_cb(self, data):
		logger.debug('Received goto_slide %s', data)
		if 'slide' in data.keys():
			if data['slide']=='next':
				self.get_callback()._goto_next_slide()
			elif data['slide']=='previous':
				self.get_callback()._goto_previous_slide()
		else:		
			self.get_callback()._goto_slide(data['group_id'], data['slide_id'])

	def update_slide(self, slide):
		if (not slide.uptodate) and slide.ready:
			logger.info("Updating: %s", slide)
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
		logger.debug("slide_done: %s", slide)
		data=None
		if (isinstance (slide, types.OverrideSlide)):
			if slide.id > 0:
				data = {'display_id': self.displayid, 
					'slide_id': slide.id,
					'override_queue_id': slide.override_queue_id }
		else:
			data = {'display_id': self.displayid, 
				'group_id': slide.group, 
				'slide_id': slide.id }
		if data:
			self.socket.send(Event.simple('iskdpy.current_slide', data))
		else:
			logger.debug("sent error instead of empty slide")
			data = {'display_id': self.displayid,
					'message': 'Empty slide shown'}
			self.socket.send(Event.simple('iskdpy.error', data))
		logger.debug("slide_done end")

	def __data_hash_updated(self, data):
		d=(data['presentation'], data['override_queue'], data['manual'])
		dhash=hashlib.md5(json.dumps(d, sort_keys=True)).hexdigest()
		if dhash != self.dhash:
			self.dhash=dhash
			return True
		return False
	def get_path(self):
		return self.cache_path

	def __is_display_updated(self, data):
		if not self.displayid and 'id' in data: 
			self.displayid=data['id']
			return True #First time, data always used.
		try:
			return self.__data_hash_updated(data)
		except:
			return True
	
	def __create_display_tree(self, data):
		presentation_data=data.pop('presentation')
		slides=[]
		for slide in presentation_data.pop('slides', []):
			s=types.Slide(**slide)
			s.filename='%s/%d.%s' % (self.cache_path, s.id, s.suffix)
			slides.append(s)
		presentation = types.Presentation(slides=slides, **presentation_data)
		slides=[]
		for slide in data.pop('override_queue', []):
			s=types.OverrideSlide(**slide)
			s.filename='%s/%d.%s' % (self.cache_path, s.id, s.suffix)
			slides.append(s)
		override=slides

		display=types.Display(presentation=presentation, override_queue=override, **data)
		return display

	def __get_slide(self, slide):
		location=slide.filename
		sid=slide.id
		return self.http.get_and_save('%s/slides/%d/full' % (self.server, sid), location)

	def __set_slide_timestamp(self, slide):
		time=slide.updated_at
		location=slide.filename
		os.utime(location, (time, time))
	
	def __fill_cache(self):
		slides=self.display.all_slides
		for slide in slides.values():
			self.update_slide(slide)
		return self.display


if __name__ == "__main__":
	#from pprint import pprint
	from .. import config
	from ..main import setup_logger
	setup_logger()
	#source=Source.factory('WebsocketSource')(config.sources[0])
	source=WebsocketSource(config.sources[0])
	source.connect()
	source.update_display()
	#source._WebsocketSource__fill_cache()
	print "%s" % (source.display, )
	print "%s" % repr(source.display.presentation[45])
	print "%s" % repr(types.Slide())

