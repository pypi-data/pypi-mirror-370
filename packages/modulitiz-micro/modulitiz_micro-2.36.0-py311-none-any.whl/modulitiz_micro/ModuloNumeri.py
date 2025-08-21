class ModuloNumeri(object):
	"""
	Utility di gestione dei numeri, sia interi (senza virgola) che floating-point (con decimali) che con o senza segno.
	"""
	
	UNO_DIVISO_1024=0.0009765625
	
	NUMERI_CARDINALI={
		0:"zero",
		1:"uno",
		2:"due",
		3:"tre",
		4:"quattro",
		5:"cinque",
		6:"sei",
		7:"sette",
		8:"otto",
		9:"nove",
		10:"dieci",
		11:"undici"
	}
	
	NUMERI_ORDINALI={
		"primo":1,
	}
	
	@staticmethod
	def isInt(valore)->bool:
		"""
		Determina se un valore può essere considerato un numero intero.
		"""
		try:
			int(valore)
			return True
		except ValueError:
			return False
	
	@staticmethod
	def isFloat(valore)->bool:
		"""
		Determina se un valore può essere considerato un numero con la virgola.
		"""
		try:
			float(valore)
			return True
		except ValueError:
			return False

	@staticmethod
	def strToInt(valore:str)->int|None:
		"""
		Converte una stringa in numero intero.
		"""
		try:
			ris=int(valore)
			return ris
		except ValueError:
			return None

	@staticmethod
	def intToBool(valore:int)->bool:
		"""
		Converte un numero intero in valore booleano (o binario).
		"""
		if int(valore)==1:
			return True
		return False

	@staticmethod
	def boolToInt(valore:bool)->int:
		"""
		Converte un valore booleano (o binario) in numero intero.
		"""
		return int(valore)

	@classmethod
	def byteToKilobyte(cls,byte:int)->int:
		"""
		Converte un numero di byte in KB
		"""
		return int(byte*cls.UNO_DIVISO_1024)
	@classmethod
	def byteToMegabyte(cls,byte:int)->int:
		"""
		Converte un numero di byte in MB
		"""
		return int(cls.byteToKilobyte(byte)*cls.UNO_DIVISO_1024)

	@classmethod
	def versionStrToInt(cls,testo:str)->int:
		"""
		Converte la stringa di una versione in intero.
		NB: la versione andrebbe sempre trattata come una stringa.
		"""
		arr=testo.split(".")
		testoPadded="".join([x.ljust(4,"0") for x in arr])
		return cls.strToInt(testoPadded)

	@staticmethod
	def humanFormat(num: int) -> str:
		"""
		Formatta un numero in modo che sia più leggibile.
		"""
		magnitude=0
		while abs(num)>=1000:
			magnitude+=1
			num/=1000.0
		return '%.2f%s'%(num,['','K','M','G','T','P'][magnitude])
	
	@staticmethod
	def decimalNumbersTruncate(value:float,decimals:int)->float:
		"""
		Rimuove la quantità di decimali voluta da un valore.
		Il valore 1.234 se viene troncato a 2 decimali diventa 1.23
		"""
		factor=10**decimals
		return int(value*factor)/factor
	
	@classmethod
	def numberToWord(cls,numero:int)->str:
		"""
		Converte un numero in parola.
		"""
		return cls.NUMERI_CARDINALI[numero]
	@classmethod
	def wordToNumber(cls,parola:str)->int:
		"""
		Converte una parola in numero.
		"""
		return cls.NUMERI_ORDINALI[parola]
