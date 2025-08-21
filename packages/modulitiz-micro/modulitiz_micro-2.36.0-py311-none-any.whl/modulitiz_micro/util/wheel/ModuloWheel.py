import importlib.metadata

class ModuloWheel(object):
	
	def __init__(self,modulo):
		self.__modulo=modulo
	
	def retrieveVersion(self)->str:
		"""
		Recupera la versione di una wheel, indipendentemente in che modo sia costruita (.toml, setup.py, poetry, ...)
		"""
		return importlib.metadata.version(self.__modulo.__name__)
