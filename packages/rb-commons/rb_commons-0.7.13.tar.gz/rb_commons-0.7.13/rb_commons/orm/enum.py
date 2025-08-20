from enum import Enum

class OriginType(str, Enum):
    MANUAL = "MANUAL"
    ETL = "ETL"
    API = "API"
    DEFAULT = "DEFAULT"
    BILLZ = "BILLZ"
    BITO = "BITO"
    SMARTUP = "SMARTUP"
    DIZGO = "DIZGO"

class MediaSource(str, Enum):
    ROBO = "ROBO"
    BILLZ = "BILLZ"
    BITO = "BITO"
    EUROPHARM = "EUROPHARM"
    DIZGO = "DIZGO"