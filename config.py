window=dict(width=1280, height=720, resizable=True)
scale_down=True
fullscreen=False

clock=dict(x=900, y=10, format="%a %H:%M:%S", font="Franklin Gothic Heavy")
empty_slide=dict(filename= 'base.png', duration=10, type= 'image', clock=False)

default_duration=5
default_cache_path='cache'

import credentials
sources=[ dict( source_name='LocalSource', display_name="test_display", local_dir="local") ]
#sources=[ dict( credentials.sites[0].items(), source_name='NetworkSource', display_name="deram-test", cache_path="cache") ]
#sources=[ dict( credentials.sites[0].items(), source_name='BackgroundNetworkSource', display_name="deram-test", cache_path="cache ") ]

default_source=sources[0]

# Sources in use
import isk_background_network_source
import isk_network_source
import isk_local_source
