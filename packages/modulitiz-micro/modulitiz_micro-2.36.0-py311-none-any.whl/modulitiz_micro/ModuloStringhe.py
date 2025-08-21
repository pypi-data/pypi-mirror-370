import locale
import random
import string

from modulitiz_micro.ModuloDate import ModuloDate


class ModuloStringhe(object):
	"""
	Utility di gestione delle stringhe.
	"""
	
	CODIFICA_ASCII="ascii"
	CODIFICA_LATIN1="latin_1"
	CODIFICA_UTF8="utf-8"
	
	SEP=r"//||//"
	
	@classmethod
	def setLocaleItalian(cls):
		"""
		Necessario per avere, ad esempio, il giorno della settimana nella lingua corretta.
		"""
		cls.setLocale("it_IT")
	
	@classmethod
	def setLocale(cls,lang:str):
		"""
		Imposta la lingua predefinita.
		"""
		try:
			cls.__setLocale(lang)
		except locale.Error:
			lang+=".utf8"
			cls.__setLocale(lang)
	
	@staticmethod
	def __setLocale(lang:str):
		locale.setlocale(locale.LC_TIME, lang)
	
	@staticmethod
	def isEmpty(val:str|None)->bool:
		"""
		Verifica se il valore passato in input è NULL o vuoto.
		"""
		if val is None:
			return True
		val=str(val)
		return val==''
	
	@staticmethod
	def contains(haystack:str,needle:str)->bool:
		"""
		Verifica se un testo è contenuto in un altro testo.
		:param haystack: testo contenitore
		:param needle: testo da cercare
		"""
		return haystack.find(needle)!=-1
	
	@staticmethod
	def normalizzaEol(cont:str)->str:
		"""
		Converte i caratteri di fine riga secondo lo standard Unix (universale)
		"""
		cont=cont.replace("\r\n","\n")
		cont=cont.replace("\r","\n")
		return cont
	
	@staticmethod
	def normalizzaTrattini(testo:str)->str:
		"""
		Tutti i caratteri assimilabili come un trattino vengono convertiti in trattini.
		"""
		#https://en.wikipedia.org/wiki/Dash#Common_dashes_and_Unicode_characters
		testo=testo.replace(u'\u2012',"-")		#figure dash
		testo=testo.replace(u'\u2013',"-")		#en dash
		testo=testo.replace(u'\u2014',"-")		#em dash
		testo=testo.replace(u'\u2015',"-")		#horizontal bar
		#https://en.wikipedia.org/wiki/Hyphen#Unicode
		testo=testo.replace(u'\u002D',"-")		#HYPHEN-MINUS
		testo=testo.replace(u'\u2212',"-")		#MINUS SIGN
		testo=testo.replace(u'\u00AD',"-")		#SOFT HYPHEN
		testo=testo.replace(u'\u2010',"-")		#HYPHEN
		testo=testo.replace(u'\u2011',"-")		#NON-BREAKING HYPHEN
		testo=testo.replace(u'\u0584',"-")		#ARMENIAN HYPHEN
		testo=testo.replace(u'\u1806',"-")		#MONGOLIAN SOFT HYPHEN
		testo=testo.replace(u'\uFE63',"-")		#SMALL HYPHEN-MINUS
		testo=testo.replace(u'\uFF0D',"-")		#FULLWIDTH HYPHEN-MINUS
		testo=testo.replace(u'\u2043',"-")		#HYPHEN BULLET
		return testo
	
	@staticmethod
	def normalizzaCaratteriSpeciali(testo:str)->str:
		"""
		Normalizzazione altri caratteri speciali.
		"""
		testo=testo.replace(u'\u039b','&')		#GREEK CAPITAL LETTER LAMDA
		return testo
	
	@classmethod
	def aggiungiTimestamp(cls,nomefile:str)->str:
		"""
		Se il nome del file ha l'estensione aggiungo il timestamp prima dell'estensione
		"""
		timestamp=ModuloDate.dateToString(None,ModuloDate.FORMATO_DATA_ORA_NOSPAZI)
		if not cls.contains(nomefile,"."):
			return nomefile+"_"+timestamp
		arr=nomefile.split(".")
		nuovonome=".".join(arr[0:-1])+"_"+timestamp+"."+arr[-1]
		return nuovonome
	
	@classmethod
	def phoneNumberFormat(cls,stringa:str,sep:str):
		"""
		Formatta un numero di telefono rendendolo più facile da leggere.
		"""
		return cls.insertCharEveryN(stringa,sep,3)
	
	@staticmethod
	def capitalizeEveryWord(text:str)->str:
		"""
		Converte in maiuscolo il primo carattere di ogni parola.
		"""
		arr=text.split(" ")
		arrNew=[x.capitalize() for x in arr]
		textNew=" ".join(arrNew)
		return textNew
	
	@staticmethod
	def splitColonne(text:str,sep:str)->list:
		"""
		Divide una stringa in colonne, ad ogni colonna vengono tolti gli spazi all'inizio e alla fine.
		"""
		colonne=text.split(sep)
		colonne=[x.strip() for x in colonne]
		return colonne
	
	@staticmethod
	def randomString(useLower:bool,useUpper:bool,useDigits:bool,length:int)->str:
		"""
		Crea una stringa di caratteri e/o numeri di lunghezza configurabile.
		"""
		chars=""
		if useLower:
			chars+=string.ascii_lowercase
		if useUpper:
			chars+=string.ascii_uppercase
		if useDigits:
			chars+=string.digits
		return ''.join(random.choices(chars, k=length))
	
	@staticmethod
	def insertCharEveryN(stringa:str,sep:str,everyN:int)->str:
		"""
		Inserisce un carattere o un testo ogni N caratteri di un altro testo.
		"""
		return sep.join(stringa[i:i+everyN] for i in range(0, len(stringa), everyN))
	
	@staticmethod
	def trovaCodificaCorretta(textBytes:bytes,expectedText:str)->list:
		"""
		Questa funzione non ti puo' dire se la codifica e' corretta,
		devi verificarlo tu a occhio perche' piu' codifiche possono andare bene.
		"""
		# questa variabile la lascio qui dentro perche' e' pesante
		codecs=('ascii','big5','big5hkscs','cp037','cp424','cp437','cp500','cp737','cp775','cp850','cp852','cp855','cp856','cp857','cp860','cp861','cp862','cp863','cp864','cp865','cp866',
				'cp869','cp874','cp875','cp932','cp949','cp950','cp1006','cp1026','cp1140','cp1250','cp1251','cp1252','cp1253','cp1254','cp1255','cp1256','cp1257','cp1258','euc_jp',
				'euc_jis_2004','euc_jisx0213','euc_kr','gb2312','gbk','gb18030','hz','iso2022_jp','iso2022_jp_1','iso2022_jp_2','iso2022_jp_2004','iso2022_jp_3','iso2022_jp_ext','iso2022_kr',
				'latin_1','iso8859_2','iso8859_3','iso8859_4','iso8859_5','iso8859_6','iso8859_7','iso8859_8','iso8859_9','iso8859_10','iso8859_13','iso8859_14','iso8859_15','johab','koi8_r',
				'koi8_u','mac_cyrillic','mac_greek','mac_iceland','mac_latin2','mac_roman','mac_turkish','ptcp154','shift_jis','shift_jis_2004','shift_jisx0213','utf_16','utf_16_be','utf_16_le',
				'utf_7','utf_8','utf_8_sig')
		results=[]
		for codec in codecs:
			try:
				testo=textBytes.decode(codec)
				if testo==expectedText:
					results.append(codec)
			except UnicodeDecodeError:
				pass
		return results
