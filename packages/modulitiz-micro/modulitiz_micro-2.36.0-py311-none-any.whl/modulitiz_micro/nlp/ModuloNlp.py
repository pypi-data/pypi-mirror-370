class ModuloNlp(object):
	
	@staticmethod
	def giornoRelativoToParola(giornoRel:int)->str|None:
		match giornoRel:
			case -1: return "ieri"
			case 0: return "oggi"
			case 1: return "domani"
			case 2: return "dopodomani"
			case _: return None
	
	@staticmethod
	def giornoRelativoToNum(giornoRel:str)->int|None:
		match giornoRel:
			case "ieri": return -1
			case "oggi": return 0
			case "domani": return 1
			case "dopodomani": return 2
			case _: return None
	
	@staticmethod
	def verboEssere(isPassato:bool)->str:
		if isPassato:
			return "era"
		return "è"
	
	@staticmethod
	def articolo(isDeterminativo:bool,isMaschile:bool)->str:
		if isDeterminativo:
			if isMaschile:
				return "il"
			return "la"
		if isMaschile:
			return "un"
		return "una"
	
