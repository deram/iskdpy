import logging
logger = logging.getLogger(__name__)

import websocket
import json
from select import select
import socket
import random

from threading import Thread, RLock

from .misc_utils import RateLimit

def NOP(data):
	pass

class Event():
	def __init__(self, data, success_cb=NOP, failure_cb=NOP):
		#print data
		self.success_cb=success_cb
		self.failure_cb=failure_cb

		if isinstance(data, basestring):
			data=json.loads(data, "utf8")
			if isinstance(data[0], list):
				data=data[0]
		try:
			self.name=data[0]
			self.attr=data[1]
			if isinstance(self.attr, dict):
				self.id = self.attr.get('id', random.randint(1, 65535))
				self.channel = self.attr.get('channel')
				self.data = self.attr.pop('data')
				if 'success' in self.attr:
					self.result = True
					self.success = self.attr.get('success')
				else:
					self.result = False
				self.connection_id = data[2]
		except IndexError:
			pass

	def attributes(self):
		return {'id': self.id, 'channel': self.channel, 'data': self.data} 

	def __repr__(self):
		return json.dumps([self.name, self.attributes()])

	@classmethod
	def pong(cls, conn_id):
		return cls(['websocket_rails.pong', {'data':{'connection_id': conn_id }}])

	@classmethod
	def simple(cls, name, data, *args, **kwargs):
		return cls([name, {'data':data}], *args, **kwargs)

class Channel():
	def __init__(self, wsr, channel_name):
		self.wsr=wsr
		self.channel_name=channel_name
		self.actions={}

	def unsubscribe(self):
		self.wsr.send(Event(['websocket_rails.unsubscribe', {'data':{'channel': self.channel_name }}]))
		return self

	def subscribe(self):
		self.wsr.send(Event(['websocket_rails.subscribe', {'data':{'channel': self.channel_name }}]))
		return self

	def send(self, ev):
		ev.channel=self.channel_name
		self.wsr.send(ev)
		return self

class WebsocketRails():
	def __init__(self, url, timeout=0):
		websocket.enableTrace(False)
		self.timeout=timeout
		self.conn_id=None
		self.url=url
		self.ws=None
		self.channels={}
		self.queue={}
		self.messages=[]
		self.actions={
			'websocket_rails.ping': self.__pong,
			'client_connected': self.__connected
		}

		self.thread=None
		self.send_lock=RLock()
		self.recv_lock=RLock()

		self._connect()

	def start(self):
		if not self.thread:
			self.running=True
			self.thread=Thread(target=self._work)
			self.thread.daemon=True
			self.thread.start()

	def stop(self):
		if self.thread and self.running:
			self.running=False
			self.thread.join()
			self.thread=None

	def _work(self):
		while self.running:
			self.run()

	@RateLimit(1)
	def _connect(self):
		with self.send_lock, self.recv_lock:
			try:
				logger.info('Connecting %s' % self.url)
				self.ws=websocket.create_connection(self.url)
				self.queue={}
				for channel in self.channels.values():
					channel.subscribe()
				while len(self.messages):
					self.send(self.messages.pop(0))
			except (websocket.WebSocketException, socket.error):
				pass

	def _send(self, ev):
		with self.send_lock:
			try:
				return self.ws.send(repr(ev))
			except (websocket.WebSocketConnectionClosedException, AttributeError, socket.error):
				self.messages.append(ev)
				self._connect()
		
	def _recv(self):
		with self.recv_lock:
			try:
				(rlist, wlist, xlist) = select([self.ws.fileno()],[],[],self.timeout)
				if rlist:
					data=self.ws.recv()
					if data:
						return Event(data)
			except (websocket.WebSocketConnectionClosedException, AttributeError, socket.error):
				self._connect()

	def _run(self, ev):
		if not ev:
			return
		if ev.id and ev.id in self.queue:
			if ev.result:
				if ev.success:
					func=self.queue.pop(ev.id).success_cb
				else:
					func=self.queue.pop(ev.id).failure_cb
			else:
				logger.error("UNKNOWN RESULT FOR: %s id:%d" % (ev.name, ev.id))
				logger.debug("SENT: %s" % self.queue.pop(ev.id).__dict__)
				logger.debug("RECEIVED: %s" % ev.__dict__)
				func=NOP

		elif ev.channel:
			ch=self.channels.get(ev.channel)
			func=ch.actions.get(ev.name)
		else:
			func=self.actions.get(ev.name)

		if func:
			return func(ev.data)
		elif ev:
			logger.debug("UNHANDLED: %s" % ev.__dict__)
		else: #pragma: no cover
			return #this is impossible

	def run(self):
		self._run(self._recv())

	def run_all(self):
		while len(self.queue):
			self.run()

	def send(self, ev):
		self.queue.update({ev.id: ev})
		self._send(ev)

	def channel(self, channel):
		chan=self.channels.get(channel)
		if not chan:
			chan=Channel(self, channel)
			self.channels.update({channel: chan})

		return chan

	def close(self):
		self.ws.close()

	def __connected(self, data):
		self.conn_id=data.get('connection_id')
		logger.debug("Connected: id=%s" % self.conn_id)

	def __pong(self, data):
		self.send(Event.pong(self.conn_id))
