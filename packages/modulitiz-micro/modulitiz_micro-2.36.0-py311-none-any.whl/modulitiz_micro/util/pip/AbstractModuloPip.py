import re
from abc import ABC

from modulitiz_micro.ModuloListe import ModuloListe
from modulitiz_micro.ModuloStringhe import ModuloStringhe
from modulitiz_micro.sistema.ModuloSystem import ModuloSystem


class AbstractModuloPip(ABC):
	REGEX_VERSION=r"\d+\.\d+\.\d+"
	_PREFIX_OK="Successfully installed "
	
	@classmethod
	def _versionFromFileRequirements(cls,rigaIn:str,args:str) -> list:
		cmd='pip index versions --pre %s %s'%(rigaIn,args)
		output=ModuloSystem.systemCallReturnOutput(cmd,None)
		righe=ModuloListe.eliminaElementiVuoti(ModuloStringhe.normalizzaEol(output).split("\n"))
		righe=cls._parseResults(righe)
		result=[]
		if len(righe)<3:
			return result
		
		result.append(cls._search(righe[-2],r"INSTALLED:\s+(%s)"))
		result.append(cls._search(righe[-1],r"LATEST:\s+(%s)"))
		return result
	
	@staticmethod
	def _parseResults(righe:list)->list:
		output=[]
		for riga in righe:
			riga=riga.strip()
			if not ModuloStringhe.isEmpty(riga) and not riga.startswith("["):
				output.append(riga)
		return output
	
	@classmethod
	def _search(cls,riga:str,regex:str)->str|None:
		ricerca=re.search(regex%(cls.REGEX_VERSION,),riga)
		if ricerca is None:
			return None
		return ricerca.group(1).strip()
