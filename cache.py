import urllib2
import base64
import json
from pprint import pprint 
from isk_types import Presentation

def slideid_to_file(id):
	return cachefile('%d.png' % id)

def cachefile(name):
	return 'cache/%s' % name

def get_url_authenticated(url, user="isk", passwd="Kissa"):
	request = urllib2.Request(url)
	base64string = base64.encodestring('%s:%s' % (user, passwd)).replace('\n', '')
	request.add_header("Authorization", "Basic %s" % base64string)   
	result = urllib2.urlopen(request)
	return result.read()

def get_url_and_save(url, file):
	resource = get_url_authenticated(url)
	output = open(file , 'wb')
	output.write(resource)
	output.close()
	return resource

def get_json():
	json_data = get_url_and_save('http://isk.depili.fi/displays/3/presentation?format=json', 'cache/main.json')
	return json_data

def get_slide(slide):
	return get_url_and_save('http://isk.depili.fi/slides/%s/full' % slide.get_id(), slide.get_filename() ) 

def set_image_timestamp(id, modified):
	print "to be implemented"
	

def fill_cache():
	json_data=get_json()
	tmp=json.loads(json_data)
	show=Presentation(tmp)
	slides=show.get_all_slides()
	for slide in slides.values():
		print "Fetching: %s" % slide
		get_slide(slide)


if __name__ == "__main__":
	fill_cache()
