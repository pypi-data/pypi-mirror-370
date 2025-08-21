import time

from modulitiz_micro.ModuloDate import ModuloDate
from modulitiz_micro.ModuloListe import ModuloListe
from modulitiz_micro.ModuloNumeri import ModuloNumeri
from modulitiz_micro.ModuloStringhe import ModuloStringhe
from modulitiz_micro.sistema.ModuloSystem import ModuloSystem


class ModuloAndroidSim(object):
	"""
	CREATE TABLE sms (
		_id INTEGER PRIMARY KEY
		thread_id INTEGER
		address TEXT
		person INTEGER
		date INTEGER
		date_sent INTEGER DEFAULT 0
		protocol INTEGER
		read INTEGER DEFAULT 0
		status INTEGER DEFAULT -1
		type INTEGER
		reply_path_present INTEGER
		subject TEXT
		body TEXT
		service_center TEXT
		locked INTEGER DEFAULT 0
		sub_id INTEGER DEFAULT INVALID_SUBSCRIPTION_ID
		error_code INTEGER DEFAULT NO_ERROR_CODE
		creator TEXT
		seen INTEGER DEFAULT 0
	);
	"""
	
	def __init__(self,deviceId:str):
		self.deviceId=deviceId
		
		self.__SEP_WITH_DELIM=(r''' "'"\"%s"\"'" '''%(ModuloStringhe.SEP.replace(r"|",r"\|"),)).strip()
	
	def hasDeviceCellSignal(self)->bool:
		cmd=r'adb -s "%s" shell "dumpsys telephony.registry | grep mServiceState"'%(self.deviceId,)
		output=ModuloStringhe.normalizzaEol(ModuloSystem.systemCallReturnOutput(cmd,None)).strip()
		ind=output.find("=")
		if ind==-1:
			return False
		serviceState=output[ind+1]
		if not ModuloNumeri.isInt(serviceState):
			return False
		return int(serviceState)==0
	
	# operazioni di lettura
	def smsRead(self,onlyUnread:bool)->list:
		"""
		Tutti i comandi che fanno operazioni di SELECT, UPDATE o DELETE richiedono il ROOT
		"""
		sql=self.__smsQuery(onlyUnread,False)
		output=self.__querySmsDb(sql)
		return ModuloListe.eliminaElementiVuoti(output.split("|"+ModuloStringhe.SEP+"\n"))
	
	def smsReadUntilNew(self,checkEverySecs:int|float,timeoutMin:int|float) -> list:
		"""
		Aspetta l'arrivo di un nuovo messaggio.
		Questo metodo NON è asincrono.
		"""
		timeoutSecs=timeoutMin*60
		tsStart=ModuloDate.getSecs()
		results=[]
		while ModuloListe.isEmpty(results) and (ModuloDate.getSecs()-tsStart)<timeoutSecs:
			time.sleep(checkEverySecs)
			results=self.smsRead(True)
		return results
	
	def smsReadCount(self,onlyUnread: bool) -> int:
		"""
		Tutti i comandi che fanno operazioni di SELECT, UPDATE o DELETE richiedono il ROOT
		"""
		sql=self.__smsQuery(onlyUnread,True)
		output=self.__querySmsDb(sql)
		return int(output)
	
	def __smsQuery(self,onlyUnread:bool,isCount:bool)->str:
		sqlSelect="COUNT(*)" if isCount else "*,%s AS sep"%(self.__SEP_WITH_DELIM,)
		sql="SELECT %s FROM sms WHERE 1=1 %s;"%(sqlSelect,("AND read=0" if onlyUnread else ""),)
		return sql
	
	# operazioni di modifica / cancellazione
	def smsDelete(self,idSms:int)->str:
		"""
		Tutti i comandi che fanno operazioni di SELECT, UPDATE o DELETE richiedono il ROOT
		"""
		sql="DELETE FROM sms WHERE _id=%d;"%(idSms,)
		return self.__querySmsDb(sql)
	def smsUpdateAsRed(self,idSms:int)->str:
		"""
		Tutti i comandi che fanno operazioni di SELECT, UPDATE o DELETE richiedono il ROOT
		"""
		sql="UPDATE sms SET read=1 WHERE _id=%d AND read=0;"%(idSms,)
		return self.__querySmsDb(sql)
	def smsUpdateManyAsRed(self,idsSms:list[int])->str|None:
		"""
		Tutti i comandi che fanno operazioni di SELECT, UPDATE o DELETE richiedono il ROOT
		"""
		if not idsSms:
			return None
		idsSmsStr=",".join(str(x) for x in idsSms)
		sql="UPDATE sms SET read=1 WHERE _id IN(%s) AND read=0;"%(idsSmsStr,)
		return self.__querySmsDb(sql)
		
	def __querySmsDb(self,sqlQuery:str)->str:
		"""
		Richiede il ROOT sul device
		"""
		cmd=r'''adb -s "%s" shell "su -c 'sqlite3 "/data/data/com.android.providers.telephony/databases/mmssms.db" \"%s\"'" '''%(self.deviceId,sqlQuery)
		output=ModuloSystem.systemCallReturnOutput(cmd,None).strip()
		output=ModuloStringhe.normalizzaEol(output)
		return output
	
	def smsSend(self,unlockPin:int,numeroDest:str,msg:str)->str:
		msg=msg.replace(" ",r"\ ")
		# premo invio prima di inserire il pin, in questo modo forzo il focus sull'input text
		cmd=r"""adb -s "%s" shell "input keyevent KEYCODE_POWER && sleep 1 && input keyevent KEYCODE_ENTER && sleep 0.5"
adb -s "%s" shell "input text \"%d\" && sleep 0.5 && input keyevent KEYCODE_ENTER"
adb -s "%s" shell am start -a android.intent.action.SENDTO -d sms:"%s" --es sms_body "%s" --ez exit_on_sent true
adb -s "%s" shell "sleep 2 && input keyevent 61 && sleep 0.5 && input keyevent KEYCODE_ENTER && sleep 0.5 && am force-stop com.android.mms && input keyevent KEYCODE_POWER && echo \"FINE\""
"""%(self.deviceId,
	self.deviceId,unlockPin,
	self.deviceId,numeroDest,msg,
	self.deviceId)
		output=ModuloStringhe.normalizzaEol(ModuloSystem.systemCallReturnOutput(cmd,None)).strip()
		return output
