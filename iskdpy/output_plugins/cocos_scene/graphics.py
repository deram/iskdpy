from __future__ import division

import logging
logger = logging.getLogger(__name__)

import cocos
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
from cocos.actions import MoveTo, FadeOutBLTiles, FadeOut, FadeIn, StopGrid, AccelDeccel, Hide, Delay
from cocos.sprite import Sprite
import pyglet
from pyglet import font
from datetime import datetime
from weakref import proxy as weak
import os

from . import control
from ... import config

class OutlineLabel(cocos.text.Label):
	def __init__( self, *args, **kwargs):
		self.text=None
		outline_color = kwargs.pop('outline_color')
		super(OutlineLabel, self).__init__(*args, **kwargs)
		x = kwargs.pop('x')
		y = kwargs.pop('y')
		kwargs.pop('color')
		for dx in (-2, 2):
			for dy in (-2, 2):
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
		self._show=True

		self.add(OutlineLabel(
			text=self.time.strftime(self.clock_format) ,
			color=(255, 255, 255, 255),
			font_size=config.clock.get('size', 40),
			font_name=config.clock['font'],
			bold=True,
			x=config.clock['x'],
			y=config.clock['y'],
			anchor_x=font.Text.LEFT,
			anchor_y=font.Text.BOTTOM,
			outline_color=(0, 0, 0, 255) ), name='label')

		self.get('label').set_style('kerning', 2)
		
		self.schedule_interval(self.change_time, 0.2)

	def change_time(self, dt=0):
		self.time=datetime.now()
		self.get('label').set_text(self.time.strftime(self.clock_format))

	def clock_shown(self, show):
		if self._show != show:
			if show:
				self.do(AccelDeccel(MoveTo((0, 0), duration=1)))
			else:
				self.do(AccelDeccel(MoveTo((0, -100), duration=1)))
			self._show=show

def ClockLayer():
	if '__cl' not in ClockLayer.__dict__.keys():
		ClockLayer.__cl = _ClockLayer()
	return ClockLayer.__cl

class SlideLayer(Layer):
	def __init__( self, filename):
		super( SlideLayer, self ).__init__()
		try:
			self.g = Sprite( filename, anchor=(0, 0) )
		except (pyglet.image.codecs.ImageDecodeException, pyglet.resource.ResourceNotFoundException):
			self.invalid = True
		else:
			ratio_h = config.window['height'] / self.g.height
			ratio_w = config.window['width'] / self.g.width
			self.g.scale=min(ratio_h, ratio_w)
			self.add( self.g )
			self._opacity=0

	@property
	def opacity(self):
		return self._opacity

	@opacity.setter
	def opacity(self, o):
		self._opacity=o
		if 'g' in self.__dict__:
			self.g.opacity=o


class VideoLayer (SlideLayer):
	def __init__(self, video_name):
		super(VideoLayer, self).__init__()
		video_name=os.path.join(*video_name.split('/'))
		logger.debug('Video filename: %s', video_name)
		source = pyglet.media.load(video_name)
		video_format = source.video_format
		if not video_format:
			logger.error('No video track in this source.')
			return

		self.media_player = pyglet.media.Player()
		self.media_player.queue(source)
		self.media_player.eos_action=self.media_player.EOS_PAUSE
		self.media_player.set_handler('on_eos', control.RemoteControlLayer().callback._goto_next_slide)

	def on_enter(self):
		self.media_player.play()
		return super(VideoLayer, self).on_enter()

	def on_exit(self):
		self.media_player.pause()
		return super(VideoLayer, self).on_exit()

	def draw(self):
		self.media_player.get_texture().blit(0, 0)


class SlideScene(Scene):
	def __init__(self, slide):
		super(SlideScene, self).__init__()

		self.add(ColorLayer(0, 0, 0, 255), z=-10, name='color')

		self.add(self.__get_slide_layer(slide), z=0, name='slide')

		self.add(ClockLayer(), z=5, name='clock')
		ClockLayer().clock_shown(slide.show_clock)

		self.add(control.KeyboardControlLayer(), z=10)
		self.add(control.RemoteControlLayer(), z=10)

	def __get_slide_layer(self, slide):
		if (slide.type=="video"):
			return VideoLayer(slide.filename)
		else:
			return SlideLayer(slide.filename)

	def cancel_transition(self):
		try:
			self.remove('temp')
		except Exception:
			pass # no transition running.

	def set_slide(self, slide, change='normal'):
		self.get('clock').clock_shown(slide.show_clock)
		
		out_layer=self.get('slide')
		in_layer=self.__get_slide_layer(slide)
		try:
			self.remove('temp')
		except Exception:
			pass # no transition running.
		try:
			self.remove('temp_col')
		except Exception:
			pass # no transition running.
		self.remove('slide')

		self.add(out_layer, z=1, name='temp')
		self.add(in_layer, z=0, name='slide')

		transition=config.effect_mapping[change][slide.effect]
		logger.debug("Changing slide with transition: %s", transition)
		if transition == 'tile_swipe':
			out_layer.do(FadeOutBLTiles(grid=(16, 9), duration=1) + Hide() + StopGrid())
		elif transition == 'crossfade':
			out_layer.do(FadeOut(duration=1))
		elif transition == 'fade_red':
			col_layer=ColorLayer(255, 0, 0, 0)
			self.add(col_layer, z=1.1, name='temp_col')
			col_layer.do(FadeIn(duration=0.3)+Delay(0.5)+FadeOut(duration=1.5))
			out_layer.do(Delay(0.3) + Hide())
		else:
			out_layer.do(Hide())



