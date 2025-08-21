import threading


class ModuloThreadWithCallbackError(threading.Thread):
	"""
	This class should always be used in preference to threading.Thread.

	The interface provided by this class is identical to that of threading.Thread,
	however, if an exception occurs in the thread the callback function is called,
	rather than printed to stderr.

	This is important in daemon style applications where stderr is redirected to /dev/null.
	"""
	
	def __init__(self,callbackError,**kwargs):
		super().__init__(**kwargs)
		self.callbackError=callbackError
		self._realRun=self.run
		self.run=self.__wrapRun
	
	def __wrapRun(self):
		try:
			self._realRun()
		except Exception as ex:
			self.callbackError(ex)
