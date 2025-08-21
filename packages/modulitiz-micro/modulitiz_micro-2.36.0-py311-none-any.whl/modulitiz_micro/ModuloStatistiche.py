from modulitiz_micro.ModuloDate import ModuloDate
from modulitiz_micro.ModuloNumeri import ModuloNumeri


class ModuloStatistiche(object):
	"""
	Utility per la gestione delle statistiche.
	"""
	
	@staticmethod
	def calcolaProgresso(index:int, contaElementiElaborati:int, totElementi:int, secsInizio:int)->str:
		"""
		Calcola il tempo rimanente alla fine dell'elaborazione di un certo numero di elementi in base al trend attuale.
		:param index: deve partire da 0
		:param contaElementiElaborati: deve partire da 1
		:param totElementi: numero totale di elementi
		:param secsInizio: timestamp di inizio elaborazione
		"""
		secsFine=ModuloDate.getSecs()
		percentuale=int((index*100) / totElementi)
		
		secondiTrascorsi=secsFine - secsInizio
		elementiRimanenti=totElementi - index
		secondiRimanenti=int((secondiTrascorsi / contaElementiElaborati) * elementiRimanenti)
		tempoRimanente=ModuloDate.dateToString(ModuloDate.timestampUtcToDate(secondiRimanenti),ModuloDate.FORMATO_ORA)
		
		# se i numeri sono alti li conveto in un formato più leggibile
		index=ModuloNumeri.humanFormat(index)
		totElementi=ModuloNumeri.humanFormat(totElementi)
		msg="Progresso: {:<5}/{}, percentuale: {:<3}%, tempo rimanente: {}".format(index, totElementi, percentuale, tempoRimanente)
		return msg
