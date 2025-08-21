import time
from datetime import UTC
from datetime import date
from datetime import datetime
from datetime import time as dt_time
from datetime import timedelta
from datetime import timezone


class ModuloDate(object):
	"""
	Utility per gestire operazioni e formattazioni sulle date.
	"""
	
	FORMATO_DATA="%Y-%m-%d"
	FORMATO_DATA_IT="%d/%m/%Y"
	FORMATO_DATA_ORA="%Y-%m-%d %H:%M:%S"
	FORMATO_DATA_ORA_NOMEFILE="%Y-%m-%d_%H-%M-%S"
	FORMATO_DATA_ORA_NOSPAZI="%Y%m%d%H%M%S"
	FORMATO_ORA="%H:%M:%S"
	
	
	@staticmethod
	def now()->datetime:
		"""
		Data e ora attuali.
		"""
		return datetime.now()
	
	@classmethod
	def nowUtc(cls)->datetime:
		"""
		Data e ora attuali in formato UTC (quindi senza fuso orario e DST)
		"""
		data=datetime.now(timezone.utc)
		data=cls.setTimezoneUtc(data)
		return data
	
	@staticmethod
	def today()->date:
		"""
		Data odierna, senza ora.
		"""
		return date.today()
	
	@staticmethod
	def getSecs()->int:
		"""
		Timestamp in secondi in formato UTC
		"""
		return int(time.time())
	
	@staticmethod
	def getMillis()->int:
		"""
		Timestamp in millisecondi in formato UTC
		"""
		return int(time.time()*1000)
	
	@classmethod
	def getWeekDay(cls,data:datetime|None=None)->str:
		"""
		Se te lo restituisce in inglese devi settare il locale
		"""
		if data is None:
			data=cls.now()
		return data.date().strftime("%A")
	
	#
	# conversioni
	#
	@classmethod
	def dateToString(cls,data:datetime|None=None,formato:str=FORMATO_DATA_ORA)->str:
		"""
		Formatta un oggetto data.
		:param data: data da formattare, se non specificata viene usata la data attuale
		:param formato: in che modo deve essere formattata la data, se non specificato viene usato il formato inglese
		"""
		if data is None:
			data=cls.now()
		return data.strftime(formato)
	
	@staticmethod
	def stringToDate(stringa:str,formato:str=FORMATO_DATA_ORA)->datetime:
		"""
		Trasforma una data in formato stringa a oggetto.
		:param stringa: stringa da trasformare in data
		:param formato: in che modo deve essere formattata la data, se non specificato viene usato il formato inglese
		"""
		return datetime.strptime(stringa,formato)
	
	@staticmethod
	def timeToString(orario:dt_time,formato:str=FORMATO_ORA)->str:
		"""
		Formatta un oggetto di tipo ora.
		:param orario: orario da formattare
		:param formato: in che modo deve essere formattato l'orario, se non specificato viene usato il formato standard
		"""
		return orario.strftime(formato)
	@classmethod
	def stringToTime(cls,stringa:str,formato:str=FORMATO_ORA)->dt_time:
		"""
		Formatta un oggetto di tipo ora.
		:param stringa: stringa da formattare in orario
		:param formato: in che modo deve essere formattato l'orario, se non specificato viene usato il formato standard
		"""
		return cls.dateToTime(cls.stringToDate(stringa,formato))
	
	@classmethod
	def timeToDate(cls,orario:dt_time)->datetime:
		"""
		Converte da oggetto orario a data completa.
		Viene aggiunta la data odierna all'orario passato in input.
		"""
		return datetime.combine(cls.today(), orario)
	
	@staticmethod
	def timedeltaToTime(orario:timedelta)->dt_time:
		"""
		Converte un oggetto timedelta a oggetto orario.
		"""
		return (datetime.min + orario).time()
	
	@staticmethod
	def dateToTime(data:datetime)->dt_time:
		"""
		Rimuove la data da un oggetto data completo, lasciando solo l'orario.
		"""
		return data.time()
	
	@staticmethod
	def dateToTimestamp(data:datetime)->int:
		"""
		Converte un oggetto data completo in timestamp in secondi.
		Se ti serve avere il timestamp in formato UTC usa il metodo dedicato.
		"""
		return int(datetime.timestamp(data))
	@staticmethod
	def timestampToDate(timestamp:int|float)->datetime:
		"""
		Converte un timestamp in secondi in un oggetto data completo.
		Se ti serve avere il timestamp in formato UTC usa il metodo dedicato.
		"""
		return datetime.fromtimestamp(timestamp)
	
	@classmethod
	def dateToTimestampUtc(cls,data:datetime)->int:
		"""
		Converte un oggetto data completo in timestamp in secondi in formato UTC.
		"""
		return cls.dateToTimestamp(cls.setTimezoneUtc(data))
	@classmethod
	def timestampUtcToDate(cls,timestamp:int|float)->datetime:
		"""
		Converte un timestamp in secondi in formato UTC in un oggetto data completo.
		Questo metodo richiede python >= 3.11
		"""
		return datetime.fromtimestamp(timestamp,UTC)
	
	#
	# operazioni
	#
	@staticmethod
	def dateDiff(data1:datetime,data2:datetime)->timedelta:
		"""
		Calcola la differenza di tempo (sia data che oraria) tra 2 date complete.
		"""
		return data1-data2
	
	@classmethod
	def minutesDiff(cls,data1:datetime,data2:datetime)->int:
		"""
		Calcola la differenza in minuti tra 2 date complete.
		"""
		diff=cls.dateDiff(data1,data2)
		diffValue=0
		if diff.days is not None and diff.days!=0:
			diffValue+=diff.days*24*60
		diffValue+=int(diff.seconds/60)
		return diffValue
	@classmethod
	def hoursDiff(cls,data1:datetime,data2:datetime)->int:
		"""
		Calcola la differenza in ore tra 2 date complete.
		"""
		diff=cls.dateDiff(data1, data2)
		diffValue=0
		if diff.days is not None and diff.days!=0:
			diffValue+=diff.days*24
		diffValue+=int(diff.seconds/3600)
		return diffValue
	@classmethod
	def daysDiff(cls,data1:datetime,data2:datetime) -> int:
		"""
		Calcola la differenza in giorni tra 2 date complete.
		"""
		diff=cls.dateDiff(data1,data2)
		if diff.days is not None and diff.days!=0:
			return diff.days
		return 0
	
	@staticmethod
	def plusMinusDays(data:datetime,days:int|float)->datetime:
		"""
		Aggiunge o toglie giorni ad una data completa.
		"""
		td=timedelta(days=abs(days))
		if days>=0:
			return data + td
		return data - td
	
	@staticmethod
	def plusMinusHours(data:datetime,hours:int|float)->datetime:
		"""
		Aggiunge o toglie ore ad una data completa.
		"""
		td=timedelta(hours=abs(hours))
		if hours>=0:
			return data + td
		return data - td
	
	@staticmethod
	def plusMinusMinutes(data:datetime,minutes:int|float)->datetime:
		"""
		Aggiunge o toglie minuti ad una data completa.
		"""
		td=timedelta(minutes=abs(minutes))
		if minutes>=0:
			return data + td
		return data - td
	
	@staticmethod
	def plusMinusSeconds(data:datetime,seconds:int|float)->datetime:
		"""
		Aggiunge o toglie minuti ad una data completa.
		"""
		td=timedelta(seconds=abs(seconds))
		if seconds>=0:
			return data + td
		return data - td
	
	@staticmethod
	def setStartOfDay(data:datetime)->datetime:
		"""
		Imposta l'inizio del giorno ad una data completa.
		"""
		return data.replace(hour=0, minute=0, second=0, microsecond=0)
	
	@staticmethod
	def setEndOfDay(data:datetime)->datetime:
		"""
		Imposta la fine del giorno ad una data completa.
		"""
		return data.replace(hour=23, minute=59, second=59, microsecond=999999)
	
	@classmethod
	def setTimezoneLocale(cls,data:datetime)->datetime:
		"""
		Imposta il fuso orario locale ad una data completa.
		"""
		return cls.setTimezoneUtc(data).astimezone(tz=None)
	
	@classmethod
	def setTimezoneUtc(cls,data:datetime)->datetime:
		"""
		Imposta SOLO il fuso orario UTC ad una data completa.
		"""
		return cls.setTimezoneFromTzInfo(data,timezone.utc)
	
	@staticmethod
	def setTimezoneFromTzInfo(data:datetime,tz:datetime.tzinfo)->datetime:
		"""
		Imposta un fuso orario ad una data completa.
		"""
		return data.replace(tzinfo=tz)
	
	@classmethod
	def getTimezoneLocal(cls)->datetime.tzinfo:
		"""
		Ritorna il fuso orario locale.
		"""
		return cls.now().astimezone().tzinfo
	
	#
	# altre funzioni
	#
	@classmethod
	def calculateElapsedSecs(cls,millisInizio:int)->str:
		"""
		Crea la frase che mostra quanti secondi sono trascorsi dall'inizio.
		"""
		elapsedSecs=int((cls.getMillis()-millisInizio)*0.001)
		if elapsedSecs==0:
			return ""
		return f" in {elapsedSecs}s"
