from threading import Thread, current_thread, Event
from Queue import Queue, Empty
from exceptions import Exception


class QueuedThread():
	def __init__(self, thread=None, daemon=True):
		self.queue=Queue()
		if thread:
			self.thread=thread
		else:
			self.thread=Thread(None, self._worker)
			self.thread.daemon=daemon

	def start(self):
		if current_thread() == self.thread:
			return None
		else:
			return self.thread.start()

	def work_one(self, block=False):
		if current_thread() == self.thread:
			try:
				(func,args,kwargs,ret)=self.queue.get(block)
				ret.set(func(*args,**kwargs))
				self.queue.task_done()
			except Empty:
				pass

	def work_all(self):
		if current_thread() == self.thread:
			while not self.queue.empty():
				self.work_one()

	def _worker(self):
		while True:
			self.work_one(True)

	def decorate(self, func):
		def decorator(*args, **kwargs):
			if current_thread() == self.thread:
				ret=QueuedThread.ReturnValue()
				ret.set(func(*args, **kwargs))
				return ret
			else:
				ret=QueuedThread.ReturnValue()
				self.queue.put((func,args,kwargs,ret))
				return ret
		return decorator

	class ReturnValue:
		def __init__(self):
			self.ev=Event()

		def __getattr__( self, name ):
			if self.ev.is_set() or self.ev.wait():
				return getattr( self.ret, name )
			else:
				raise AttributeError

		def set(self, ret):
			self.ret=ret
			self.ev.set()

		def get(self, block=True, timeout=None):
			if block:
				if self.ev.wait(timeout):
					return self.ret
			else:
				if self.ev.is_set():
					return self.ret
			raise JobNotDone()

	class JobNotDone(Exception):
		pass


if __name__ == "__main__":
	qt=QueuedThread()

	@qt.decorate
	def bar(a,b,c):
		ret= "a: %d b: %d c: '%s'" % (a,b,c)
		print "Returning: %s" % ret
		return ret
	
	qt.start()
	ret1=bar(1,2,"foobar")
	ret2=bar(2,6,"fobar")
	print ret2.get()
	print ret1.get()

