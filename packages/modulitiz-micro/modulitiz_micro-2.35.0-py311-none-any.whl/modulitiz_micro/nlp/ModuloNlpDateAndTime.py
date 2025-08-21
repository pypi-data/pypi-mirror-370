from modulitiz_micro.ModuloDate import ModuloDate
from modulitiz_micro.ModuloNumeri import ModuloNumeri
from modulitiz_micro.nlp.ModuloNlp import ModuloNlp


class ModuloNlpDateAndTime(object):
	@staticmethod
	def dateToString(data,anno:str)->str:
		dataStr=ModuloDate.dateToString(data,"%w %A %d %B")
		numGiornoSett,giornoSett,giorno,mese=dataStr.split(" ")
		# sistemo grammaticalmente gli articoli, verbi, ...
		numGiornoSett=int(numGiornoSett)
		giorno=int(giorno)
		articoloGiornoMese="il "
		giornoParola=giorno
		if giorno in (1,8,11):
			articoloGiornoMese="l'"
			giornoParola=ModuloNumeri.numberToWord(giorno)
		verbo=ModuloNlp.verboEssere(data<ModuloDate.now())
		articoloGiornoSett=ModuloNlp.articolo(False,numGiornoSett!=0)
		output=f"{articoloGiornoMese}{giornoParola} {mese}{anno} {verbo} {articoloGiornoSett} {giornoSett}"
		output=output.lower()
		return output
	
	@classmethod
	def minutesToTimeRelative(cls,minutes:int,arrotonda:bool)->str:
		prefixTempo=""
		minutes,hoursDiff,hoursWord=cls.__minutesToHours(minutes)
		# minuti
		minutesWord=minutes
		if minutes==1:
			minutesWord="un"
		elif 10<minutes<60:
			if arrotonda is True and minutes%10!=0:
				prefixTempo=" circa"
				minutes=round(minutes,-1)
			minutesWord=minutes
		output="Fino a"+prefixTempo
		if hoursDiff>0:
			output+=" %s or%s"%(hoursWord,("a" if hoursDiff==1 else "e"))
			if minutes>0:
				output+=" e"
		if minutes>0:
			output+=" %s minut%s"%(minutesWord,("o" if minutes==1 else "i"))
		return output
	
	@staticmethod
	def __minutesToHours(minutes:int)->tuple:
		hoursDiff=0
		hoursWord=""
		if minutes<60:
			return minutes,hoursDiff,hoursWord
		hoursDiff=minutes//60
		minutes=minutes%60
		if hoursDiff==1:
			hoursWord="un"
		else:
			hoursWord=hoursDiff
		return minutes,hoursDiff,hoursWord
