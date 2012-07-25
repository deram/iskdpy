import urllib2
from urllib import urlencode
import base64
import json
import os
from pprint import pprint 
from isk_types import Display
import config
import pyglet

def get_url_authenticated(url, data=None):
	try:
		request = urllib2.Request(url)
		base64string = base64.encodestring('%s:%s' % (config.user, config.passwd)).replace('\n', '')
		request.add_header("Authorization", "Basic %s" % base64string)   
		result = urllib2.urlopen(request, data, 1)
		return result.read()
	except Exception:
		return False 

def get_url_and_save(url, file):
	resource = get_url_authenticated(url)
	if resource:
		output = open(file , 'wb')
		output.write(resource)
		output.close()
	return resource

def post_url_authenticated(url, data):
	encoded=urlencode(data)
	return get_url_authenticated(url, encoded)

def post_current_slide(slide):
	url='%s/displays/%d/current_slide' % (config.server, config.displayid)
	data={"group": slide.get_groupid(), "slide": slide.get_id()}
	post_url_authenticated(url, data)

def post_override_slide(slide):
	url='%s/displays/%d/slide_shown' % (config.server, config.displayid)
	data={"override": slide.get_override_id()}
	post_url_authenticated(url, data)

def get_json(reload=True):
	file='%s/main.json' % config.cache_path
	url='%s/displays/%d?format=json' % (config.server, config.displayid)
	json_data = get_url_and_save(url, file)
	if json_data:
		return json_data
	elif reload:
		output = open(file , 'rb')
		tmp=output.read()
		output.close()
		return tmp
	else:
		return False

def fetch_slide(slide):
	file=slide.get_cachefile()
	id=slide.get_id()
	return get_url_and_save('%s/slides/%d/full' % (config.server, id), file)

def set_slide_timestamp(slide):
	time=slide.get_update_time()
	file=slide.get_cachefile()
	os.utime(file, (time,time))

def refresh_slide(slide):
	if (not slide.is_cached()):
		print "Updating: %s" % slide
		if fetch_slide(slide):
			set_slide_timestamp(slide)
			pyglet.resource.reindex()
	#else:
	#	set_slide_timestamp(slide) # in case of errors, this might be useful
	return slide

def fill_cache_and_get_display():
	json_data=get_json()
	tmp=json.loads(json_data)
	dpy=Display(tmp)
	slides=dpy.get_all_slides()
	for slide in slides.values():
		refresh_slide(slide)
	return dpy

def get_file(file):
	file = open(file , 'wb')
	output.write(resource)
	output.close()

if __name__ == "__main__":
	fill_cache_and_get_display()
