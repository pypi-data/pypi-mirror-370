from modulitiz_micro.ModuloStringhe import ModuloStringhe
from modulitiz_micro.sistema.ModuloSystem import ModuloSystem


class ModuloAndroidAdb(object):
	"""
	deviceId puo' essere l'identificativo:
	- del dispositivo di 16 caratteri esadecimale
	- della porta usb, del prodotto, del modello, ... (vedi il comando 'adb devices -l')
	il transport_id non e' supportato
	"""
	
	def __init__(self,deviceId:str):
		self.deviceId=deviceId
	
	def isDeviceConnected(self)->bool:
		cmd=r'adb -s "%s" get-state'%(self.deviceId,)
		return self.__retrieveLastLineOfOutput(cmd)=='device'
	
	def isDeviceUnlocked(self)->bool:
		cmd=r'adb -s "%s" shell dumpsys window | grep mDreamingLockscreen'%(self.deviceId,)
		output=ModuloSystem.systemCallReturnOutput(cmd,None).strip()
		valori=[x.split("=")[1] for x in output.split(" ")]
		for valore in valori:
			if valore=="true":
				return False
		return True
	
	def reboot(self)->bool:
		cmd=r'adb -s "%s" reboot'%(self.deviceId,)
		return self.__retrieveLastLineOfOutput(cmd)==''
	def shutdown(self)->bool:
		cmd=r'adb -s "%s" reboot -p'%(self.deviceId,)
		return self.__retrieveLastLineOfOutput(cmd)=='Done'
	
	@classmethod
	def closeServer(cls) -> bool:
		cmd="adb kill-server"
		return cls.__retrieveOutput(cmd)==''
	
	@staticmethod
	def __retrieveOutput(cmd)->str:
		return ModuloStringhe.normalizzaEol(ModuloSystem.systemCallReturnOutput(cmd,None)).strip()
	@classmethod
	def __retrieveLastLineOfOutput(cls,cmd)->str:
		output=cls.__retrieveOutput(cmd)
		righe=output.split("\n")
		return righe[-1]
