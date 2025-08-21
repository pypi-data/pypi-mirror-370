import json
import random
from urllib.parse import quote_plus
from urllib.parse import unquote_plus

import requests

from modulitiz_micro.ModuloStringhe import ModuloStringhe
from modulitiz_micro.eccezioni.http.EccezioneHttpGeneric import EccezioneHttpGeneric
from modulitiz_micro.files.ModuloLogging import ModuloLogging
from modulitiz_micro.rete.http.ModuloHttp import ModuloHttp
from modulitiz_micro.rete.http.ModuloHttpConnectionSafe import ModuloHttpConnectionSafe
from modulitiz_micro.rete.http.decorators.catchAndRaiseHttpExceptions import catchAndRaiseHttpExceptions


class ModuloHttpUtils(object):
	@staticmethod
	def isUrlAvailable(logger:ModuloLogging|None,url:str,retries:int,ignoreCerts:bool=False) -> bool:
		if retries!=0:
			connectionSafe=ModuloHttpConnectionSafe(logger)
			return connectionSafe.run(retries,0,ModuloHttpUtils.__isUrlAvailable,url,ignoreCerts)
		try:
			return ModuloHttpUtils.__isUrlAvailable(url,ignoreCerts)
		except EccezioneHttpGeneric:
			return False
	
	@staticmethod
	@catchAndRaiseHttpExceptions
	def __isUrlAvailable(url:str,ignoreCerts:bool) -> bool:
		with requests.get(url,stream=True,verify=(not ignoreCerts)) as response:
			return response.status_code==ModuloHttp.STATUS_OK
	
	@staticmethod
	def getIpV4() -> str|None:
		"""
		Returns public external IpV4 address.
		"""
		url=random.choice(ModuloHttp.URLS_GET_IPV4)
		http=ModuloHttp(url,None)
		try:
			response=http.doGet(2,False)
		except EccezioneHttpGeneric:
			return None
		if response is None:
			return None
		return response.responseBody.decode(ModuloStringhe.CODIFICA_UTF8)
	
	@classmethod
	def translate(cls,langFrom:str|None,langTo:str,msg:str) -> str|None:
		if langFrom is None:
			langFrom="auto"
		msg=cls.encodeUrl(msg)
		url=f'https://translate.googleapis.com/translate_a/single?client=gtx&sl={langFrom}&tl={langTo}&dt=t&q={msg}'
		http=ModuloHttp(url,None)
		try:
			response=http.doGet(3,False)
		except EccezioneHttpGeneric:
			return None
		responseText=response.responseBody.decode(ModuloStringhe.CODIFICA_UTF8)
		result=json.loads(responseText)
		output="".join(x[0] for x in result[0])
		return output
	
	@staticmethod
	def encodeUrl(url: str) -> str:
		return quote_plus(url)
	@staticmethod
	def decodeUrl(url: str) -> str:
		return unquote_plus(url)
