window=dict(width=1280, height=720, resizable=True)
scale_down=True
fullscreen=False

clock=dict(x=900, y=10, format="%a %H:%M:%S", font="Franklin Gothic Heavy")
empty_slide=dict(filename= 'base.png', duration=10, type= 'image', clock=False)

default_duration=5
default_cache_path='cache'

sources=[ dict( source_name='NetworkSource', display_name="deram-test", cache_path="cache", server="http://isk0.asm.fi/", user="isk", passwd="Kissa") ]
#sources=[ dict( source_name='BackgroundNetworkSource', display_name="deram-test", cache_path="cache", server="http://isk0.asm.fi/", user="isk", passwd="Kissa") ]

default_source=sources[0]

# Sources in use
#import isk_network_source
import isk_background_network_source
#import isk_local_source
