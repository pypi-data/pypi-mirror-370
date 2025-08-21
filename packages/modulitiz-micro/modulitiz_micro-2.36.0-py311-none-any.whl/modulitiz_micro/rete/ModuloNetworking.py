import os
import socket
from contextlib import closing
from uuid import getnode

from _socket import gaierror

from modulitiz_micro.ModuloListe import ModuloListe
from modulitiz_micro.ModuloStringhe import ModuloStringhe
from modulitiz_micro.eccezioni.EccezioneRuntime import EccezioneRuntime
from modulitiz_micro.sistema.ModuloSystem import ModuloSystem


class ModuloNetworking(object):
	@staticmethod
	def getMacAddress()->str:
		mac=("%012X" % getnode())
		return mac

	@staticmethod
	def getLocalIp()->str|None:
		"""
		Returns private local IP address.
		"""
		sockObj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sockObj.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		try:
			# doesn't even have to be reachable
			sockObj.connect(('255.255.255.255', 1))
			indirizzoIp = sockObj.getsockname()[0]
		except gaierror:
			indirizzoIp = None
		finally:
			sockObj.close()
		return indirizzoIp

	@staticmethod
	def isHttpPortOpen(host:str|None,port:int)->bool:
		# controllo host
		if host is None:
			host="127.0.0.1"
		# controllo porta
		with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
			if sock.connect_ex((host, port)) == 0:
				return True
		return False

	@staticmethod
	def checkPing(indirizzoIp:str)->bool:
		# costruisco il comando a seconda del sistema operativo
		comando="ping "
		if ModuloSystem.isWindows():
			comando+="-n"
		elif os.name=='posix':
			comando+="-c"
		else:
			raise EccezioneRuntime("Tipologia del sistema operativo non riconosciuta: "+os.name)
		comando+=" 1 " + indirizzoIp
		# eseguo il comando
		outputComando=ModuloStringhe.normalizzaEol(ModuloSystem.systemCallReturnOutput(comando,None))
		righe=outputComando.split("\n")
		righe=ModuloListe.eliminaElementiVuoti(righe)
		for riga in righe:
			if ModuloStringhe.contains(riga, "%"):
				numPacchettiPersi=int(riga.split("=")[1].split("(")[0].strip())
				return numPacchettiPersi==0
		return False
