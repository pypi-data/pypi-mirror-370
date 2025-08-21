from abc import ABC

from modulitiz_micro.eccezioni.EccezioneRuntime import EccezioneRuntime


class AbstractOverrideTestUtil(ABC):
	"""
	Solo le funzioni statiche devono essere revertate
	"""
	
	def __init__(self):
		super().__init__()
		self._cache={}
	
	def __enter__(self):
		self._cache.clear()
		return self
	
	def __exit__(self,*args,**kwargs):
		self._cache.clear()
	
	@staticmethod
	def getMockedFunction(throwExc:Exception|None,expectedValue: str|tuple|None):
		"""
		Must use only 1 param.
		"""
		if throwExc is not None:
			return lambda *args,**kwargs:(_ for _ in ()).throw(throwExc)
		elif expectedValue is not None:
			return lambda *args,**kwargs:expectedValue
		raise EccezioneRuntime("Use only 1 param")
