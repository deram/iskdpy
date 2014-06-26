import logging
logger = logging.getLogger(__name__)

from cocos.layer import Layer
from pyglet.window import key

class _KeyboardControlLayer(Layer):

	is_event_handler = True  #: enable pyglet's events

	def __init__( self):
		super(_KeyboardControlLayer, self).__init__()
		self.push_all_handlers()

	def on_key_press( self, k , m ):
		if k == key.ENTER:
			self.parent.cancel_transition()
			RemoteControlLayer().callback.goto_next_slide()
			return True
		elif k == key.RIGHT:
			self.parent.cancel_transition()
			RemoteControlLayer().callback.goto_next_slide()
			return True
		elif k == key.LEFT:
			self.parent.cancel_transition()
			RemoteControlLayer().callback.goto_previous_slide()
			return True


class _RemoteControlLayer(Layer):
	def __init__(self, *args, **kwargs):
		super(_RemoteControlLayer, self).__init__(*args, **kwargs)
		self.schedule_interval(self.run, 0.1)
		self.task=None
		self.callback=None

	def set_callback(self, cb):
		self.callback=cb

	def set_task(self, task):
		self.task=task

	def run(self, *args):
		if self.task:
			self.task()

def RemoteControlLayer():
	if "__rcl" not in RemoteControlLayer.__dict__:
		RemoteControlLayer.__rcl=_RemoteControlLayer()
	return RemoteControlLayer.__rcl

def KeyboardControlLayer():
	if "__kcl" not in KeyboardControlLayer.__dict__:
		_KeyboardControlLayer.__kcl=_KeyboardControlLayer()
	return _KeyboardControlLayer.__kcl
