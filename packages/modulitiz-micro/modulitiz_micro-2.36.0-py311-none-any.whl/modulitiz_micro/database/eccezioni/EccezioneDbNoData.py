from modulitiz_micro.eccezioni.EccezioneBase import EccezioneBase

class EccezioneDbNoData(EccezioneBase):
	
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
