from modulitiz_micro.sistema.ModuloSystem import ModuloSystem


class ModuloAndroid(object):
	@staticmethod
	def isAaptInstalled()->bool:
		return ModuloSystem.isAptPackageInstalled("aapt")
	@staticmethod
	def isAdbInstalled()->bool:
		return ModuloSystem.isAptPackageInstalled("adb")
	
	@staticmethod
	def getApkVersionName(nomefile:str)->str|None:
		if not ModuloAndroid.isAaptInstalled():
			return None
		cmd=rf'''aapt dump badging {nomefile} | grep "versionName" | sed -e "s/.*versionName='//" -e "s/' .*//"'''
		output=ModuloSystem.systemCallReturnOutput(cmd,None)
		return output
