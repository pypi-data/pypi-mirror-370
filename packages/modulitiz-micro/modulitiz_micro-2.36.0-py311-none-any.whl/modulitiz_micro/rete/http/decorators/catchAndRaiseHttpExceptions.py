import socket
from functools import wraps
from urllib.error import URLError

import requests

from modulitiz_micro.eccezioni.http.EccezioneHttpGeneric import EccezioneHttpGeneric


def catchAndRaiseHttpExceptions(funzione):
	"""
	Cattura tutte le eccezioni http di vario tipo e rilancia un'eccezione custom
	"""
	
	@wraps(funzione)
	def wrapped(*args,**kwargs):
		try:
			return funzione(*args,**kwargs)
		except (ConnectionError,TimeoutError,URLError,
				requests.exceptions.ConnectionError,socket.gaierror) as ex:
			raise EccezioneHttpGeneric() from ex
	return wrapped
