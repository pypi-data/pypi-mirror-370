import os
import sys

from modulitiz_micro.files.ModuloFiles import ModuloFiles


class ModuloPyinstaller(object):
	"""
	Utility di gestione del modulo che permette di compilare sorgenti e interprete in un file eseguibile unico (exe)
	"""
	
	@staticmethod
	def isExecutableMode()->bool:
		"""
		Identifica se lo script viene eseguito da un eseguibile o meno.
		"""
		return getattr(sys, 'frozen', False)
	
	@classmethod
	def cdProjectsDir(cls):
		"""
		Se questo metodo non viene chiamato da un eseguibile costruito con PyInstaller fa nulla,
		altrimenti cambia la cartella corrente alla root dei progetti.
		"""
		if cls.isExecutableMode() is False:
			return
		pathExecutableDir=os.path.dirname(sys.executable)
		originalPath=os.path.abspath(ModuloFiles.pathJoin(pathExecutableDir,"../"))
		os.chdir(originalPath)
