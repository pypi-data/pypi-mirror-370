import os.path
import re

from modulitiz_micro.ModuloFunzioni import ModuloFunzioni
from modulitiz_micro.ModuloListe import ModuloListe
from modulitiz_micro.ModuloStringhe import ModuloStringhe
from modulitiz_micro.files.ModuloFiles import ModuloFiles


class ModuloCheckTestNamingConvention(object):
	"""
	Checks if naming convention of test classes matches real source classes.
	"""
	EXCLUDE_DIRS=("testutil",)
	EXCLUDE_FILES=("TestMain.py",)
	
	def __init__(self,moduleName:str,pathSource:str):
		self.pathSource=ModuloFiles.pathJoin(pathSource,moduleName)
		self.pathTest=ModuloFiles.pathJoin(pathSource,"test")
		self.errors=[]
		self.__sourceFiles=[]
	
	def doWork(self)->list[str]:
		# check if paths exists
		self.__checkPath(self.pathSource)
		self.__checkPath(self.pathTest)
		# cache source files
		for rootRel,rootAbs,folders,filenames in ModuloFiles.walk(self.pathSource,(),self.EXCLUDE_DIRS,None,None):
			self.__sourceFiles.extend([ModuloFiles.pathJoin(rootRel,x) for x in filenames])
		self.__sourceFiles=[x for x in self.__sourceFiles if not ModuloStringhe.contains(x,"__pycache__")]
		# check every test file
		for rootRel,rootAbs,folders,filenames in ModuloFiles.walk(self.pathTest,self.EXCLUDE_FILES,self.EXCLUDE_DIRS,None,None):
			if not rootRel.endswith("__pycache__"):
				for filename in filenames:
					self.__checkFile(rootRel,rootAbs,filename)
		return self.errors
	
	def __checkPath(self,path:str):
		if os.path.exists(path):
			return
		self.errors.append("Path not exists: %s"%(path,))
	
	def __checkFile(self,rootRel:str,rootAbs:str,filename:str):
		filenameRel=ModuloFiles.pathJoin(rootRel,filename)
		filenameAbs=ModuloFiles.pathJoin(rootAbs,filename)
		isDecorator=ModuloStringhe.contains(rootRel,"decorators")
		# file name convention
		results=re.findall(r"[A-Z]\w+Test.py",filename)
		if ModuloListe.isEmpty(results):
			self.errors.append("File name not matching conventions: %s"%(filenameRel,))
			return
		# file name must match class name
		testClasses=ModuloFunzioni.getClassesFromFileSource(filenameAbs)
		if len(testClasses)>1:
			self.errors.append("File must not contain more than 1 class: %s"%(filenameRel,))
			return
		baseFilename=ModuloFiles.getBaseFileNameAndExtension(filename)[0]
		testClassName=None
		if not isDecorator:
			testClassName=testClasses[0]
			if testClassName!=baseFilename:
				self.errors.append("File and class names must be equals: %s"%(filenameRel,))
				return
		# test must follow source structure
		sourceFilenameRel=self.__getSourceFileNameFromTestFileName(rootRel,baseFilename,isDecorator)
		if sourceFilenameRel is None:
			self.errors.append("File doesn't match source dirs structure: %s"%(filenameRel,))
			return
		# source class name must equals class test
		if not isDecorator:
			sourceClassName=ModuloFunzioni.getClassesFromFileSource(ModuloFiles.pathJoin(self.pathSource,sourceFilenameRel))[0]
			if not testClassName.startswith(sourceClassName):
				self.errors.append("Test class name doesn't match source class name: %s"%(filenameRel,))
	
	def __getSourceFileNameFromTestFileName(self,rootRel:str,baseFilename:str,isDecorator:bool)-> str|None:
		partIncremental=""
		for part in re.findall(r'[A-Z](?:[a-z\d]+|[A-Z]*(?=[A-Z]|$))', baseFilename):
			partIncremental+=part
			partIncrementalToUse=partIncremental if not isDecorator else partIncremental[0].lower()+partIncremental[1:]
			filePathRel=ModuloFiles.pathJoin(rootRel,partIncrementalToUse)+".py"
			if filePathRel in self.__sourceFiles:
				return filePathRel
		return None
