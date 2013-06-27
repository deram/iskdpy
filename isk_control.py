from cocos.layer import Layer
from cocos.actions import *
from pyglet.window import key

from isk_presenter import Presenter

class KeyboardControlLayer(Layer):

	is_event_handler = True  #: enable pyglet's events

	def __init__( self):
		super(KeyboardControlLayer, self).__init__()
		self.push_all_handlers()

	def on_key_press( self, k , m ):
		if k == key.ENTER:
			self.do(CallFunc(self.parent.change_slide))
			return True


class RemoteControlLayer(Layer):
	def __init__(self, *args, **kwargs):
		self.source=Presenter.current().get_source()
		super(RemoteControlLayer, self).__init__(*args, **kwargs)

		self.schedule(self.run)

	def run(self, *args):
		ctrl=self.source.get_control()
		if ctrl:
			self.do(CallFunc(self.parent.change_slide))
			print ctrl

