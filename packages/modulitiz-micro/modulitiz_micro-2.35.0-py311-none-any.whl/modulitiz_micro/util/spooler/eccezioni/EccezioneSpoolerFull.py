from modulitiz_micro.util.spooler.eccezioni.EccezioneSpooler import EccezioneSpooler


class EccezioneSpoolerFull(EccezioneSpooler):
	
	def __init__(self):
		super().__init__("Spooler pieno")
