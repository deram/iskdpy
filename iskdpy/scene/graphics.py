import cocos
from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.scenes.transitions import *
from cocos.actions import *
from cocos.sprite import Sprite
import pyglet
from pyglet import gl, font
from datetime import datetime
from time import strftime

from pyglet.window import key

from .transitions import *
from .. import config
from ..presenter import Presenter
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

class ClockLayer(Layer):
	def __init__(self):
		super(ClockLayer, self).__init__()
		self.time=datetime.now()
		self.clock_format=config.clock['format']

		self.add(OutlineLabel(
			text=self.time.strftime(self.clock_format) ,
			color=(255,255,255,255),
			font_size=40,
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

		source = pyglet.media.load(video_name)
		format = source.video_format
		if not format:
			print 'No video track in this source.'
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
		self.slide=slide
		if (not self.slide):
	   		self.slide=Presenter().get_next()

		self.duration=self.slide.get_duration()
			
		self.add(ColorLayer(0,0,0,255), z=-10)

		if (self.slide.get_type()=="video"):
			self.add(VideoLayer(self.slide.get_filename()), z=0)
			self.duration=0
		else:
			self.add(SlideLayer(self.slide.get_filename()), z=0)

		if (self.slide.get_clock()):
			self.add(ClockLayer(), z=5)

		self.add(control.KeyboardControlLayer(), z=10)
		self.add(control.RemoteControlLayer(), z=10)

		if (self.duration > 0):
			self.schedule_interval(self.change_slide, self.duration)

	def change_slide(self, dt=0):
		slide=Presenter().get_next()
		if not self.slide==slide and slide.is_ready():
			transition=FadeBLTransition #FadeTransition
			director.replace(transition(SlideScene(slide), 1.25))

