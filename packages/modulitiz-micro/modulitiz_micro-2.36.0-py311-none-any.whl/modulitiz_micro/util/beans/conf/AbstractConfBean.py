from abc import ABC

from modulitiz_micro.ModuloPyinstaller import ModuloPyinstaller
from modulitiz_micro.files.ModuloFiles import ModuloFiles
from modulitiz_micro.sistema.EnvVarsEnum import EnvVarsEnum
from modulitiz_micro.sistema.ModuloEnvVars import ModuloEnvVars


class AbstractConfBean(ABC):
	
	def __init__(self,cartellaBase:str|None,nomeProgetto:str):
		self.CARTELLA_BASE_PROGETTO:str|None=None
		if cartellaBase is not None:
			self.CARTELLA_BASE_PROGETTO=ModuloFiles.pathJoin(cartellaBase,nomeProgetto)
		self.IS_DEBUG=(ModuloEnvVars.getOrNone(EnvVarsEnum.MODULITIZ_IS_DEBUG)=="1" and not ModuloPyinstaller.isExecutableMode())
		self.NOME_PROGETTO=nomeProgetto
