class EmailBean(object):
	def __init__(self,dizionario:dict):
		self.destinatario:str=dizionario['destinatario']
		self.user:str=dizionario['user']
		self.password:str=dizionario['password']
