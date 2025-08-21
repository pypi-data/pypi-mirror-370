import json
from abc import ABC

from modulitiz_micro.files.ModuloFiles import ModuloFiles


class AbstractFileConfBean(ABC):
	"""
	Classe che può essere usata come base per definire la struttura del file di configurazione del programma
	"""
	
	def __init__(self,nomefile:str):
		self._diz=json.loads(ModuloFiles.readFileText(nomefile,True))
