from modulitiz_micro.eccezioni.EccezioneRuntime import EccezioneRuntime


class EccezioneBase(EccezioneRuntime):
	
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
