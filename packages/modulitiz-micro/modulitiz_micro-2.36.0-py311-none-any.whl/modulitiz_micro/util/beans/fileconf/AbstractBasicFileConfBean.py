from modulitiz_micro.util.beans.fileconf.AbstractFileConfBean import AbstractFileConfBean


class AbstractBasicFileConfBean(AbstractFileConfBean):
	"""
	Classe che può essere usata come base per definire la struttura del file di configurazione del programma
	"""
	
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.percorsoCartellaEsterna=self._diz['percorsoCartellaEsterna']
