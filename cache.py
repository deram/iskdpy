import urllib2
import base64
import json
import os
from pprint import pprint 
from isk_types import Display
import config


def get_url_authenticated(url):
	request = urllib2.Request(url)
	base64string = base64.encodestring('%s:%s' % (config.user, config.passwd)).replace('\n', '')
	request.add_header("Authorization", "Basic %s" % base64string)   
	result = urllib2.urlopen(request, None, 1)
	return result.read()

def get_url_and_save(url, file):
	resource = get_url_authenticated(url)
	output = open(file , 'wb')
	output.write(resource)
	output.close()
	return resource

def get_json():
	file='%s/main.json' % config.cache_path
	url='http://isk.depili.fi/displays/%d?format=json' % config.displayid
	json_data = get_url_and_save(url, file)
	return json_data

def fetch_slide(slide):
	file=slide.get_cachefile()
	id=slide.get_id()
	get_url_and_save('http://isk.depili.fi/slides/%s/full' % id, file)
	set_slide_timestamp(slide)

def set_slide_timestamp(slide):
	time=slide.get_update_time()
	file=slide.get_cachefile()
	os.utime(file, (time,time))

def refresh_slide(slide):
	if (not slide.is_cached()):
		print "Updating: %s" % slide
		fetch_slide(slide)
	else:
		print "Skipping: %s" % slide
		#set_slide_timestamp(slide) # in case of errors, this might be useful
	return slide

def fill_cache_and_get_display():
	json_data=get_json()
	tmp=json.loads(json_data)
	dpy=Display(tmp)
	slides=dpy.get_all_slides()
	for slide in slides.values():
		refresh_slide(slide)
        return dpy

if __name__ == "__main__":
	fill_cache_and_get_display()
