import unittest
import time
from websocket import WebSocketException, WebSocketConnectionClosedException
from iskdpy.utils.misc_utils import RateLimit
from iskdpy.utils import websocket_rails

class MockConnection():
	def __init__(self, *a, **kw):
		self.callstack=[]
		self.messages_in=[]
		self.messages_out=[]
		self.fail=False
		self.connected=False

	def _report_call(self, func, *a, **kw):
		self.callstack.append(dict(f=func, a=a, kw=kw))
	def _mock_message(self, message):
		if message:
			self.messages_in.append("[%s]" % message)
		else:
			self.messages_in.append(message)
	def _get_message(self, i=0):
		return self.messages_out.pop(i)
	def _pop(self, i=0):
		return self.callstack.pop(i)

	def fileno(self):
		return -1
	def select(self, *a, **kw):
		if self.fail or not self.connected:
			self.connected=False
			raise WebSocketConnectionClosedException()
		return (len(self.messages_in)>0, False, False)

	def send(self, *a, **kw):
		self._report_call('send', *a, **kw)
		if self.fail or not self.connected:
			self.connected=False
			raise WebSocketConnectionClosedException()
		else:
			self.messages_out.append(a[0])
	def recv(self, *a, **kw):
		self._report_call('recv', *a, **kw)
		if self.fail or not self.connected:
			self.connected=False
			raise WebSocketConnectionClosedException()
		elif len(self.messages_in):
			return self.messages_in.pop()
		else:
			return
	def close(self, *a, **kw):
		self._report_call('close', *a, **kw)
		self.connected=False

	def create_connection(self, *a, **kw):
		self._report_call('create_connection', *a, **kw)
		if self.fail:
			self.connected=False
			raise WebSocketException()
		else:
			self.connected=True
			return self

foo=None
class TestWebsocketRailsMisc(unittest.TestCase):
	def setUp(self):
		self.ws=websocket_rails.WebsocketRails(None)

	def test_event_with_no_data_dict(self):
		ev=websocket_rails.Event(['testname', ''])
		self.assertEqual(ev.name, 'testname')

	#def test_pong_without_connid(self):
	#	ev=websocket_rails.Event.pong(None)
	#	self.assertEqual(ev, None)

	def test_websocketrails_run(self):
		global foo
		def fail(ev):
			global foo
			foo=ev
		ev=websocket_rails.Event(['testname', {'id': 1, 'data': 1, 'success': False}], failure_cb=fail)
		self.ws.queue.update({ev.id: ev})
		self.ws._run(ev)
		self.assertEqual(foo, ev.data)

		ev=websocket_rails.Event(['testname', {'id': 16, 'data': 2}])
		self.ws.queue.update({ev.id: ev})
		self.ws._run(ev)
		self.assertNotEqual(foo, ev.data)

		ev=websocket_rails.Event(['testname', {'id': 1, 'data': 3, 'success': True}], success_cb=None)
		self.ws.queue.update({ev.id: ev})
		self.ws._run(ev)
		self.assertNotEqual(foo, ev.data)

