from modulitiz_micro.eccezioni.EccezioneBase import EccezioneBase


class EccezioneSpooler(EccezioneBase):
	
	def __init__(self,msg:str):
		super().__init__(msg)
