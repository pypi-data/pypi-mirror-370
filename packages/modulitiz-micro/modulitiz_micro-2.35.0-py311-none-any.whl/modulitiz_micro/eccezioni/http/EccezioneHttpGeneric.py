from modulitiz_micro.eccezioni.http.EccezioneHttp import EccezioneHttp


class EccezioneHttpGeneric(EccezioneHttp):
	
	def __init__(self):
		super().__init__(None)
