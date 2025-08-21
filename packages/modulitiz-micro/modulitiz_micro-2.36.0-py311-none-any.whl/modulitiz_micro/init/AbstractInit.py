from abc import ABC
from abc import abstractmethod


class AbstractInit(ABC):
	@staticmethod
	@abstractmethod
	def getCartellaScriptCorrente(cls)->str:
		"""
		Come recuperare la cartella dello script corrente.
		"""
