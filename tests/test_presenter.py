import unittest

from iskdpy import presenter
from iskdpy.types import *


def gen_test_dpy():
	slides=[]
	for i in xrange(3):
		for j in xrange(4):
			slides.append(Slide(attribs=dict(id="%d%d"%(i,j), name="testslide %d%d" % (i,j), group="%d" % i)))
	presentation=Presentation(attribs=dict(id=1, name="testpresentation_1"), slides=slides)
	return Display(attribs=dict(id=1, name="testdisplay"), presentation=presentation)

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
		pass
	def slide_done(self, *a, **kw):
		pass
	def set_slide(self, *a, **kw):
		pass
	def get_current(self):
		return self

class TestPresenter(unittest.TestCase):
	def setUp(self):
		self.presenter=presenter
		presenter.Source=FakePlugin()
		presenter.OutputPlugin=FakePlugin()
	
	def tearDown(self):
		presenter=self.presenter

	def test001_empty_start(self):
		self.assertTrue(presenter._get_next())
		self.assertTrue(presenter._get_previous())

	def test002_simple_display_data(self):
		presenter.Source.dpy=gen_test_dpy()
		presenter.Source.dpy_updated=True
		self.assertTrue(presenter._update_display())

		self.assertTrue(presenter._get_next())

		current=presenter._get_current_slide()
		for i in xrange(13):
			self.assertTrue(presenter._get_next())
		for i in xrange(13):
			self.assertTrue(presenter._get_previous())
		self.assertTrue(current==presenter._get_current_slide())

	def test003_set_current_slide(self):
		self.assertTrue(presenter._set_current_slide("2","23"))
		self.assertTrue(presenter.pos==11)

		self.assertFalse(presenter._set_current_slide("5","53"))

