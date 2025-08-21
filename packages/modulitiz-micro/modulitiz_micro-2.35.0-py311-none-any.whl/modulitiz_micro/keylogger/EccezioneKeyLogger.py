from modulitiz_micro.eccezioni.EccezioneBase import EccezioneBase


class EccezioneKeyLogger(EccezioneBase):
	
	def __init__(self):
		super().__init__("Ricevuto comando da tastiera di chiusura programma")
