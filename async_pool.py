import asyncio
from itertools import count
import time
import logging

#import tracemalloc # trace

class worker_pool(object):
	def __init__(self, max_size = 16, name="async_worker_pool"):
		self.size = 0
		self.max_size = max_size
		self.Q = asyncio.Queue(self.max_size)
		#self.outQ = asyncio.Queue()
		
		self._loop = asyncio.get_event_loop()
		self.worker_count = None
		self.worker_dict = None
		
		self.__worker_id_gen = count(1)
		self.__id_bucket = []
		self._name = name

		logging.basicConfig(level=logging.DEBUG)
		logging.getLogger().setLevel(logging.INFO)

	def _worker_id_gen(self, pop=False):
		if pop:
			self.__id_bucket.append(pop)
			return
		if self.__id_bucket:
			return self.__id_bucket.pop()
		return next(self.__worker_id_gen)

	async def _worker(self, Q:asyncio.Queue, worker_id=None):
		logging.info(f"{self._name}`s worker {worker_id} was created")
		self.worker_count +=1
		
		while(True):
			task = await Q.get()
			if (task == "ExitMessage"):
				Q.task_done()
				break
			try:
				message = await task
				del task
			except Exception as e:
				logging.error(f"{self._name} {worker_id} error when await task\n {e}")
			finally:
				Q.task_done()

		if (worker_id in self.worker_dict):
			self.worker_dict.pop(worker_id)
			self.worker_count-=1
		self._worker_id_gen(pop = worker_id)
		logging.info(f"{self._name}`s worker {worker_id} ended")

	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await self._join()

	async def __aenter__(self):
		self.start()
		return self

	def _add_worker(self):
		workerId = self._worker_id_gen()
		self.worker_dict[workerId] = self._loop.create_task(
			self._worker(self.Q, worker_id=workerId))

	def start(self):
		#tracemalloc.start() # trace
		#tracemalloc.clear_traces()	# trace
		try:
			assert(self.worker_count == None)
		except:
			logging.error("this pool had already started")
			return
		self.worker_count = 0
		self.worker_dict = {}
		self.set_worker_count(self.max_size)

	async def _set_worker_count(self, count):
		if (count > self.max_size):	logging.warning(f"{self._name} max size exceed, set to max size {self.max_size}")
		self.size = min(count, self.max_size)

		if self.worker_count > self.size:
			[await self.Q.put("ExitMessage") for _ in range(self.worker_count - self.size)]
		else:
			[self._add_worker() for _ in range(self.size - self.worker_count)]
		await self.Q.join()

	def set_worker_count(self, count):
		self._loop.run_until_complete(self._set_worker_count(count))

	async def _join(self):
		if not self.worker_count:
			logging.error("this pool has no running worker")
			return 1
		
		## ensure all task has been digested
		await self.Q.join()

		## close all worker
		await self._set_worker_count(0)
		for worker in self.worker_dict.values():
			if not worker.done():
				await worker
		try: #check worker count
			assert(self.worker_count == 0)
			self.worker_count = None
			self.worker_dict = None
		except:
			logging.critical(f"{self._name} has some worker didn`t exit : {self.worker_count}")
			return 1

	def stop(self):
		## close loop
		self._loop.run_until_complete(self._join())
		#first_size, first_peak = tracemalloc.get_traced_memory() # trace
		#print(first_size, first_peak) # trace

	async def _push_all(self, iterable):

		try:
			while (True):
				future = next(iterable)
				await self.Q.put(future)
		except StopIteration:
			pass
		except Exception as e:
			logging.error(f"{self._name} push tasks failed\n{e}")

		await self.Q.join()

	def push_all(self, iterable): # try not to creat too much trafic, so put in one by one
		self._loop.run_until_complete(self._push_all(iterable))
		
	#async def fetch_one(self):
	#	return await self.outQ.get()
	#	
	#def read_all(self):
	#	out = []
	#	while not outQ.empty():
	#		out.append(asyncio.run_coroutine_threadsafe(self.fetch_one(), self._loop))
	#	return out

	"""
	async def self_logging(self):
		print worker count and size
		print runtime
	"""


