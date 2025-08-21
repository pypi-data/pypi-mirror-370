import re

from modulitiz_micro.ModuloStringhe import ModuloStringhe


class ModuloListe(object):
	"""
	Utility di gestione degli oggetti liste.
	"""
	
	@staticmethod
	def mergeListsOfDicts(listaFrom: list[dict],keyFrom: str|int,listaTo: list[dict],keyTo: str|int) -> list[dict]:
		"""
		Esempio: queste due liste...
		[
			{'index':1},
			{'index':3}
		]

		[
			{'id':1,'val':'a'},
			{'id':2,'val':'b'},
			{'id':3,'val':'c'},
			{'id':4,'val':'d'}
		]

		... diventano così

		[
			{'id':1,'val':'a'},
			{'id':3,'val':'c'}
		]
		"""
		nuovaLista=[]
		for elemFrom in listaFrom:
			valore=str(elemFrom[keyFrom])
			for elemTo in listaTo:
				if str(elemTo[keyTo])==valore:
					nuovaLista.append(elemTo)
		return nuovaLista
	
	@classmethod
	def humanOrder(cls,lista: list) -> list:
		"""
		Ordina una lista in modo che sia più leggibile: ad esempio:
		[elemento1,elemento10,elemento2]
		viene ordinato in questo modo:
		[elemento1,elemento2,elemento10]
		invece che:
		[elemento10,elemento1,elemento2]
		"""
		convert=lambda text:int(text) if text.isdigit() else text
		alphanum=lambda key:[convert(c) for c in re.split(r'(\d+)',key)]
		return sorted(lista,key=alphanum)
	
	@staticmethod
	def eliminaElementi(lista: list,elemsToRemove: list|tuple) -> list:
		"""
		Elimina dalla lista gli elementi specificati.
		"""
		for elemToRemove in elemsToRemove:
			while elemToRemove in lista:
				lista.remove(elemToRemove)
		return lista
	
	@classmethod
	def eliminaElementiVuoti(cls,lista: list) -> list:
		"""
		Elimina dalla lista le stringhe vuote e gli elementi null
		"""
		return cls.eliminaElementi(lista,(None,""))
	
	@staticmethod
	def diff(lista1: list,lista2: list) -> tuple:
		"""
		Calcola la differenza tra 2 liste, mostra gli elementi che mancano dalla 1a alla 2a e viceversa.
		"""
		set1=set(lista1)
		set2=set(lista2)
		toAdd=list(set1-set2)
		toRemove=list(set2-set1)
		return toAdd,toRemove
	
	@staticmethod
	def affianca(lista1: list,lista2: list) -> list:
		"""
		Unisce 2 liste.
		"""
		return list(zip(lista1,lista2))
	
	@staticmethod
	def separa(lista: list) -> list:
		"""
		Separa 2 liste.
		"""
		return [list(x) for x in zip(*lista)]
	
	@staticmethod
	def chunks(lista: list,n: int):
		"""
		Divide una lista in una lista di liste.
		"""
		for i in range(0,len(lista),n):
			yield lista[i:i+n]
	
	@staticmethod
	def isEmpty(lista: list) -> bool:
		"""
		Verifica se una lista è null o vuota.
		"""
		return lista is None or lista==[]
	
	@staticmethod
	def collectionContainsString(lista: list|tuple,testo: str) -> bool:
		"""
		Verifica se almeno un elemento di una lista o una tupla contiene una stringa.
		"""
		for elem in lista:
			if ModuloStringhe.contains(elem,testo):
				return True
		return False
	
	@staticmethod
	def stringContainsCollection(testo: str,lista: list|tuple) -> bool:
		"""
		Verifica se una stringa contiene almeno un elemento di una lista o una tupla.
		"""
		for elem in lista:
			if ModuloStringhe.contains(testo,elem):
				return True
		return False
	
	@staticmethod
	def collectionSafeGet(collection: dict|list|tuple,*keys):
		"""
		Ritorna elementi innestati in un dizionario, lista o tupla in una sola volta.
		Se un elemento intermedio non esiste ritorna null.
		Ad esempio:
		'ciao' = funzione(
			{'a':[('ciao',),]}
			,
			'a',0,0
		)
		"""
		for key in keys:
			try:
				collection=collection[key]
			except (IndexError,KeyError):
				return
		return collection
