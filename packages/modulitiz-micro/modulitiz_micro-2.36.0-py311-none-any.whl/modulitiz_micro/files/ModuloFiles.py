import glob
import os
import shutil

from modulitiz_micro.ModuloDate import ModuloDate
from modulitiz_micro.ModuloListe import ModuloListe
from modulitiz_micro.ModuloStringhe import ModuloStringhe
from modulitiz_micro.eccezioni.EccezioneRuntime import EccezioneRuntime


class ModuloFiles(object):
	@staticmethod
	def open(*args,**kwargs):
		return open(newline="\n",*args,**kwargs)
	
	@classmethod
	def readFileBinary(cls,filename:str)->str:
		"""
		Convert digital data to binary format
		Puo' essere usato, ad esempio, per inserire un file di tipo BLOB su sqlite
		"""
		return cls.readFile(filename,'rb',None)
	@classmethod
	def readFileText(cls,filename:str,useUtf8:bool|None)->str:
		return cls.readFile(filename,'rt',useUtf8)
	@staticmethod
	def readFile(filename:str,mode:str,useUtf8:bool|None):
		codifica=None
		if useUtf8 is not None:
			if useUtf8 is True:
				codifica=ModuloStringhe.CODIFICA_UTF8
			else:
				codifica='latin-1'
		with open(filename,mode,encoding=codifica) as fp:
			cont=fp.read()
		return cont

	@staticmethod
	def getFileSize(nomefile:str)->int:
		"""
		Se non trova nessun file ritorna -1
		"""
		try:
			statinfo=os.stat(nomefile)
			return statinfo.st_size
		except FileNotFoundError:
			return -1

	@classmethod
	def getFolderSize(cls, path:str)->int:
		if not os.path.exists(path) or os.path.isfile(path):
			return -1
		count=0
		for root,dirs,filenames in os.walk(path):
			for filename in filenames:
				count+=cls.getFileSize(os.path.join(root,filename))
		return count
	
	@staticmethod
	def getTimestampUtcUltimaModifica(nomefile:str)->int:
		return int(os.path.getmtime(nomefile))

	@staticmethod
	def normalizzaSlashPath(percorso:str)->str:
		percorso=os.path.normpath(percorso)
		return percorso.replace("\\","/")

	@classmethod
	def pathJoin(cls,path1:str|None,path2:str|None)->str|None:
		if ModuloStringhe.isEmpty(path1):
			return path2
		if ModuloStringhe.isEmpty(path2):
			return path1
		# normalizzazione
		path1=cls.normalizzaSlashPath(path1)
		path2=cls.normalizzaSlashPath(path2)
		# concatenazione
		path=os.path.join(path1,path2)
		path=cls.normalizzaSlashPath(path)
		return path

	@classmethod
	def pathAbsToRel(cls,percorso:str,root:str):
		percorso=percorso.replace(root,"")
		percorso=cls.normalizzaSlashPath(percorso)
		if percorso.startswith("/"):
			percorso=percorso[1:]
		return percorso

	@staticmethod
	def normalizzaPercorsoLocale(percorso:str):
		percorso=os.path.normpath(os.path.abspath(percorso))
		return percorso
	@classmethod
	def normalizzaPercorsoRemoto(cls,percorso:str):
		return cls.normalizzaSlashPath(percorso)

	@classmethod
	def rinominaConTimestamp(cls,nomefile:str):
		nomefileSenzaEstensione,ext=cls.getBaseFileNameAndExtension(nomefile)
		nomefileNew=nomefileSenzaEstensione+"_"+ModuloDate.dateToString(None, ModuloDate.FORMATO_DATA_ORA_NOMEFILE)+ext
		os.rename(nomefile,nomefileNew)

	@staticmethod
	def sposta(sourceFilename:str,destFilename:str):
		shutil.move(sourceFilename,destFilename)

	@staticmethod
	def copia(sourceFilename:str,destFilename:str):
		try:
			shutil.copy2(sourceFilename,destFilename)
		except Exception:
			raise EccezioneRuntime("Errore copia file "+sourceFilename+" in "+destFilename)

	@classmethod
	def eliminaContenutoCartella(cls,percorso:str):
		"""
		elimina tutto il contenuto di una cartella ma non la cartella
		"""
		for root,dirs,nomefiles in os.walk(percorso):
			for nomefile in nomefiles:
				os.unlink(cls.pathJoin(root, nomefile))
			for cartella in dirs:
				shutil.rmtree(cls.pathJoin(root, cartella))

	@staticmethod
	def deleteByPattern(pattern:str):
		filesDaElim=glob.glob(pattern)
		for fileDaElim in filesDaElim:
			os.remove(fileDaElim)

	@staticmethod
	def getBaseFileNameAndExtension(nomefile:str)->tuple:
		arr=nomefile.split(".")
		nomefileSenzaEstensione=".".join(arr[0:-1])
		ext="."+arr[-1]
		return nomefileSenzaEstensione,ext

	@classmethod
	def walk(cls,root:str,excludeFiles:list|tuple,excludeDirs:list|tuple,minByteSize:int|None,maxByteSize:int|None):
		"""
		Questa funzione e' uguale a os.walk() ma restituisce anche il path relativo oltre a quello assoluto.
		"""
		root=cls.normalizzaPercorsoLocale(root)
		for result in os.walk(root):
			yield from cls.__walk(root,excludeFiles,excludeDirs,minByteSize,maxByteSize,result)
			
	@classmethod
	def __walk(cls,root: str,excludeFiles: list|tuple,excludeDirs: list|tuple,minByteSize: int|None,maxByteSize: int|None,
			result:tuple[str, list[str], list[str]]):
		percorso,dirs,nomefiles=result
		percorsoRel=cls.pathAbsToRel(percorso,root)
		# elaboro i file
		for index,nomefile in enumerate(nomefiles):
			nomefileRelPath=cls.pathJoin(percorsoRel,nomefile)
			# escludo i file che sono nella blacklist
			if nomefileRelPath in excludeFiles:
				nomefiles[index]=""
				continue
			# controllo dimensione file
			if maxByteSize is not None or minByteSize is not None:
				bytesFile=cls.getFileSize(cls.pathJoin(root,nomefileRelPath))
				if(maxByteSize is not None and bytesFile>maxByteSize) or (minByteSize is not None and bytesFile<minByteSize):
					nomefiles[index]=""
		nomefiles=ModuloListe.eliminaElementiVuoti(nomefiles)
		#elaboro le cartelle
		for index,cartella in enumerate(dirs):
			cartellaRelPath=cls.normalizzaPercorsoRemoto(cls.pathJoin(percorsoRel,cartella))
			#escludo le cartelle che sono nella blacklist
			if cartellaRelPath in excludeDirs:
				dirs[index]=""
		dirs=ModuloListe.eliminaElementiVuoti(dirs)
		yield percorsoRel,percorso,dirs,nomefiles
