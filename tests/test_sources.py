from iskdpy.config import test_configs
import unittest
from iskdpy.source_plugins import local
from iskdpy.source_plugins import websocketsource

def NOP(*a,**kw):
	pass

websocketsource.presenter.refresh_slide_cache=NOP
websocketsource.presenter.display_updated=NOP

class TestLocalSource(unittest.TestCase):
	def setUp(self):
		conf=test_configs['LocalSource']
		self.source = local.LocalSource(conf)

	def test_update_display(self):
		self.assertTrue(self.source)
		self.assertTrue(self.source.connect())
		self.assertTrue(self.source.update_display())
		self.assertFalse(self.source.update_display())
		display=self.source.get_display()
		self.assertTrue(display)
		self.assertEqual(len(display.get_override()), 0)
		presentation=display.get_presentation()
		self.assertEqual(len(presentation), 1)
		self.assertGreater(len(presentation[0]), 0)
		
class TestWebsocketSource(unittest.TestCase):
	def setUp(self):
		conf=test_configs['WebsocketSource']
		self.source = websocketsource.WebsocketSource(conf)

	def test_update_display(self):
		self.assertTrue(self.source)
		self.assertTrue(self.source.connect())
		display=self.source.get_display()
		self.assertTrue(display)
		self.assertEqual(len(display.get_override()), 0)
		presentation=display.get_presentation()
		self.assertGreater(len(presentation), 0)
		self.assertGreater(len(presentation[0]), 0)



