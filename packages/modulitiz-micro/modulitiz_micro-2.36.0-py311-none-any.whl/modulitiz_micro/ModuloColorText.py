import colorama
import webcolors

from modulitiz_micro.rete.http.ModuloHttpUtils import ModuloHttpUtils


class ModuloColorText(object):
	"""
	Utility per gestire i colori e stampare a schermo testo colorato.
	"""
	
	DEFAULT=	'\033[0m'
	GRASSETTO=	DEFAULT+'\033[1m'
	NERO=		'\033[90m'
	ROSSO=		'\033[91m'
	VERDE=		'\033[92m'
	GIALLO=		'\033[93m'
	BLU=		'\033[94m'
	FUCSIA=		'\033[95m'
	AZZURRO=	'\033[96m'
	
	def __init__(self):
		colorama.init()
	
	@staticmethod
	def wordToRGB(word:str,lang:str="en")->str|None:
		"""
		Traduce un colore in formato RGB, è possibile scegliere la lingua di origine.
		"""
		if lang!="en":
			word=ModuloHttpUtils.translate(lang,"en",word)
			if word is None:
				return None
		word=word.replace(" ","").replace("ish","")
		return webcolors.name_to_hex(word)
