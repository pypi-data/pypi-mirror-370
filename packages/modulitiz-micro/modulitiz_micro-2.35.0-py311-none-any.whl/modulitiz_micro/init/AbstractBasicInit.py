from abc import ABC
from abc import abstractmethod

from modulitiz_micro.init.AbstractInit import AbstractInit


class AbstractBasicInit(AbstractInit,ABC):
	@classmethod
	@abstractmethod
	def getCartellaBase(cls)->str:
		"""
		Ricavo la cartella dell'archivio del progetto attuale.
		"""
	
	@classmethod
	@abstractmethod
	def getProjectRoot(cls,nome: str) -> str:
		"""
		Restituisce il percorso assoluto di un progetto.
		"""
	
	@classmethod
	@abstractmethod
	def getProjectsRoot(cls) -> str:
		"""
		Restituisce il percorso assoluto dei progetti.
		"""
