from modulitiz_micro.eccezioni.http.EccezioneHttp import EccezioneHttp


class EccezioneHttp404(EccezioneHttp):
	
	def __init__(self,):
		super().__init__(404)
