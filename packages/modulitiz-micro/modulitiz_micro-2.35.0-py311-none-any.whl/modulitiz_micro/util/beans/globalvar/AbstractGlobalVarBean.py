from abc import ABC
from typing import NewType

from modulitiz_micro.ModuloDate import ModuloDate
from modulitiz_micro.files.ModuloLogging import ModuloLogging
from modulitiz_micro.sistema.ModuloSystem import ModuloSystem
from modulitiz_micro.util.beans.conf.AbstractConfBean import AbstractConfBean


class AbstractGlobalVarBean(ABC):
	"""
	Classe da usare come base per definire la struttura di una classe che raggrupperà gli oggetti che verranno usati nel programma
	"""
	
	def __init__(self,confBean:NewType("T",AbstractConfBean),projectTitle:str,projectVersion:str,projectStartYear:int,isDebug:bool|None):
		self.confBean=confBean
		self.projectTitle=projectTitle
		self.projectVersion=projectVersion
		self.projectStartYear=projectStartYear
		
		self.projectHeader="%s V%s"%(projectTitle,projectVersion)
		
		if isDebug is None:
			isDebug=confBean.IS_DEBUG
		self.logger=ModuloLogging(cartellaBase=confBean.CARTELLA_BASE_PROGETTO,isDebug=isDebug)
		currentYear=ModuloDate.dateToString(None,"%Y")
		ModuloSystem.setTitoloFinestra(projectTitle)
		self.logger.info("""
############################################################
	%s - Since %d - Copyright %s
############################################################""",self.projectHeader,projectStartYear,currentYear)
		self.isRequestedStop=False
		self.isRequestedExit=False
	
