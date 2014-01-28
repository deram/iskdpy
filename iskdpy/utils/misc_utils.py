import time
import inspect

def RateLimit(interval, default=None):
	def decorate(f):
		f.lastTimeCalled=[0]
		def inner(*args,**kargs):
			elapsed = time.time() - f.lastTimeCalled[0]
			if (elapsed < interval):
				return default
			f.lastTimeCalled[0] = time.time()
			return f(*args,**kargs)
		inner.actual=f # for reseting in tests
		return inner
	return decorate
