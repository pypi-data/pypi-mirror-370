from enum import StrEnum
from enum import unique


@unique
class EnvVarsEnum(StrEnum):
	MODULITIZ_IS_DEBUG="MODULITIZ_IS_DEBUG"
	PATH="PATH"
	TMP="TMP"
