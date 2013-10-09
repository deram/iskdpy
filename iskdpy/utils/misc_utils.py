import time

def RateLimit(interval, default=None):
	def decorate(f):
		lastTimeCalled = [0.0]
		def inner(*args,**kargs):
			elapsed = time.clock() - lastTimeCalled[0]
			if (elapsed < interval):
				return default
			lastTimeCalled[0] = time.clock()
			return f(*args,**kargs)
		return inner
	return decorate
