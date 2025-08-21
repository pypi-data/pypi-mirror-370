import getpass
import os
import platform
import signal
import subprocess
import sys
from typing import Callable

import psutil

from modulitiz_micro.ModuloColorText import ModuloColorText
from modulitiz_micro.ModuloFunzioni import ModuloFunzioni
from modulitiz_micro.ModuloListe import ModuloListe
from modulitiz_micro.ModuloStringhe import ModuloStringhe
from modulitiz_micro.eccezioni.EccezioneRuntime import EccezioneRuntime
from modulitiz_micro.eccezioni.EccezioneSoNonSupportato import EccezioneSoNonSupportato
from modulitiz_micro.sistema.EnvVarsEnum import EnvVarsEnum


class ModuloSystem(object):
	ESTENSIONI_POTENZIALMENTE_ESEGUIBILI=(".exe",".msi",".cmd",".bat",".vbs")
	
	CODIFICA_WINDOWS_CMD='cp437'
	
	CMD_PAUSE=r'''python -c "input('pause:')"'''
	WINDOWS_PATTERN_ECHO="""echo|set /p="{}" & echo."""
	
	@classmethod
	def handleCtrlC(cls,handler:Callable=None):
		cls.handleEvent(handler, signal.SIGINT)
	@classmethod
	def handleEvent(cls,handler:Callable=None,signalType=None):
		if handler is None:
			handler=cls.__signalHandler
		signal.signal(signalType,handler)

	@staticmethod
	def __signalHandler(_signalType, _frame):
		print("\nUscita...")
		sys.exit(0)

	@staticmethod
	def sendCtrlcProcessChilds(ppid:int):
		try:
			parent = psutil.Process(ppid)
		except psutil.NoSuchProcess:
			return
		children = parent.children(recursive=True)
		for process in children:
			ModuloSystem.sendCtrlcProcess(process.pid)

	@staticmethod
	def sendCtrlcProcess(pid:int):
		if pid<=0:
			raise EccezioneRuntime("Il pid deve essere maggiore di 0")
		if ModuloSystem.isWindows():
			segnale=signal.CTRL_C_EVENT
		else:
			segnale=signal.SIGINT
		os.kill(pid,segnale)
	
	
	@classmethod
	def systemCallCallbackOutput(cls,cmd:str, callbackOutput:Callable,codifica:str|None):
		for riga in cls.systemCallYieldOutput(cmd,codifica):
			callbackOutput(riga)
	@classmethod
	def systemCallPrintOutput(cls,cmd: str,codifica: str|None):
		for riga in cls.systemCallYieldOutput(cmd,codifica):
			print(">>> "+riga)
	
	@classmethod
	def systemCallPrintOutputColor(cls,cmd: str,codifica: str|None):
		for riga in cls.systemCallYieldOutput(cmd,codifica):
			print("%s>>>%s %s"%(ModuloColorText.BLU,ModuloColorText.DEFAULT,riga))
	
	@classmethod
	def systemCallYieldOutput(cls,cmd:str, codifica:str|None):
		if codifica is None:
			codifica=cls.CODIFICA_WINDOWS_CMD
		with cls.systemCall(cmd,True) as pipe:
			# scorro l'output
			for line in iter(pipe.stdout.readline,b''):
				rigaDecoded=line.decode(codifica,'replace').rstrip()
				yield rigaDecoded
	
	@classmethod
	def systemCallReturnOutput(cls,cmd: str,codifica: str|None) -> str|None:
		if codifica is None:
			codifica=cls.CODIFICA_WINDOWS_CMD
		with cls.systemCall(cmd,True) as pipe:
			output=cls.fromPipeToString(pipe,None,codifica)
		return output
	
	@classmethod
	def systemCall(cls,cmd:str, useStdOut:bool)->subprocess.Popen:
		"""
		useStdOut		se mostrare o meno l'output a schermo
		"""
		if useStdOut is True:
			stdOut=subprocess.PIPE
		else:
			stdOut=subprocess.DEVNULL
		# sistemo variabili ambiente
		envVars=os.environ
		if not cls.isWindows():
			originalCommand=envVars.get("_",None)
			if originalCommand is not None:
				originalCommand=os.path.dirname(originalCommand)
				envVarPath=envVars[EnvVarsEnum.PATH]
				if originalCommand+":" not in envVarPath or ":"+originalCommand not in envVarPath or ":"+originalCommand+":" not in envVarPath:
					envVars[EnvVarsEnum.PATH]=originalCommand+":"+envVarPath
		# se ci sono piu' comandi separati li eseguo insieme
		righe=ModuloListe.eliminaElementiVuoti(ModuloStringhe.normalizzaEol(cmd).split("\n"))
		cmdFinal=" && ".join(righe)
		# creo l'oggetto
		pipe=subprocess.Popen(cmdFinal,shell=True,
			stdin=subprocess.PIPE,
			stdout=stdOut,
			stderr=subprocess.STDOUT,
			cwd=os.getcwd(), env=envVars)
		return pipe
	
	@classmethod
	def systemCallWaitAndClose(cls,cmd: str,useStdOut: bool):
		with cls.systemCall(cmd,useStdOut) as pipe:
			pipe.wait()
	
	@classmethod
	def fromPipeToString(cls,pipe: subprocess.Popen,stdinData:bytes|None,codifica:str|None)->str|None:
		if codifica is None:
			codifica=cls.CODIFICA_WINDOWS_CMD
		# chiedo i dati
		output=pipe.communicate(stdinData)[0]
		if output is None:
			return None
		output=output.decode(codifica,'replace')
		return output
	
	@staticmethod
	def stdinReadMultipleLines(numLinesEmptyToExit:int=2)->list:
		countLinesEmpty=0
		output=[]
		while True:
			line=sys.stdin.readline().rstrip("\n")
			if line=='':
				countLinesEmpty+=1
				if countLinesEmpty==numLinesEmptyToExit:
					break
			else:
				countLinesEmpty=0
			output.append(line)
		return output
	
	@classmethod
	def setTitoloFinestra(cls,titolo:str):
		if not cls.isWindows():
			return
		# preparo il comando
		cmd="title "+titolo
		#invio il comando
		cls.systemCallWaitAndClose(cmd,False)
	

	@staticmethod
	def pause():
		input("Premere il tasto INVIO per continuare...")

	@staticmethod
	def getHostname()->str:
		return platform.node()
	@staticmethod
	def getUsername()->str:
		return getpass.getuser()

	@staticmethod
	def getCmdSleep()->str:
		if ModuloSystem.isWindows():
			return "timeout "
		return "sleep "

	@staticmethod
	def getTempFolder()->str:
		if ModuloSystem.isWindows():
			return os.environ[EnvVarsEnum.TMP]
		return "/tmp"
	
	@staticmethod
	def getFolderNull()->str:
		if ModuloSystem.isWindows():
			return 'NUL'
		return "/dev/null"
	
	@staticmethod
	def isWindows()->bool:
		return os.name=='nt'

	@staticmethod
	def isSystem64bit()->bool:
		return sys.maxsize > 2**32

	@classmethod
	def shutdown(cls,delay:int=30):
		if cls.isWindows():
			cmd='{} {} && shutdown /p'
		else:
			cmd='{} {} && systemctl poweroff'
		cmd=cmd.format(cls.getCmdSleep(),delay)
		# in questo caso la pipe deve restare aperta
		cls.systemCall(cmd,True)
	@classmethod
	def reboot(cls,delay:int=30):
		if cls.isWindows():
			cmd='{} {} && shutdown /r'
		else:
			cmd='{} {} && reboot now'
		cmd=cmd.format(cls.getCmdSleep(),delay)
		# in questo caso la pipe deve restare aperta
		cls.systemCall(cmd,True)
	
	@staticmethod
	def findPidByName(nomeExe:str)->int|None:
		process=ModuloSystem.findProcessByName(nomeExe)
		if process is None:
			return None
		return process.pid

	@staticmethod
	def findProcessByName(nomeExe:str)->psutil.Process|None:
		for p in psutil.process_iter():
			currentName=""
			currentCmdLine=""
			currentNomeExe=""
			try:
				currentName = p.name()
				currentCmdLine=" ".join(p.cmdline())
				currentNomeExe = p.exe()
			except (psutil.AccessDenied, psutil.ZombieProcess, SystemError):
				pass
			except psutil.NoSuchProcess:
				continue
			if ModuloStringhe.contains(currentName,nomeExe) or ModuloStringhe.contains(currentCmdLine,nomeExe) or os.path.basename(currentNomeExe) == nomeExe:
				return p

	@classmethod
	def isAptPackageInstalled(cls,nome:str)->bool:
		if cls.isWindows():
			raise EccezioneSoNonSupportato("Windows non supportato")
		cmd=fr'''apt list --installed | grep {nome}/'''
		output=cls.systemCallReturnOutput(cmd,None)
		righe=ModuloStringhe.normalizzaEol(output).split("\n")
		righe=ModuloListe.eliminaElementiVuoti(righe)
		for riga in righe:
			if riga.startswith(nome):
				return True
		return False

	@staticmethod
	def getNumOfCores()->int:
		return os.cpu_count()

	@staticmethod
	def getLoadPerc()->float:
		"""
		Restituisce la percentuale di cpu utilizzata dall'ultima chiamata a questa funzione
		"""
		return psutil.cpu_percent()

	@classmethod
	def getLoadAveragesPerc(cls)->list:
		numCores=cls.getNumOfCores()
		lista=psutil.getloadavg()
		return [x/numCores*100 for x in lista]
	
	@classmethod
	def getTempCpu(cls)->list[tuple[str,int]]|None:
		"""
		funziona solo su linux, ritorna una mappa:
		nome sensore e valore sensore
		"""
		if cls.isWindows():
			return None
		sensors=psutil.sensors_temperatures(fahrenheit=False)
		sensor=ModuloFunzioni.dictGetFirstValue(sensors)
		lista=[]
		for valore in sensor:
			obj:psutil._common.shwtemp=valore
			lista.append((obj.label,int(obj.current)))
		return lista
	
	@staticmethod
	def getBattery()->tuple|None:
		battery=psutil.sensors_battery()
		if battery is None:
			return None
		percent=int(battery.percent)
		isPlugged=battery.power_plugged
		return percent,isPlugged
