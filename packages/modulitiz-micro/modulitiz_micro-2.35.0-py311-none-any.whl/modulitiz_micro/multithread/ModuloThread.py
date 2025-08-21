import threading

from modulitiz_micro.files.ModuloLogging import ModuloLogging
from modulitiz_micro.multithread.ModuloThreadLogger import ModuloThreadLogger
from modulitiz_micro.multithread.ModuloThreadWithCallbackError import ModuloThreadWithCallbackError


class ModuloThread(object):
	@staticmethod
	def startDaemon(logger:ModuloLogging,funzione,args:tuple)->ModuloThreadLogger:
		d=ModuloThreadLogger(logger,name='th__'+funzione.__name__,target=funzione,args=args,daemon=True)
		d.start()
		return d
	@staticmethod
	def startDaemonWithCallbackError(callbackError,funzione,args:tuple)->ModuloThreadWithCallbackError:
		d=ModuloThreadWithCallbackError(callbackError,name='th__'+funzione.__name__,target=funzione,args=args,daemon=True)
		d.start()
		return d
	
	@staticmethod
	def numeroThreadsAttivi()->int:
		"""
		Non e' incluso il main, ovviamente.
		Se usi pydev debugger devi sottrarre altri 2 o 3 threads
		"""
		return threading.active_count()-1
