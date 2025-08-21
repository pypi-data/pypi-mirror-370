import logging
import os
import sys

from modulitiz_micro.ModuloDate import ModuloDate
from modulitiz_micro.files.ModuloFiles import ModuloFiles


class ModuloLogging(logging.Logger):
	CARTELLA_LOG="logs"
	NOMEFILE_PREFIX="log"
	NOMEFILE_EXT=".txt"
	# dimensione massima del file di log in byte
	MAX_FILE_SIZE=10*1024*1024
	
	def __init__(self,nomefileFullPath:str|None=None,cartellaBase:str|None=None,isDebug:bool=False):
		super().__init__("modulitiz")
		logFormatterConsole = self.__getOutputFormatter(False)
		logLevel=logging.INFO if not isDebug else logging.DEBUG
		# imposto livello
		self.setLevel(logLevel)
		# creo console logger
		consoleHandler=logging.StreamHandler(sys.stdout)
		consoleHandler.setLevel(logLevel)
		consoleHandler.setFormatter(logFormatterConsole)
		self.addHandler(consoleHandler)
		# creo file logger
		self.__addFileHandler(nomefileFullPath,cartellaBase,isDebug)
	
	def close(self):
		self.handlers.clear()
	
	@staticmethod
	def exceptionToString(eccezione)->str:
		formatter=logging.Formatter()
		lastEccezione=sys.exc_info()
		try:
			msg=formatter.formatException(eccezione)
		except TypeError:
			msg=formatter.formatException(lastEccezione)
		return msg
	
	@staticmethod
	def __getOutputFormatter(isDebug:bool)->logging.Formatter:
		formato='%(asctime)s '+('[%(filename)s:%(lineno)s]\t' if isDebug is True else '')+'[%(levelname)s]\t%(message)s'
		return logging.Formatter(formato)
	
	def __addFileHandler(self,nomefileFullPath:str|None,cartellaBase:str|None,isDebug:bool):
		# controllo se loggare anche su file
		if nomefileFullPath is None and cartellaBase is None:
			return
		# controllo che la cartella dei log esista
		if cartellaBase is None:
			cartellaBase=self.CARTELLA_LOG
		else:
			cartellaBase=ModuloFiles.pathJoin(cartellaBase,self.CARTELLA_LOG)
		if not os.path.exists(cartellaBase):
			os.makedirs(cartellaBase,exist_ok=True)
		
		# creo il nome del file
		if nomefileFullPath is None:
			nomefileFullPath=ModuloFiles.pathJoin(cartellaBase,self.NOMEFILE_PREFIX+self.NOMEFILE_EXT)
		# se il file e' troppo grande ne creo uno nuovo
		if ModuloFiles.getFileSize(nomefileFullPath)>=self.MAX_FILE_SIZE:
			os.rename(nomefileFullPath,nomefileFullPath+"_"+ModuloDate.dateToString(None,ModuloDate.FORMATO_DATA_ORA_NOMEFILE))
		# file handler
		fileHandler=logging.FileHandler(nomefileFullPath)
		fileHandler.setFormatter(self.__getOutputFormatter(isDebug))
		self.addHandler(fileHandler)
