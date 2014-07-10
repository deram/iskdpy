# Default configs override with local_config.py
window=dict(width=1920, height=1080, resizable=True)
scale_down=False
fullscreen=True

clock=dict(x=1450, y=12, format="%a %H:%M:%S", size=48, font="Arial")
empty_slide=dict(filename= 'base.png', duration=10, type= 'image', show_clock=True)

default_duration=5
default_cache_path='cache'

effect_ids=[ 'unknown', 'normal', 'subtle', 'alert' ]
effect_mapping=dict(update=dict(unknown='crossfade', normal='crossfade', subtle='crossfade', alert='fade_red'),
					normal=dict(unknown='crossfade', normal='tile_swipe', subtle='crossfade', alert='fade_red'))

logger_levels=dict( iskdpy='INFO' )

sources=[ dict( source_name='LocalSource', display_name="test_display", local_dir="local") ]
output="CocosOutput"
font_files=[]

future={}
# local configuration overrides defaults
try:
	from local_config import *
except: # pragma: no cover
	print 'local_config.py not found'