class TestWebsocketRailsConnection(unittest.TestCase):
	SAMPLE_EVENT_DATA = ['event','message']
	SAMPLE_EVENT = "{ data: ['event','message'] }"
	URL = "ws://example.com:3000"

	def setUp(self):
		self.conn=MockConnection()

		self.tmp1=websocket_rails.websocket.create_connection
		self.tmp2=websocket_rails.WebsocketRails._connect
		self.tmp3=websocket_rails.select

		websocket_rails.websocket.create_connection=self.conn.create_connection
		websocket_rails.WebsocketRails._connect=websocket_rails.WebsocketRails._connect.actual
		websocket_rails.select=self.conn.select

	def tearDown(self):
		websocket_rails.websocket.create_connection=self.tmp1
		websocket_rails.WebsocketRails._connect=self.tmp2
		websocket_rails.select=self.tmp3

	def test001_constructor(self):
		ws=websocket_rails.WebsocketRails(self.URL)
		self.assertTrue(self.conn._pop()['a'][0] == self.URL)
		self.assertTrue(self.conn.connected)
		ws.close()
		self.assertFalse(self.conn.connected)


	def test002_send(self):
		self.conn.fail=True # CONNECTION FAILING
		ws=websocket_rails.WebsocketRails(self.URL)

		self.assertTrue(self.conn._pop()['f'] == 'create_connection')
		self.assertFalse(self.conn.connected)

		ev1=websocket_rails.Event.simple('event', 'message')
		ws.send(ev1)
		self.assertTrue(self.conn._pop()['f'] == 'create_connection')
		self.assertTrue(len(ws.messages) == 1 )
		self.assertTrue(ws.messages[0] == ev1)

		self.conn.fail=False # CONNECTIONS OK
		ws._connect()
		self.assertTrue(self.conn._pop()['f'] == 'create_connection')
		self.assertTrue(self.conn.connected)
		self.assertTrue(self.conn._pop()['f'] == 'send')
		self.assertTrue(self.conn._get_message() == repr(ev1))
		self.assertTrue(len(ws.messages) == 0 )

		self.conn.fail=True # CONNECTION FAILING
		ev2=websocket_rails.Event.simple('event', 'message2')
		ws.send(ev2)
		self.assertTrue(self.conn._pop()['f'] == 'send')
		self.assertTrue(self.conn._pop()['f'] == 'create_connection')
		self.assertFalse(self.conn.connected)
		self.assertTrue(len(ws.messages) == 1 )

		self.conn.fail=False # CONNECTIONS OK
		ev3=websocket_rails.Event.simple('event', 'message3')
		ws.send(ev3)
		self.assertTrue(self.conn._pop()['f'] == 'send')
		self.assertTrue(self.conn._pop()['f'] == 'create_connection')
		self.assertTrue(self.conn._pop()['f'] == 'send')
		self.assertTrue(self.conn._pop()['f'] == 'send')
		self.assertTrue(self.conn.connected)
		self.assertTrue(len(ws.messages) == 0 )
		
		self.assertTrue(self.conn._get_message() == repr(ev2))
		self.assertTrue(self.conn._get_message() == repr(ev3))

	def test003_recv(self):
		ws=websocket_rails.WebsocketRails(self.URL)
		self.assertTrue(self.conn.connected)
		self.assertTrue(self.conn._pop()['f'] == 'create_connection')

		ev=websocket_rails.Event.simple('event', 'message')
		self.conn._mock_message(ev)
		self.assertTrue(repr(ws._recv()) == repr(ev))
		self.conn._mock_message(None)
		self.assertTrue(ws._recv() is None)

	def test004_run(self):
		ws=websocket_rails.WebsocketRails(self.URL)
		ev=websocket_rails.Event.simple('client_connected', {'connection_id': 15})
		self.conn._mock_message(ev)
		ws.run()
		self.assertTrue(ws.conn_id==15)

		ev=websocket_rails.Event.simple('websocket_rails.ping', {})
		self.conn._mock_message(ev)
		ws.run()
		msg=self.conn._get_message()
		ev2=websocket_rails.Event(msg)
		self.assertTrue(ev2.name=='websocket_rails.pong')
		self.assertTrue(ev2.data['connection_id']==15)

	def test005_channel(self):
		ws=websocket_rails.WebsocketRails(self.URL)
		self.conn._mock_message(websocket_rails.Event.simple('client_connected', {'connection_id': 15}))
		ws.run()

		name='test'
		ws.channel(name).subscribe()
		ev=websocket_rails.Event(self.conn._get_message())
		self.assertTrue(ev.name=='websocket_rails.subscribe')
		self.assertTrue(ev.data.get('channel')==name)

		self.temp=None
		def _action(data):
			self.temp=data

		# Send message to channel
		chan=ws.channel(name)
		chan.actions.update({'action': _action})
		ev2=websocket_rails.Event.simple('action', {'foobar': 'test'})
		chan.send(ev2)

		msg=self.conn._get_message()

		ev3=websocket_rails.Event(msg)
		self.assertTrue(ev3.channel == name)
		self.assertTrue(ev2.name == ev3.name)
		self.assertTrue(ev2.data == ev3.data)
		self.assertTrue(ev2.id == ev3.id)


		# Received a message from channel (pretend not from us)
		del ws.queue[ev3.id]
		self.conn._mock_message(ev3)
		ws.run()
		self.assertTrue(self.temp)
		self.assertTrue(self.temp.get('foobar')=='test')

		self.assertTrue(len(self.conn.messages_out)==0)
		self.conn.fail=True
		ws.run()
		self.assertTrue(len(self.conn.messages_out)==0)
		self.conn.fail=False
		ws.run()
		self.assertTrue(len(self.conn.messages_out)==1)

		ev=websocket_rails.Event(self.conn._get_message())
		self.assertTrue(ev.name=='websocket_rails.subscribe')
		self.assertTrue(ev.data.get('channel')==name)

		chan.unsubscribe()
		ev=websocket_rails.Event(self.conn._get_message())
		self.assertTrue(ev.name=='websocket_rails.unsubscribe')
		self.assertTrue(ev.data.get('channel')==name)

	def test006_thread(self):
		ws=websocket_rails.WebsocketRails(self.URL)
		ws.start()
		thread=ws.thread
		self.assertTrue(ws.running)
		ws.start()
		self.assertTrue(ws.thread==thread)
		self.assertTrue(ws.running)
		ev=websocket_rails.Event.simple('client_connected', {'connection_id': 15})
		self.conn._mock_message(ev)
		time.sleep(0.1)
		self.assertTrue(ws.conn_id==15)

		ev=websocket_rails.Event.simple('websocket_rails.ping', {})
		self.conn._mock_message(ev)
		time.sleep(0.1)
		msg=self.conn._get_message()
		ev2=websocket_rails.Event(msg)
		self.assertTrue(ev2.name=='websocket_rails.pong')
		self.assertTrue(ev2.data['connection_id']==15)
		ws.stop()
		self.assertFalse(ws.running)
		ws.stop()
		self.assertFalse(ws.running)

