import os
import zipfile

from modulitiz_micro.ModuloStringhe import ModuloStringhe
from modulitiz_micro.files.ModuloFiles import ModuloFiles


class ModuloZip(object):
	
	@classmethod
	def zip(cls,dirIn: str,fileOut: str,includeRootDir: bool):
		fh=zipfile.ZipFile(fileOut,'w',zipfile.ZIP_DEFLATED)
		if not os.path.isfile(dirIn):
			cls.__fromFolder(fh,dirIn,includeRootDir)
		else:
			fh.write(dirIn)
		fh.close()
	
	@staticmethod
	def unzip(fileIn: str,dirOut: str|None = None):
		if dirOut is None:
			dirOut="./"
		elif dirOut=="":
			dirOut=fileIn.split("/")[-1].split(".")[0]
		zipRef=zipfile.ZipFile(fileIn,'r')
		zipRef.extractall(dirOut)
		zipRef.close()
	
	@staticmethod
	def __fromFolder(fh,dirIn: str,includeRootDir: bool):
		pathOutRootRel=os.path.basename(dirIn) if includeRootDir else ""
		for pathRel,pathAbs,dirs,nomefiles in ModuloFiles.walk(dirIn,(),(),None,None):
			# controllo se devo scrivere anche la cartella principale
			if not ModuloStringhe.isEmpty(pathOutRootRel):
				pathOutRel=ModuloFiles.pathJoin(pathOutRootRel,pathRel)
				fh.write(pathAbs,pathOutRel)
			else:
				pathOutRel=pathRel
			for nomefile in nomefiles:
				percorsoFile=ModuloFiles.pathJoin(pathAbs,nomefile)
				percorsoFileRel=ModuloFiles.pathJoin(pathOutRel,nomefile)
				fh.write(percorsoFile,percorsoFileRel)
