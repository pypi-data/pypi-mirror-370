import asyncio
from functools import wraps


def noAwait(funzione):
	"""
	Usare questo decorator per evitare di propagare async e await in tutto il codice.
	Esempio dell'uso:
	
	@noAwait
	async def funzione(self):
		await funzioneAsync()
	"""
	
	@wraps(funzione)
	def wrapped(*args, **kwargs):
		try:
			loop=asyncio.get_event_loop_policy().get_event_loop()
		except RuntimeError:
			loop=asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		loop.run_until_complete(funzione(*args,**kwargs))
	return wrapped
