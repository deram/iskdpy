import logging
logger = logging.getLogger(__name__)

import cocos
from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.actions import CallFunc
from cocos.sprite import Sprite
import pyglet
from pyglet import font
from datetime import datetime
from weakref import proxy as weak
import os

from . import transitions
from .. import config
from ..import presenter
from . import control

class OutlineLabel(cocos.text.Label):
	def __init__( self, *args, **kwargs):
		self.text=None
		outline_color = kwargs.pop('outline_color')
		super(OutlineLabel, self).__init__(*args, **kwargs)
		x = kwargs.pop('x')
		y = kwargs.pop('y')
		kwargs.pop('color')
		for dx in (-2,2):
			for dy in (-2,2):
				self.add(cocos.text.Label(*args, x=x+dx, y=y+dy, color=outline_color, **kwargs), z=-1)

	def set_style(self, *args, **kwargs):
		self.walk(lambda item: item.element.set_style(*args, **kwargs))

	def set_text(self, text):
		def set_element_text(item):
			item.element.begin_update()
			item.element.text=text
			item.element.end_update()

		if (self.text != text):
			self.walk(set_element_text)
			self.text=text

class _ClockLayer(Layer):
	def __init__(self):
		super(_ClockLayer, self).__init__()
		self.time=datetime.now()
		self.clock_format=config.clock['format']

		self.add(OutlineLabel(
			text=self.time.strftime(self.clock_format) ,
			color=(255,255,255,255),
			font_size=config.clock.get('size', 40),
			font_name=config.clock['font'],
			bold=True,
			x=config.clock['x'],
			y=config.clock['y'],
			anchor_x=font.Text.LEFT,
			anchor_y=font.Text.BOTTOM,
			outline_color=(0,0,0,255) ), name='label')

		self.get('label').set_style('kerning', 2)
		
		self.schedule_interval(self.change_time, 0.2)

	def change_time(self, dt=0):
		self.time=datetime.now()
		self.get('label').set_text(self.time.strftime(self.clock_format))

__cl=None
def ClockLayer():
	global __cl
	if not __cl:
		__cl = _ClockLayer()
	return __cl

class SlideLayer(Layer):
	def __init__( self, file):
		super( SlideLayer, self ).__init__()
		try:
			g = Sprite( file, anchor=(0,0) )
		except pyglet.image.codecs.ImageDecodeException:
			self.invalid = True
		else:
			self.add( g )

class VideoLayer (SlideLayer):
	def __init__(self, video_name):
		super(SlideLayer, self).__init__()
                video_name=os.path.join(*video_name.split('/'))
                logger.debug('Video filename: %s' % video_name)
		source = pyglet.media.load(video_name)
		format = source.video_format
		if not format:
			logger.error('No video track in this source.')
			return

		self.media_player = pyglet.media.Player()
		self.media_player.queue(source)
		self.media_player.eos_action=self.media_player.EOS_PAUSE
		self.media_player.set_handler('on_eos', self.handle_on_eos)
		self.eos_handled=False

	def handle_on_eos(self):
		if ( not self.eos_handled ):
			self.do(CallFunc(self.parent.change_slide))
		self.eos_handled=True
		return True

	def on_enter(self):
		self.media_player.play()
		return super(VideoLayer, self).on_enter()

	def on_exit(self):
		self.media_player.pause()
		return super(VideoLayer, self).on_exit()

	def draw(self):
		self.media_player.get_texture().blit(0, 0)


class SlideScene(Scene):
	def __init__(self, slide=None):
		super(SlideScene, self).__init__()
		self.scheduled_event=False
		self.slide=weak(slide)
		if (not self.slide):
	   		self.slide=weak(presenter.get_next())

		duration=self.slide.get_duration()

		self.add(ColorLayer(0,0,0,255), z=-10)

		if (self.slide.get_type()=="video"):
			self.add(VideoLayer(self.slide.get_filename()), z=0)
			duration=0
		else:
			self.add(SlideLayer(self.slide.get_filename()), z=0)

		if (self.slide.get_clock()):
			self.add(ClockLayer(), z=5)

		self.add(control.KeyboardControlLayer(), z=10)
		self.add(control.RemoteControlLayer(), z=10)

		if (duration > 0 and not presenter.is_manual()):
			self.schedule_interval(self.change_slide, duration)

	def change_slide(self, dt=0):
		if not presenter.is_manual():
			slide=presenter.get_next()
			if not self.slide==slide and slide.is_ready():
				transition=transitions.getTransition('FadeBLTransition') #FadeTransition
				director.replace(transition(SlideScene(slide), 1.25))
		else:
			self.unschedule(self.change_slide)

	def reload_slide(self, dt=0):
		slide=presenter.get_current_slide()
		if not self.slide==slide and slide.is_ready():
			transition=transitions.getTransition('FadeBLTransition') #FadeTransition
			director.replace(transition(SlideScene(slide), 1.25))

