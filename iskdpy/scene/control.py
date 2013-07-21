from cocos.layer import Layer
from cocos.actions import *
from pyglet.window import key

from ..presenter import Presenter

class _KeyboardControlLayer(Layer):

	is_event_handler = True  #: enable pyglet's events

	def __init__( self):
		super(_KeyboardControlLayer, self).__init__()
		self.push_all_handlers()

	def on_key_press( self, k , m ):
		if k == key.ENTER:
			Presenter().get_next()
			self.do(CallFunc(self.parent.reload_slide))
			return True
		elif k == key.RIGHT:
			Presenter().get_next()
			self.do(CallFunc(self.parent.reload_slide))
			return True
		elif k == key.LEFT:
			Presenter().get_previous()
			self.do(CallFunc(self.parent.reload_slide))
			return True


class _RemoteControlLayer(Layer):
	def __init__(self, *args, **kwargs):
		super(_RemoteControlLayer, self).__init__(*args, **kwargs)
		Presenter().register_control(self)
		self.schedule_interval(self.run, 0.1)

	def run(self, *args):
		Presenter().run_control()

	def goto_slide(self, group_id, slide_id):
		def func(dt=0):
			if Presenter().set_current_slide(group_id, slide_id):
				self.parent.reload_slide()
		self.do(Delay(0.1) + CallFunc(func))
	
	def goto_next_slide(self):
		def func(dt=0):
			if Presenter().get_next():
				self.parent.reload_slide()
		self.do(Delay(0.1) + CallFunc(func))

	def goto_previous_slide(self):
		def func(dt=0):
			if Presenter().Presenter().get_previous():
				self.parent.reload_slide()
		self.do(Delay(0.1) + CallFunc(func))
	
	def reload_slide(self):
		self.do(Delay(0.1) + CallFunc(self.parent.reload_slide))

__rcl=None
def RemoteControlLayer():
	global __rcl
	if not __rcl:
		__rcl=_RemoteControlLayer()
	return __rcl

__kcl=None
def KeyboardControlLayer():
	global __kcl
	if not __kcl:
		__kcl=_KeyboardControlLayer()
	return __kcl
