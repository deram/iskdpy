import logging
logger = logging.getLogger(__name__)

import websocket
import json
from select import select
import socket
import random

from .misc_utils import RateLimit

def NOP(data):
	pass

class Event():
	def __init__(self, data, success_cb=NOP, failure_cb=NOP):
		#print data
		self.success_cb=success_cb
		self.failure_cb=failure_cb

		if isinstance(data, basestring):
			data=json.loads(data, "utf8")[0]
		try:
			self.name=data[0]
			self.attr=data[1]
			if isinstance(self.attr, dict):
				self.id = self.attr.get('id', random.randint(1, 65535))
				self.channel = self.attr.get('channel')
				self.data = self.attr.pop('data')
				if 'success' in self.attr and self.attr.get('success'):
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
		if conn_id:
			return cls(['websocket_rails.pong', {'data':{'connection_id': conn_id }}])

	@classmethod
	def simple(cls, name, data, *args, **kwargs):
		return cls([name, {'data':data}], *args, **kwargs)

class Channel():
	def __init__(self, ws, channel_name):
		self.ws=ws
		self.channel_name=channel_name
		self.actions={}

	def unsubscribe(self):
		self.ws.send(Event(['websocket_rails.unsubscribe', {'data':{'channel': self.channel_name }}]))
		return self

	def subscribe(self):
		self.ws.send(Event(['websocket_rails.subscribe', {'data':{'channel': self.channel_name }}]))
		return self

	def send(self, ev):
		ev.channel=self.channel_name
		self.ws.send(ev)
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
		self._connect()

	@RateLimit(1)
	def _connect(self):
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
		try:
			return self.ws.send(repr(ev))
		except (websocket.WebSocketConnectionClosedException, AttributeError, socket.error):
			self.messages.append(ev)
			self._connect()
		
	def _recv(self):
		try:
			(rlist, wlist, xlist) = select([self.ws.fileno()],[],[],self.timeout)
			if rlist:
				data=self.ws.recv()
				if data:
					return Event(data)
		except (websocket.WebSocketConnectionClosedException, AttributeError, socket.error):
			self._connect()

	def run(self):
		ev=self._recv()
		if not ev:
			return
		if ev.result and ev.id in self.queue:
			if ev.success:
				func=self.queue.pop(ev.id).success_cb
			else:
				func=self.queue.pop(ev.id).failure_cb

		elif ev.channel:
			ch=self.channels.get(ev.channel)
			func=ch.actions.get(ev.name)
		else:
			func=self.actions.get(ev.name)

		if func:
			return func(ev.data)
		elif ev:
			logger.debug("UNHANDLED: %s" % ev.__dict__)

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

	def __pong(self, data):
		self.send(Event.pong(self.conn_id))


if __name__ == "__main__":
	def myprint(data):
		print data.keys(),data.get('id')

	ws = WebsocketRails("ws://isk0.asm.fi/websocket", 10)
	ws.send(Event.simple('iskdpy.hello', {'display_name': 'deram-test'}, myprint))
	#ws.channel('display_1').subscribe()
	ws.run_all()
	ws.send(Event.simple('iskdpy.display_data', 1, myprint))
	ws.send(Event.simple('iskdpy.display_data', 1, myprint))
	ws.send(Event.simple('iskdpy.display_data', 1, myprint))
	ws.send(Event.simple('iskdpy.display_data', 1, myprint))
	ws.send(Event.simple('iskdpy.display_data', 1, myprint))
	ws.send(Event.simple('iskdpy.display_data', 1, myprint))
	ws.run_all()
	ws.close()
