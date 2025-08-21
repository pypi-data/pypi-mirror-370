from abc import ABC

from modulitiz_micro.util.spooler.beans.QueueBean import QueueBean


class AbstractSpooler(ABC):
	beans:dict[str,QueueBean]={}
	
	@classmethod
	def _areJobsNotDone(cls)->bool:
		for bean in cls.beans.values():
			if bean.size>0:
				return True
		return False
