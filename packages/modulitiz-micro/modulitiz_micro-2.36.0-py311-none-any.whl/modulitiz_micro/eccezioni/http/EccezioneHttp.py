from modulitiz_micro.eccezioni.EccezioneBase import EccezioneBase


class EccezioneHttp(EccezioneBase):
	
	def __init__(self,httpCode:int|None,*args,**kwargs):
		super().__init__(*args,**kwargs)
		self.httpCode=httpCode
