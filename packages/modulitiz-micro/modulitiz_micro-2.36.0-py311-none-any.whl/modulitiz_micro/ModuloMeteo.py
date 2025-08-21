import json

from modulitiz_micro.ModuloDate import ModuloDate
from modulitiz_micro.ModuloListe import ModuloListe
from modulitiz_micro.eccezioni.http.EccezioneHttpGeneric import EccezioneHttpGeneric
from modulitiz_micro.files import ModuloLogging
from modulitiz_micro.rete.http.ModuloHttp import ModuloHttp
from modulitiz_micro.rete.http.ModuloHttpUtils import ModuloHttpUtils


class ModuloMeteo(object):
	"""
	Utility di gestione delle previsioni meteo.
	"""
	OPZIONI="lang=it&units=metric"
	KEY="appid=e28cd365c35c12e3ed8f2d84e04398c9"
	
	__URL_BASE="https://api.openweathermap.org"
	URL_ATTUALE=__URL_BASE+f"/data/2.5/weather?{OPZIONI}&{KEY}&q="
	URL_PREVISIONE=__URL_BASE+f"/data/2.5/forecast?{OPZIONI}&{KEY}&q="
	
	def __init__(self,logger:ModuloLogging):
		self.__logger=logger
	
	def getPrevisionePioggiaFinoADomani(self,citta:str,codStato:str)->list|None:
		"""
		Chiede le previsioni fino al giorno dopo e mostra solo i risultati che dicono che pioverà.
		"""
		adesso=ModuloDate.now()
		domani=ModuloDate.setEndOfDay(ModuloDate.plusMinusDays(adesso,1))
		oreDiff=ModuloDate.hoursDiff(domani, adesso)
		elementi=self.__getPrevisioni(citta, codStato,True,None,oreDiff)
		if elementi is None:
			return None
		# filtro gli elementi
		lista=[]
		for elem in elementi:
			if ModuloListe.collectionSafeGet(elem,'rain') is not None:
				lista.append(elem)
		return lista
	
	def __getPrevisioni(self,citta:str,codStato:str,includiPrimaPrevisione:bool,stepHours:int|None,maxHours:int)->list|None:
		cittaEStato=citta+","+codStato
		url=self.URL_PREVISIONE+ModuloHttpUtils.encodeUrl(cittaEStato)
		http=ModuloHttp(url,self.__logger,False)
		try:
			response=http.doGet(0,False)
		except EccezioneHttpGeneric:
			return None
		responseObj=json.loads(response.responseBody)
		lista=responseObj['list']
		maxLista=len(lista)
		# calcolo gli indici
		if maxHours is not None:
			maxInd=int(maxHours/3)+1
			if maxInd>=maxLista:
				maxInd=maxLista-1
		else:
			maxInd=maxLista-1
		if stepHours is None:
			step=1
		else:
			step=int(stepHours/3)
		inds=list(range(4,maxInd,step))
		if includiPrimaPrevisione:
			inds.insert(0,1)
		# processo il json
		output=[]
		for ind in inds:
			elem=lista[ind]
			output.append(elem)
		return output
