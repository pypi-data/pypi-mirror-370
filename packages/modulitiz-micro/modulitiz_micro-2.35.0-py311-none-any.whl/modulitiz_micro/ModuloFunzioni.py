import ast
import random
import sys

from modulitiz_micro.files.ModuloFiles import ModuloFiles


class ModuloFunzioni(object):
	"""
	Utility riguardanti le funzioni o non catalogabili in modo definito.
	"""
	
	GENERI={'m':'Maschio','f':'Femmina'}
	
	@staticmethod
	def getFunctionName(n:int=0)->str:
		"""
		Per il nome della funzione corrente, non impostare nessun parametro o impostare 0;
		Per il nome della funzione chiamante, impostare 1;
		Per il nome della funzione chiamante la funzione, impostare 2;
		E via dicendo così.
		"""
		return sys._getframe(n + 1).f_code.co_name

	@staticmethod
	def getFullyQualifiedName(funzione)->str:
		"""
		Ritorna il package + il nome della funzione;
		in questo modo è possibile distinguere 2 funzioni con lo stesso nome, ad esempio:
		src.funzione
		src.package.funzione
		src.package.modulo.funzione
		src.package.modulo.classe.funzione
		"""
		return funzione.__module__+"."+funzione.__qualname__
	
	@staticmethod
	def getClassesFromFileSource(filename:str)->list[str]:
		"""
		Reads content of file, then finds all classes in it.
		"""
		module=ast.parse(ModuloFiles.readFileText(filename,True))
		classes=[node.name for node in ast.walk(module) if isinstance(node,ast.ClassDef)]
		return classes
	
	@staticmethod
	def orderDict(diz:dict)->dict:
		"""
		Ordina gli elementi di un dizionario.
		Nota: ha senso solo se hai intenzione di esporlo all'utente sotto forma di lista.
		"""
		myKeys = list(diz.keys())
		myKeys.sort()
		newDiz = {i: diz[i] for i in myKeys}
		return newDiz
	
	@staticmethod
	def dictGetFirstValue(diz: dict):
		"""
		Ritorna il valore del primo elemnto di un dizionario.
		È ottimizzato per oggetti con molti elementi.
		"""
		return next(iter(diz.items()))[1]
	
	@staticmethod
	def randomBoolean()->bool:
		"""
		Genera un valore booleano in modo randomico.
		"""
		return bool(random.getrandbits(1))
