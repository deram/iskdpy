from cocos.director import director
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene
#from cocos.scenes.transitions import *
from isk_transitions import *
from cocos.actions import *
from cocos.sprite import Sprite
import pyglet
from pyglet import gl, font
from datetime import datetime
from time import strftime

from pyglet.window import key

from isk_presenter import CurrentPresenter

class OutlineLabel(pyglet.text.Label):
    def __init__( self, *args, **kwargs):
        outline_color = kwargs.pop('outline_color')
        super(OutlineLabel, self).__init__(*args, **kwargs)
        x = kwargs.pop('x')
        y = kwargs.pop('y')
        kwargs.pop('color')
        self.outline=[]
        for dx in (-2,2):
            for dy in (-2,2):
                self.outline.append(pyglet.text.Label(*args, x=x+dx, y=y+dy, 
                                                      color=outline_color, 
                                                      **kwargs))
    def draw(self):
        for item in self.outline:
            item.draw()
        super(OutlineLabel, self).draw()

    def set_style(self, *args, **kwargs):
        super(OutlineLabel, self).set_style(*args, **kwargs)
        for item in self.outline:
            item.set_style(*args, **kwargs)

    def begin_update(self):
        super(OutlineLabel, self).begin_update()
        for item in self.outline:
            item.begin_update()

    def end_update(self):
        super(OutlineLabel, self).end_update()
        for item in self.outline:
            item.text=self.text
            item.end_update()


class ControlLayer(Layer):

    is_event_handler = True     #: enable pyglet's events

    def __init__( self, clock=True ):
        super(ControlLayer, self).__init__()
        self.scheduled_event=False
        self.push_all_handlers()
        self.clock=clock
        now=datetime.now()
        self.text_title = OutlineLabel(text=now.strftime("%H:%M:%S") ,
            color=(255,255,255,255),
            font_size=40,
            font_name="Franklin Gothic Heavy",
            bold=True,
            x=1280-35,
            y=130,
            anchor_x=font.Text.RIGHT,
            anchor_y=font.Text.TOP,
            outline_color=(0,50,0,255) )
        self.text_title.set_style('kerning', 2)

    def draw( self ):
        if (self.clock):
            self.text_title.draw()

    def on_key_press( self, k , m ):
        if k == key.ENTER:
            self.do(CallFunc(self.parent.change_slide))
            return True

    def on_enter(self):
	if (not self.scheduled_event):
            self.scheduled_event = True
            if (self.clock):
                self.schedule(self.change_time)
        return super(ControlLayer, self).on_enter()

    def change_time(self, dt=0):
        now=datetime.now()
        self.text_title.begin_update()
        self.text_title.text=now.strftime("%H:%M:%S")
        self.text_title.end_update()



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
            transition=FadeBLTransition #FadeTransition
            director.replace(transition(SlideScene(), 1.25))
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
    def __init__(self, filename="", type=""):
        super(SlideScene, self).__init__()
        self.scheduled_event=False
        if (not filename):
       	    slide=CurrentPresenter().get_next()
            self.filename=slide.get_cachefile()
            self.duration=slide.get_duration()
            self.clock=slide.get_clock()
            self.type=slide.get_type()
        else:
            self.filename=filename
            self.duration=100
            self.clock=True
            
        self.add(ColorLayer(255,255,255,255), z=-10)

	if (self.type=="video"):
            self.add(VideoLayer(self.filename), z=0)
	else:
            self.add(SlideLayer(self.filename), z=0)

        self.add(ControlLayer(self.clock), z=10)

    def on_enter(self):
	if (not self.scheduled_event and self.duration > 0):
            self.scheduled_event = True
            self.schedule_interval(self.change_slide, self.duration)
        return super(SlideScene, self).on_enter()

    def change_slide(self, dt=0):
        transition=FadeBLTransition #FadeTransition
        director.replace(transition(SlideScene(), 1.25))


