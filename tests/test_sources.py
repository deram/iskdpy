import unittest
from iskdpy.source_plugins.local import LocalSource
from iskdpy.source_plugins.websocketsource import WebsocketSource

class TestLocalSource(unittest.TestCase):
	def setUp(self):
		conf=dict( source_name='LocalSource', display_name="test_display", local_dir="local")	
		self.source = LocalSource(conf)

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
		conf=dict( source_name='WebsocketSource', display_name="deram-test", cache_path="cache", server="http://isk0.asm.fi", user="isk", passwd="Kissa")
		self.source = WebsocketSource(conf)

	def test_update_display(self):
		self.assertTrue(self.source)
		self.assertTrue(self.source.connect())
		display=self.source.get_display()
		self.assertTrue(display)
		self.assertEqual(len(display.get_override()), 0)
		presentation=display.get_presentation()
		self.assertGreater(len(presentation), 0)
		self.assertGreater(len(presentation[0]), 0)



