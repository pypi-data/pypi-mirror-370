from modulitiz_micro.ModuloDate import ModuloDate
from modulitiz_micro.ModuloListe import ModuloListe
from modulitiz_micro.files.cache.CacheBean import CacheBean


class CacheRam(object):
	def __init__(self):
		self.__mappa={}
	
	def get(self,tipo: str,chiave: str,minsBeforeExpiry: int|None) -> CacheBean|None:
		# controllo se esiste in ram
		bean: CacheBean=ModuloListe.collectionSafeGet(self.__mappa,tipo,chiave)
		if bean is None:
			return None
		# controllo se non e' scaduto
		if minsBeforeExpiry is not None and ModuloDate.now()>ModuloDate.plusMinusMinutes(bean.dataLastUpdate,minsBeforeExpiry):
			del self.__mappa[tipo][chiave]
			return None
		return bean
	
	def insertOrUpdate(self,tipo: str,chiave: str,valore):
		if tipo not in self.__mappa:
			self.__mappa[tipo]={}
		if chiave not in self.__mappa[tipo]:
			self.__mappa[tipo][chiave]={}
		self.__mappa[tipo][chiave]=CacheBean(valore,ModuloDate.now())
	
	def clear(self):
		self.__mappa.clear()
