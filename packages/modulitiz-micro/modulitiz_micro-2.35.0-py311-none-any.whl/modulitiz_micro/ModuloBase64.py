import base64

from modulitiz_micro.ModuloStringhe import ModuloStringhe


class ModuloBase64(object):
	"""
	Utility di gestione del sistema di codifica base64.
	"""
	
	@staticmethod
	def codificaFile(inputFile:str,outputFile:str):
		"""
		Legge un file binario e scrive un file con il relativo contenuto codificato.
		"""
		# leggo
		with open(inputFile,"rb") as fp:
			contenuto=fp.read()
		# codifico
		encoded=base64.b64encode(contenuto)
		# scrivo
		with open(outputFile,"w+b") as fp:
			fp.write(encoded)
	@staticmethod
	def codificaStr(decodedStr:str)->str:
		"""
		Converte una stringa.
		"""
		return base64.b64encode(decodedStr.encode(ModuloStringhe.CODIFICA_UTF8)).decode(ModuloStringhe.CODIFICA_UTF8)
	@staticmethod
	def codificaStrUrlSafe(decodedStr:str)->str:
		"""
		Converte una stringa in modo che possa essere usata come url.
		"""
		return base64.urlsafe_b64encode(decodedStr.encode(ModuloStringhe.CODIFICA_UTF8)).decode(ModuloStringhe.CODIFICA_UTF8)

	@staticmethod
	def decodificaFile(inputFile:str,outputFile:str):
		"""
		Legge il contenuto codificato di un file e lo decodifica, scrivendo l'output in un altro file.
		"""
		# leggo
		with open(inputFile,"rb") as fp:
			contenuto=fp.read()
		# decodifico
		decoded=base64.b64decode(contenuto)
		# scrivo
		with open(outputFile,"w+b") as fp:
			fp.write(decoded)
	@staticmethod
	def decodificaStr(codedStr:str)->str:
		"""
		Decodifica una stringa.
		"""
		return base64.b64decode(codedStr.encode(ModuloStringhe.CODIFICA_UTF8)).decode(ModuloStringhe.CODIFICA_UTF8)
	@staticmethod
	def decodificaStrUrlSafe(codedStr:str)->str:
		"""
		Decodifica una stringa che è stata codificata per essere usata come url.
		"""
		return base64.urlsafe_b64decode(codedStr.encode(ModuloStringhe.CODIFICA_UTF8)).decode(ModuloStringhe.CODIFICA_UTF8)
