import logging
logger = logging.getLogger(__name__)

from multiprocessing import Process, Queue, current_process, Event
from threading import Thread
from multiprocessing.pool import ThreadPool

class AsyncProcess(object):
	def __init__(self, obj):
		self.obj=obj
		self.queues=(Queue(), Queue())
		self.remote=QueuedCall(self.obj, *self.queues)
		self.local=QueuedCall(self.obj, *reversed(self.queues))

		self.proc=Process(target=self._remote_target, name=self.obj.__class__.__name__)
		self.proc.daemon=True
		self.proc.start()

		self.guard=Thread(target=self._guard_target, name="Guard_%s" % self.obj.__class__.__name__)
		self.guard.daemon=True
		self.guard.start()

		self.thread=Thread(target=self._local_target, name="Async_%s" % self.obj.__class__.__name__)
		self.thread.daemon=True
		self.thread.start()

	def __getattr__(self, name):
		if self.proc.is_alive():
			return getattr(self.local, name)
		else:
			raise ProcessNotAlive()

	def _remote_target(self):
		self.obj.__callback=self.remote
		self.remote.target()

	def _local_target(self):
		self.local.target()

	def _guard_target(self):
		self.proc.join()
		self.proc.terminate()
		self.local.terminate()

class QueuedCall(object):
	def __init__(self, obj, q_to, q_from):
		self.obj=obj
		self.q_to=q_to
		self.q_from=q_from
		self.names=(current_process().name, obj.__class__.__name__)
		self.returns={}

	def __getattr__(self, name):
		logger.debug("%s->%s %s", self.names[0], self.names[1], name)
		getattr(self.obj, name)
		def inner(*args, **kwargs):
			ret=ReturnValue()
			job=Job(name, args, kwargs)
			self.returns[job.id]=ret
			self.q_to.put(job)
			return ret
		return inner

	def target(self):
		if not current_process().name == self.names[0]:
			self.names=tuple(reversed(self.names))
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

	def terminate(self):
		for r in self.returns.values():
			r.set(ProcessNotAlive())

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

class ReturnValue():
	def __init__(self):
		self.ev=Event()
		self.ret=None

	def __enter__(self):
		return self.get()

	def __exit__(self, *args, **kwargs):
		pass

	def __getattr__(self, name):
		if self.ev.is_set() or self.ev.wait():
			self._get()
			return getattr(self.ret, name)
		else:
			raise JobNotDone()

	def _get(self):
		if isinstance(self.ret, Exception):
			ex=self.ret
			self.ret=None 
			raise ex # pylint: disable=E0702
					 # clearly ex can not be None. known bug in pylint.
		return self.ret

	def set(self, ret):
		self.ret=ret
		self.ev.set()

	def get(self, block=True, timeout=None):
		if block:
			if self.ev.wait(timeout):
				return self._get()
		else:
			if self.ev.is_set():
				return self._get()
		raise JobNotDone()

class JobNotDone(Exception):
	pass

class ProcessNotAlive(Exception):
	pass

if __name__ == '__main__':
	pass
