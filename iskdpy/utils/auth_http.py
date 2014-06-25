import logging
logger = logging.getLogger(__name__)

import cookielib
import urllib2
from urllib import urlencode
import base64
from . import file
import socket

class AuthHttp():
	def __init__(self, loginurl, credentials, timeout=2):
		self.timeout=timeout
		self.cookiejar = cookielib.CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookiejar))
		self.auth_result=self.post(loginurl, credentials)

	def get_cookie(self, name):
		for c in self.cookiejar:
			if c.name == name:
				return c
		return None

	def get(self, url, data=None):
		try:
			request = urllib2.Request(url)
			result = self.opener.open(request, data, self.timeout)
			return result.read()
		except urllib2.HTTPError, e:
			logger.error("HTTPError: %s %s %s" % (url, e.code, e.reason))
		except urllib2.URLError, e:
			logger.error("URLError: %s %s" % (url, e.reason))
		except socket.timeout:
			logger.error("Timeout connecting")
		return False
	
	def get_and_save(self, url, filename):
		resource = self.get(url)
		if resource:
			file.write(filename, resource)
		return resource
	
	def post(self, url, data):
		encoded=urlencode(data)
		return self.get(url, encoded)
