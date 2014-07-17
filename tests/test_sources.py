from iskdpy.config import test_configs
import unittest
from iskdpy.source_plugins import local
from iskdpy.source_plugins import websocketsource
from iskdpy.source import SourcePlugin

def NOP(*a,**kw):
	pass

captures=[]
def capture(name):
	def inner(*a, **kw):
		captures.append((name, a, kw))
	return inner

SourcePlugin._signal_refresh_slide_cache=NOP
SourcePlugin._signal_display_updated=capture('display_updated')

class TestLocalSource(unittest.TestCase):
	def setUp(self):
		conf=test_configs['LocalSource']
		self.source=SourcePlugin.factory(conf.get('source_name'), conf)

	def test_update_display(self):
		self.assertTrue(self.source)
		self.assertTrue(self.source.connect())
		self.assertTrue(self.source.update_display())
		self.assertFalse(self.source.update_display())
		with self.source.get_display() as display:
			self.assertTrue(display)
			self.assertEqual(len(display.override_queue), 0)
			presentation=display.presentation
			self.assertEqual(len(presentation), 5)
		
class TestWebsocketSource(unittest.TestCase):
	def setUp(self):
		conf=test_configs['WebsocketSource']
		self.source=SourcePlugin.factory(conf.get('source_name'), conf)

	def test001_update_display(self):
		self.assertTrue(self.source)
		self.assertTrue(self.source.connect())
		with self.source.get_display() as display:
			self.assertTrue(display)
			self.assertEqual(len(display.override_queue), 1)
			presentation=display.presentation
			self.assertGreater(len(presentation), 0)

	def test002_slide_effect(self):
		self.assertTrue(self.source.connect())
		with self.source.get_display() as display:
			presentation=display.presentation
			self.assertEqual(presentation[0].effect,'normal')

