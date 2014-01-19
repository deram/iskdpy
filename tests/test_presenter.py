import unittest

from iskdpy import presenter
from iskdpy.types import *


def gen_test_dpy():
	groups=[]
	for i in xrange(3):
		slides=[]
		for j in xrange(4):
			slides.append(Slide(attribs=dict(id="%d%d"%(i,j), name="testslide %d%d" % (i,j))))
		groups.append(Group(attribs=dict(id="%d"%i, name="testgroup_%d" % (i)), slides=slides))
	presentation=Presentation(attribs=dict(id=1, name="testpresentation_1"), groups=groups)
	override=OverrideGroup()
	return Display(attribs=dict(id=1, name="testdisplay"), presentation=presentation, override=override)

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
		self.assertTrue(presenter._get_next())
		self.assertTrue(presenter._get_next())
		self.assertTrue(presenter._get_next())
		self.assertTrue(presenter._get_next())
		self.assertTrue(presenter._get_next())
		self.assertTrue(presenter._get_next())
		self.assertTrue(presenter._get_next())

	def test003_set_current_slide(self):
		self.assertTrue(presenter._set_current_slide("2","23"))
		self.assertTrue(presenter.gpos==2)
		self.assertTrue(presenter.spos==3)

		self.assertFalse(presenter._set_current_slide("5","53"))

