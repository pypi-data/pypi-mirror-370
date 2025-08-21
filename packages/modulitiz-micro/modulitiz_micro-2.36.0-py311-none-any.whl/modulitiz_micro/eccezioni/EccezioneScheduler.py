from modulitiz_micro.eccezioni.EccezioneBase import EccezioneBase


class EccezioneScheduler(EccezioneBase):
	
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
