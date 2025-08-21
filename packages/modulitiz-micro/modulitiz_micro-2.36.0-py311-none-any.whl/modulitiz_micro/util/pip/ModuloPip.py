from modulitiz_micro.ModuloListe import ModuloListe
from modulitiz_micro.ModuloStringhe import ModuloStringhe
from modulitiz_micro.files.ModuloFiles import ModuloFiles
from modulitiz_micro.sistema.ModuloSystem import ModuloSystem
from modulitiz_micro.util.pip.AbstractModuloPip import AbstractModuloPip


class ModuloPip(AbstractModuloPip):
	
	@classmethod
	def updateFromFileRequirements(cls,percorsoCartellaDipendenze: str) -> tuple[bool,str]:
		fileDipendenze=ModuloFiles.pathJoin(percorsoCartellaDipendenze,"requirements.txt")
		cmd='pip install -U -r "%s"'%(fileDipendenze,)
		output=ModuloSystem.systemCallReturnOutput(cmd,None)
		# check output
		righe=ModuloListe.eliminaElementiVuoti(ModuloStringhe.normalizzaEol(output).split("\n"))
		ultimeRigheReversed=righe[-10:]
		ultimeRigheReversed.reverse()
		isError=False
		for riga in ultimeRigheReversed:
			if riga.startswith(cls._PREFIX_OK):
				elencoModuliAggiornati=riga.replace(cls._PREFIX_OK,"")
				return True,elencoModuliAggiornati
			if not isError and (riga.startswith("ERROR:") or riga.startswith("Exception:")):
				isError=True
		if isError:
			msg="Aggiornamento moduli non riuscito:\n{}".format(output[-1000:])
			return False,msg
		return True," nessun aggiornamento"
	
	@classmethod
	def versionsFromFileRequirements(cls,percorsoCartellaDipendenze: str) -> list:
		fileDipendenze=ModuloFiles.pathJoin(percorsoCartellaDipendenze,"requirements.txt")
		if ModuloFiles.getFileSize(fileDipendenze)<=0:
			return []
		cont=ModuloStringhe.normalizzaEol(ModuloFiles.readFileText(fileDipendenze,None))
		righe=ModuloListe.eliminaElementiVuoti(cont.split("\n"))
		results=[]
		# memorizzo opzioni
		argsList=[]
		for riga in righe:
			if riga.startswith("-"):
				argsList.append(riga)
		args=" ".join(argsList)
		# elaboro ogni modulo
		for riga in righe:
			if not riga.startswith("-"):
				results.append(cls._versionFromFileRequirements(riga,args))
		return results
