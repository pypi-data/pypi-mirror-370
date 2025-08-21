import re

from modulitiz_micro.ModuloStringhe import ModuloStringhe
from modulitiz_micro.files.ModuloFiles import ModuloFiles
from modulitiz_micro.util.pip.ModuloPip import ModuloPip


class ModuloToml(object):
	"""
	Operazioni sul file .toml
	"""
	REGEX_TOML_VERSION=r'version *= *"(%s)"'%(ModuloPip.REGEX_VERSION,)
	
	def __init__(self,nomefile:str):
		self.nomefile=nomefile
	
	def retrieveMinPyVersion(self)->str:
		output=self.__retrieveByRegex(r'python-tag* \= *"(py\d+)"')
		if output is None:
			return "py3"
		return output
	
	def retrieveVersion(self)->str|None:
		"""
		Recupera la versione di una wheel leggendo il file .toml
		"""
		return self.__retrieveByRegex(self.REGEX_TOML_VERSION)
	
	def updateVersion(self,version:str):
		cont=ModuloStringhe.normalizzaEol(ModuloFiles.readFileText(self.nomefile,True))
		cont=re.sub(self.REGEX_TOML_VERSION,r'version = "%s"'%(version,),cont)
		with ModuloFiles.open(self.nomefile,'wt') as fp:
			fp.write(cont)
	
	def __retrieveByRegex(self,regex:str)->str|None:
		cont=ModuloFiles.readFileText(self.nomefile,True)
		ricerca=re.search(regex,cont)
		if ricerca is None:
			return None
		return ricerca.group(1)
