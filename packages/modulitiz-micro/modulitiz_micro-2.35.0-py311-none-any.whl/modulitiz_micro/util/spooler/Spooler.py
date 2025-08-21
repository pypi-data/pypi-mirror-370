import time

from modulitiz_micro.util.spooler.AbstractSpooler import AbstractSpooler
from modulitiz_micro.util.spooler.beans.QueueBean import QueueBean


class Spooler(AbstractSpooler):
	@staticmethod
	def increaseSize(bean:QueueBean):
		bean.size+=1
	@staticmethod
	def decreaseSize(bean:QueueBean):
		bean.size-=1
	
	@classmethod
	def waitUntilJobsDone(cls):
		while cls._areJobsNotDone():
			time.sleep(0.1)
