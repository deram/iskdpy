import urllib2
import base64
from pprint import pprint 
from slideshow import *


def get_url_authenticated(url, user="isk", passwd="Kissa"):
    request = urllib2.Request(url)
    base64string = base64.encodestring('%s:%s' % (user, passwd)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)   
    result = urllib2.urlopen(request)
    return result.read()
   
def get_url_and_save(url, file):
    resource = get_url_authenticated(url)
    output = open('cache/%s' % file, 'wb')
    output.write(resource)
    output.close()
    return resource

def get_json():
    json = get_url_and_save('http://isk.depili.fi/displays/3/presentation?format=json', 'main.json')
    return json

def get_image(id):
    get_url_and_save('http://isk.depili.fi/slides/%s/full' % id , '%s.png' % id ) 


if __name__ == "__main__":
    json= get_json()
    print json
    show=Slideshow(show=json)
    slides=show.get_all_slides()
    for slide in slides.keys():
        get_image(slide)

