from functools import wraps

from modulitiz_micro.ModuloFunzioni import ModuloFunzioni
from modulitiz_micro.util.spooler.Spooler import Spooler
from modulitiz_micro.util.spooler.beans.QueueBean import QueueBean
from modulitiz_micro.util.spooler.eccezioni.EccezioneSpooler import EccezioneSpooler
from modulitiz_micro.util.spooler.eccezioni.EccezioneSpoolerFull import EccezioneSpoolerFull


def spooler(maxSize:int,notifyIfConsecutiveSizeGreaterThan:int=0):
	"""
	Usare questo decorator per produrre (creare) la coda di azioni e consumarla (scodare) non appena c'è uno slot libero.
	:param maxSize: dimensione massima della coda
	:param notifyIfConsecutiveSizeGreaterThan: cosa fare se la coda è piena:
		- 0: notifica sempre
		- >0: notifica solo se maggiore di N
	"""
	# controllo parametri di input
	if notifyIfConsecutiveSizeGreaterThan>maxSize:
		raise EccezioneSpooler("%d non può essere maggiore di %d"%(notifyIfConsecutiveSizeGreaterThan,maxSize))
	
	def decorator(funzione):
		@wraps(funzione)
		def wrapped(*args,**kwargs):
			fullPathFunction=ModuloFunzioni.getFullyQualifiedName(funzione)
			bean=Spooler.beans.get(fullPathFunction,None)
			if bean is None:
				bean=QueueBean()
				Spooler.beans[fullPathFunction]=bean
			# controllo se ho raggiunto o superato il limite
			if bean.size>=maxSize:
				bean.countConsecutiveOverSize+=1
				if bean.countConsecutiveOverSize>notifyIfConsecutiveSizeGreaterThan:
					bean.countConsecutiveOverSize=0
					raise EccezioneSpoolerFull()
			else:
				bean.countConsecutiveOverSize=0
			# chiamo la funzione
			Spooler.increaseSize(bean)
			try:
				with bean.lock:
					output=funzione(*args,**kwargs)
			except Exception as e:
				Spooler.decreaseSize(bean)
				raise e
			Spooler.decreaseSize(bean)
			return output
		return wrapped
	return decorator
