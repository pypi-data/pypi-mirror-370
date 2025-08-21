import os
import shutil

from modulitiz_micro.ModuloColorText import ModuloColorText
from modulitiz_micro.ModuloListe import ModuloListe
from modulitiz_micro.files.ModuloFiles import ModuloFiles
from modulitiz_micro.sistema.ModuloSystem import ModuloSystem
from modulitiz_micro.util.wheel.ModuloCheckTestNamingConvention import ModuloCheckTestNamingConvention
from modulitiz_micro.util.wheel.ModuloToml import ModuloToml


class ModuloBuildWheel(object):
	CMD_PYTHON="python"
	PATTERN_NOMEFILE_WHEEL="{}-{}-{}-none-any.whl"
	
	def __init__(self,moduleName:str,percorsoFileMain:str):
		self.moduleName=moduleName
		
		self.percorsoCartellaSource=os.path.dirname(percorsoFileMain)
		self.percorsoCartellaRoot=os.path.dirname(self.percorsoCartellaSource)
		self.skipUnitTest=False
		
		self.moduloToml=ModuloToml("pyproject.toml")
		self.moduloTestNamingConventions=ModuloCheckTestNamingConvention(moduleName,self.percorsoCartellaSource)
		self.versionOld=None
		self.versionNew=None
		self.filenameWheel=None
	
	def doWork(self):
		self.versionOld=self.moduloToml.retrieveVersion()
		self.skipUnitTest=input("Skip unit test? y, n (default = n):")=='y'
		# ask which version should be incremented (major, minor, bug fix)
		versionType=input("Which version increment? 1=major, 2=minor, 3=bug fix (default = 2):")
		if versionType=="":
			versionType=2
		else:
			versionType=int(versionType)
		# compute next version
		self.__computeVersionNew(versionType)
		# printing info
		msg=f"Build {self.moduleName} {self.versionNew}"
		ModuloSystem.setTitoloFinestra(msg)
		print("""{}
		============================================================
				{} (from version {})
		============================================================
		{}""".format(ModuloColorText.GRASSETTO,msg,self.versionOld,ModuloColorText.DEFAULT))
		# change dir
		os.chdir(self.percorsoCartellaSource)
		if self.__doUnitTests() is True:
			return
		# aggiorno versione
		self.moduloToml.updateVersion(self.versionNew)
		# building wheel
		ModuloSystem.systemCallPrintOutput(f'{self.CMD_PYTHON} -m pip install -U build twine==6.0.1',None)
		print()
		percorsoCartellaOut=ModuloFiles.pathJoin(self.percorsoCartellaRoot,"wheel")
		cmd='{} -m build --wheel --outdir "{}"'.format(self.CMD_PYTHON,percorsoCartellaOut)
		ModuloSystem.systemCallPrintOutput(cmd,None)
		# deleting temporary dirs
		print()
		shutil.rmtree(ModuloFiles.pathJoin(self.percorsoCartellaSource,"build"))
		shutil.rmtree(ModuloFiles.pathJoin(self.percorsoCartellaSource,self.moduleName+".egg-info"))
		# install wheel
		self.filenameWheel=self.PATTERN_NOMEFILE_WHEEL.format(self.moduleName,self.versionNew,self.moduloToml.retrieveMinPyVersion())
		percorsoWheel=ModuloFiles.pathJoin(percorsoCartellaOut,self.filenameWheel)
		cmd='{} -m pip install -U "{}"'.format(self.CMD_PYTHON,percorsoWheel)
		ModuloSystem.systemCallPrintOutput(cmd,None)
		print()
		print("Uploading to Pypi")
		cmd='{} -m twine upload "{}"'.format(self.CMD_PYTHON,percorsoWheel)
		ModuloSystem.systemCallPrintOutput(cmd,None)
		# delete wheel
		os.remove(percorsoWheel)
	
	def __doUnitTests(self) -> bool:
		if self.skipUnitTest:
			return False
		nomefileTest=ModuloFiles.pathJoin(self.percorsoCartellaSource,"test/TestMain.py")
		print("Check file and class naming conventions...")
		errors=self.moduloTestNamingConventions.doWork()
		if not ModuloListe.isEmpty(errors):
			errorsCount=len(errors)
			print("There %s %d error%s:"%("are" if errorsCount>1 else "is",errorsCount,"s" if errorsCount>1 else ""))
			for error in errors:
				print(error)
			return True
		print("Starting tests...")
		cmd='%s "%s"'%(self.CMD_PYTHON,nomefileTest)
		rows=[]
		for row in ModuloSystem.systemCallYieldOutput(cmd,None):
			print("%s>>>%s %s"%(ModuloColorText.BLU,ModuloColorText.DEFAULT,row))
			rows.append(row)
		rows=reversed(rows[-10:])
		rows=[x.strip() for x in rows]
		rows=[x if x!="" and x!=ModuloColorText.DEFAULT else None for x in rows]
		rows=ModuloListe.eliminaElementiVuoti(rows)
		lastRow=rows[0]
		PATTERN_TO_PRINT="""{}
	==================================================
			{}
	==================================================
	"""+ModuloColorText.DEFAULT
		if lastRow!="OK":
			print(PATTERN_TO_PRINT.format(ModuloColorText.ROSSO,"Errors during tests execution"))
			return True
		print(PATTERN_TO_PRINT.format(ModuloColorText.VERDE,"Tests completed successfully"))
		return False
	
	def __computeVersionNew(self,versionType:int):
		arr=[int(x) for x in self.versionOld.split(".")]
		arr[versionType-1]+=1
		if versionType!=len(arr):
			for i in range(versionType,len(arr)):
				arr[i]=0
		arr=[str(x) for x in arr]
		self.versionNew=".".join(arr)
