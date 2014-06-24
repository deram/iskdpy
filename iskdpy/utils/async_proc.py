import logging
logger = logging.getLogger(__name__)

from multiprocessing import Process, Queue, current_process, Event
from threading import Thread, current_thread
from Queue import Full, Empty
from exceptions import Exception
from multiprocessing.pool import ThreadPool
import sys
class AsyncProcess(object):
	def __init__(self, obj):
		self.obj=obj
		self.q1=Queue()
		self.q2=Queue()
		self.remote=QueuedCall(self.obj, self.q1, self.q2)
		self.local=QueuedCall(self.obj, self.q2, self.q1)

		self.proc=Process(target=self._remote_target)
		self.proc.daemon=True
		self.proc.start()

		self.thread=Thread(target=self._local_target)
		self.thread.daemon=True
		self.thread.start()

	def __getattr__( self, name ):
		print current_process(), name
		return getattr( self.local, name )

	def _remote_target(self):
		self.obj.__callback=self.remote
		self.remote.target()

	def _local_target(self):
		self.local.target()

class QueuedCall(object):
	def __init__(self, obj, q_to, q_from):
		self.obj=obj
		self.q_to=q_to
		self.q_from=q_from
		self.returns={}

	def __getattr__( self, name ):
		attr=getattr( self.obj, name )
		def inner(*args, **kwargs):
			ret=ReturnValue()
			job=Job(name, args, kwargs)
			self.returns[job.id]=ret
			self.q_to.put(job)
			return ret
		return inner

	def target(self):
		pool=ThreadPool()
		while True:
			job=self.q_from.get()
			if job.done and job.id in self.returns:
				self.returns.pop(job.id).set(job.ret)
			else:
				def helper(job):
					try:
						f=getattr(self.obj, job.name)
						job.ret=f(*job.args, **job.kwargs)
					except Exception as e:
						logger.debug("transfering exception", exc_info=True)
						job.ret=e
					job.done=True
					self.q_to.put(job)
				pool.apply_async(helper, [job])

class Job(object):
	_next_id=1
	def __init__(self, name, args, kwargs):
		self.name=name
		self.args=args
		self.kwargs=kwargs
		self.ret=None
		self.done=False
		self.id=self.next_id()

	def __str__(self):
		return str(self.__dict__)

	@classmethod
	def next_id(cls):
		cls._next_id+=1
		return cls._next_id

class ReturnValue(object):
	def __init__(self):
		self.ev=Event()
		self.ret=None

	def __getattr__( self, name ):
		if self.ev.is_set() or self.ev.wait():
			if isinstance(self.ret, Exception):
				raise self.ret
			return getattr( self.ret, name )
		else:
			raise JobNotDone()

	def set(self, ret):
		self.ret=ret
		self.ev.set()

	def get(self, block=True, timeout=None):
		if block:
			if self.ev.wait(timeout):
				if isinstance(self.ret, Exception):
					raise self.ret
				return self.ret
		else:
			if self.ev.is_set():
				if isinstance(self.ret, Exception):
					raise self.ret
				return self.ret
		raise JobNotDone()

class JobNotDone(Exception):
	pass

