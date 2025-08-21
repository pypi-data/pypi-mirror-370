from enum import IntEnum
from enum import auto
from enum import unique


@unique
class AndroidSmsTypeEnum(IntEnum):
	"""
	Tipi di sms/mms
	"""
	ALL=0
	RECEIVED=auto()
	SENT=auto()
	DRAFT=auto()
	OUTBOX=auto()
	FAILED_OUTGOING=auto()
	QUEUED=auto()
