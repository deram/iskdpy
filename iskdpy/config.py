# Default configs override with local_config.py
window=dict(width=1280, height=720, resizable=True)
scale_down=False
fullscreen=True

clock=dict(x=970, y=12, format="%a %H:%M:%S", size=32, font="Franklin Gothic Heavy")
empty_slide=dict(filename= 'base.png', duration=10, type= 'image', show_clock=False)

default_duration=5
default_cache_path='cache'

sources=[ dict( source_name='LocalSource', display_name="test_display", local_dir="local") ]

# local configuration overrides defaults
try:
	from local_config import *
except:
	print 'local_config.py not found'
