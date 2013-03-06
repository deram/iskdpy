# Default configs override with local_config.py
window=dict(width=1280, height=720, resizable=True)
scale_down=True
fullscreen=False

clock=dict(x=900, y=10, format="%a %H:%M:%S", font="Franklin Gothic Heavy")
empty_slide=dict(filename= 'base.png', duration=10, type= 'image', clock=False)

default_duration=5
default_cache_path='cache'

sources=[ dict( source_name='LocalSource', display_name="test_display", local_dir="local") ]

# local configuration overrides defaults
from local_config import *

# Sources availlable. Maybe needed to move elsewhere or made totally dynamic...
import isk_background_network_source
import isk_network_source
import isk_local_source
