from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from datetime import datetime


class Start(BaseModel):
    satzart: Literal["START"] = "START"
    referenz: str
    erstellt: datetime
    eigiln: Optional[str] = None
    eigkreid: Optional[str] = None
    eigname1: str
    expiln: Optional[str] = None
    expempid: Optional[str] = None
    expname1: str
    impart: Optional[int] = None
    maplfdnr: Optional[int] = None
    status: Optional[str] = None
    versinfo: Optional[str] = None
    skalierungtext1: Optional[str] = None
    skalierungtext2: Optional[str] = None
    skalierungtext3: Optional[str] = None
    skalierungzahl1: Optional[int] = None
    skalierungzahl2: Optional[int] = None
    skalierungdatum1: Optional[datetime] = None
    skalierungdatum2: Optional[datetime] = None

    @field_validator("erstellt", "skalierungdatum1", "skalierungdatum2", mode="before")
    @classmethod
    def parse_datetime(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y%m%d%H%M%S")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        if value and value not in {"D", "L", "Z", "E", "F"}:
            raise ValueError("Invalid status value")
        return value
