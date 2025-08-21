import threading


class QueueBean(object):
	def __init__(self):
		self.lock=threading.Lock()
		self.size=0
		self.countConsecutiveOverSize=0
