import mysql.connector

class EccezioneMysqlOffline(mysql.connector.InterfaceError):
	
	def __init__(self,*args,**kwargs):
		super().__init__(*args,**kwargs)
