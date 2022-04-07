import asyncio
from itertools import count
import time
import logging

#import tracemalloc # trace

class worker_pool(object):
	def __init__(self, max_size = 16, verbose_level=20, name="async_worker_pool"):
		self.max_size = max_size 				# maximum number for workers
		self.Q = asyncio.Queue(self.max_size) 	# input queue for awaitable objects
		#self.outQ = asyncio.Queue()
		self.size = 0 							# expected the amount of worker to be create

		self._loop = asyncio.get_event_loop() 	# event loop for the current thread
		self.worker_count = None 				# currently running worker
		self.worker_dict = None 				# hash table of workers

		# tools for generate a worker
		self.__worker_id_gen = count(1)	# incremental id
		self.__id_bucket = []			# recycle used id

		self._name = name 		# pool name

		# logging level
		logging.basicConfig(level=verbose_level)
		logging.getLogger().setLevel(verbose_level)

	def _worker_id_gen(self, pop=False):
		if pop:							# indicate putting closed worker's id into bucket
			self.__id_bucket.append(pop)
			return
		if len(self.__id_bucket):	# if there is any id in bucket, pop that id
			return self.__id_bucket.pop()
		return next(self.__worker_id_gen) # if not, generate a new id


	async def _worker(self, Q:asyncio.Queue, worker_id=None):
		logging.info(f"{self._name}`s worker {worker_id} was created")
		self.worker_count +=1   # add to count after the worker has been started
		
		while(True):						# working block:
			task = await Q.get()			# retreive a object from queue
			if (task == "ExitMessage"):		# check if it is an exit command
				Q.task_done()				# report task done
				break
			if asyncio.iscoroutine(task):	# check if the object is awaitable
				await task 					# operates the object
			Q.task_done()					# report task done

		if (worker_id in self.worker_dict):
			self.worker_dict.pop(worker_id) 	# remove itself from hash table

		self.worker_count-=1 					# decrease the number of running workers
		self._worker_id_gen(pop = worker_id) 	# put its id into bucket
		logging.info(f"{self._name}`s worker {worker_id} ended")

		# protocol for asynchronous context managers 
	async def __aexit__(self, exc_type, exc_val, exc_tb):
		await self._join()

	async def __aenter__(self):	
		self.start()
		return self
 
 	# add one worker
	def _add_worker(self):
		workerId = self._worker_id_gen()	# assign a worker id
		self.worker_dict[workerId] = self._loop.create_task(
			self._worker(self.Q, worker_id=workerId))
		# create a worker by loop.create_task
		# when the loop starts running, the worker would also be established

	# set to a given number of workers
	async def _set_worker_count(self, count):
		if (count > self.max_size):					# alaming the attempt of overexpanding
			logging.warning(f"{self._name} max size exceed, set to max size {self.max_size}")
		self.size = min(count, self.max_size)		# fix to max size

		if self.worker_count > self.size:	# close some workers
			for _ in range(self.worker_count - self.size):
				await self.Q.put("ExitMessage") # send ExitMessage's until the size is equal
		else:								# create some workers
			for _ in range(self.size - self.worker_count):
				self._add_worker()			# repeat add_worker function
		await self.Q.join()					# wait for all task to complete
	def set_worker_count(self, count):
		self._loop.run_until_complete(self._set_worker_count(count))
		return self.worker_count

	def start(self, start_size = 1):
		#tracemalloc.start() 		# debug trace
		#tracemalloc.clear_traces()	# debug trace

		# prevent duplicate running pool
		try:
			assert(self.worker_count == None)
		except:
			logging.error("this pool had already started")
			return

		# if start_size = 0, ignore the expanding state and set to max
		if not start_size:	
			start_size = self.max_size	

		# initialize workers
		self.worker_count = 0 				
		self.worker_dict = {}			
		self.set_worker_count(start_size)	# wake up the starting workers

	async def _join(self):			# 將worker全部收回
		if not self.worker_count:	# 檢查running worker數量
			logging.error("this pool has no running worker")
			return 1 

		# ensure all tasks in queue are finished
		# 強制將queue裡面的東西取出，然後取消這些工作
		while(not self.Q.empty()):
			coro = self.Q.get_nowait()	# get_nowait 同步的將物件從queue取出，不會造成context switch
			coro.close()				# 關閉 awaitable 物件
			self.Q.task_done()			# 通知queue task完成

		# close all worker
		await self._set_worker_count(0)	# 送出ExitMessages
		# 確認所有worker都已經返回
		for worker in self.worker_dict.values():
			if not worker.done():
				await worker
		try: # check worker count
			assert(self.worker_count == 0)	# 確認沒東西在執行
			self.worker_count = None 		# reset objects
			self.worker_dict = None 
		except:
			logging.critical(f"{self._name} has some worker didn`t exit : {self.worker_count}")
			return 1

	def stop(self):
		## close loop
		if self._loop.is_running():
			self._loop.create_task(self._join()) 	# 將收集worker的動作排進event loop去執行
		else:
			self._loop.run_until_complete(self._join()) # 直接呼叫join

		# resource debugging
		#first_size, first_peak = tracemalloc.get_traced_memory() # trace
		#print(first  _size, first_peak) # trace

	async def _push_all(self, iterable):
		count = 0 # for debug
		try:
			while (True):	# 直到收到StopIteration訊號，把所有東西都enqueue進去
				future = next(iterable) 	# next 會從迭代器取出一個物件
				count += 1 # for debug
				await self.Q.put(future)	# Queue有大小上限，當Queue滿了且還沒收到完成訊號，put method會產生context switch
				# 若是無限制產生future物件並不會造成ＣＰＵ增漲（worker數量固定，同時在執行的future也是固定的）
				# 但利用queue限制物件生成數量可以給memory usage一個上限，不會因為探針數量增長而增加memory用量
		except StopIteration: # 正常結束
			pass
		except Exception as e:
			logging.error(f"{self._name} push tasks failed\n{e}")
		logging.debug(f"{self._name} pushed {count} tasks")
		await self.Q.join()	# 等待剛剛enqueue的物件回報完成，再結束_push_all

	def push_all(self, iterable): # try not to creat too much trafic, so put in one by one
		self._loop.run_until_complete(self._push_all(iterable))

