class EccezioneRuntime(RuntimeError):
	
	def __init__(self,*args,**kwargs):
		super().__init__(*args)
	
	def getMessage(self)->str:
		return " ".join(self.args)
