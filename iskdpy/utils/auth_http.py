import urllib2
from urllib import urlencode
import base64
from . import file
import socket

class AuthHttp():
	def __init__(self, user, passwd, timeout=2):
		self.user=user
		self.passwd=passwd
		self.timeout=timeout

	def get(self, url, data=None):
		try:
			request = urllib2.Request(url)
			base64string = base64.encodestring('%s:%s' % (self.user, self.passwd)).replace('\n', '')
			request.add_header("Authorization", "Basic %s" % base64string)   
			result = urllib2.urlopen(request, data, self.timeout)
			return result.read()
		except urllib2.URLError:
			print "URLError: Could not connect %s" % (url)
			return False 
		except socket.timeout:
			print "Timeout connecting"
			return False
	
	def get_and_save(self, url, filename):
		resource = self.get(url)
		if resource:
			file.write(filename, resource)
		return resource
	
	def post(self, url, data):
		encoded=urlencode(data)
		return self.get(url, encoded)
