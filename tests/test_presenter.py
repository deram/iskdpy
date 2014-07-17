import unittest

from iskdpy import presenter
from iskdpy.types import *


def gen_test_dpy():
	slides=[]
	for i in xrange(3):
		for j in xrange(4):
			slides.append(Slide(id="%d%d"%(i,j), name="testslide %d%d" % (i,j), group="%d" % i))
	presentation=Presentation(id=1, name="testpresentation_1", slides=slides)
	return Display(id=1, name="testdisplay", presentation=presentation)

class FakePlugin():
	def __init__(self):
		self.dpy=None
		self.dpy_updated=False
	def update_display(self):
		return self.dpy_updated
	def get_display(self):
		self.dpy_updated=False
		return self.dpy
	def update_slide(self, *a, **kw):
		return FakeReturn()
	def slide_done(self, *a, **kw):
		return FakeReturn()
	def set_slide(self, *a, **kw):
		return FakeReturn()
	def cancel_transition(self, *a, **kw):
		return FakeReturn()
	def refresh_slide_cache(self, *a, **kw):
		return FakeReturn()
	def get_current(self):
		return self

class FakeReturn():
	def __enter__(self):
		return self
	def __exit__(self, *a, **kw):
		pass

class TestPresenter(unittest.TestCase):
	def setUp(self):
		self.presenter=presenter
		presenter.SourcePlugin=FakePlugin()
		presenter.OutputPlugin=FakePlugin()
	
	def tearDown(self):
		presenter=self.presenter

	def test001_empty_start(self):
		self.assertTrue(presenter._get_slide("next"))
		self.assertTrue(presenter._get_slide("previous"))

	def test002_simple_display_data(self):
		presenter.SourcePlugin.dpy=gen_test_dpy()
		presenter.SourcePlugin.dpy_updated=True
		self.assertTrue(presenter._update_display())

		self.assertTrue(presenter._get_slide("next"))

		current=presenter._state.current_slide
		for i in xrange(13):
			self.assertTrue(presenter._get_slide("next"))
		for i in xrange(13):
			self.assertTrue(presenter._get_slide("previous"))
		self.assertTrue(current==presenter._state.current_slide)

	def test003_set_current_slide(self):
		self.assertTrue(presenter._set_current_slide("2","23"))
		self.assertEqual(presenter._state.pos, 11)

		self.assertFalse(presenter._set_current_slide("5","53"))

