from modulitiz_micro.ModuloDate import ModuloDate
from modulitiz_micro.android.enums.AndroidSmsTypeEnum import AndroidSmsTypeEnum


class SmsBean(object):
	def __init__(self,arr:list[str]):
		self.id=int(arr[0])
		self.numCell=arr[2]
		self.data=ModuloDate.timestampToDate(int(arr[4])*0.001)
		self.dataInvio=ModuloDate.timestampToDate(int(arr[5])*0.001)
		self.type=AndroidSmsTypeEnum(int(arr[9])).name.lower()
		self.body=arr[12]
