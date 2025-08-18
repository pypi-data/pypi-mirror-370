from pydantic import BaseModel, field_validator
from typing import Optional, Literal, Union
from datetime import datetime


class Ladeli(BaseModel):
    satzart: Literal["LADELI"] = "LADELI"
    referenz: str
    tladenr: str
    lkwpolkz: Optional[str] = None
    anhpolkz: Optional[str] = None
    fahid: Optional[int] = None
    fahname: Optional[str] = None
    ffiln: Optional[str] = None
    ffempid: Optional[str] = None
    ffname: Optional[str] = None
    abruf: Optional[str] = None
    tournr: Optional[str] = None
    tsmittel: Optional[str] = None
    exportiert: Optional[Union[str, bool]] = None
    wtourid: Optional[int] = None
    borderonr: Optional[str] = None
    tlade_datum: Optional[datetime] = None
    wechselbruecke1: Optional[str] = None
    wechselbruecke2: Optional[str] = None
    telefon: Optional[str] = None
    kmlast: Optional[float] = None
    kmmaut: Optional[float] = None
    dispo_user: Optional[str] = None
    ffpausch: Optional[float] = None
    lkwgrpid: Optional[str] = None
    tourzeit: Optional[str] = None
    entbisdat: Optional[datetime] = None
    entbiszeit: Optional[str] = None
    verkart: Optional[str] = None
    lposnr: Optional[str] = None
    lpospausch: Optional[float] = None
    tourinfo1: Optional[str] = None
    tourinfo2: Optional[str] = None
    tourinfo3: Optional[str] = None
    tourinfo4: Optional[str] = None
    tourinfo5: Optional[str] = None
    tourinfo6: Optional[str] = None
    tourinfo7: Optional[str] = None
    tourinfo8: Optional[str] = None
    tourinfo9: Optional[str] = None
    tourinfo10: Optional[str] = None
    dispous: Optional[str] = None
    fahvorname: Optional[str] = None
    bfahid: Optional[int] = None
    bfahname: Optional[str] = None
    bfahvorname: Optional[str] = None
    ffpwaehr: Optional[str] = None
    lppwaehr: Optional[str] = None
    aendstatus: Optional[str] = None
    abteilung: Optional[int] = None
    lkw: Optional[str] = None
    anh: Optional[str] = None
    bereich: Optional[int] = None
    plombe1: Optional[str] = None
    plombe2: Optional[str] = None
    kmleer: Optional[float] = None
    kmleermaut: Optional[float] = None
    kmlastist: Optional[float] = None
    kmleerist: Optional[float] = None

    @field_validator("tlade_datum", "entbisdat", mode="before")
    @classmethod
    def parse_date(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y%m%d")
        return value

    @field_validator("tourzeit", "entbiszeit", mode="before")
    @classmethod
    def parse_time(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%H%M").time().strftime("%H%M")
        return value

    @field_validator("aendstatus")
    @classmethod
    def validate_aendstatus(cls, value):
        if value and value not in {"N", "A"}:
            raise ValueError("Invalid Aendstatus value")
        return value

    @field_validator("exportiert")
    @classmethod
    def validate_exportiert(cls, value):
        if value in {True, "J", "j"}:
            return "J"
        elif value in {False, "N", "n"}:
            return "N"
        elif value is None:
            return None
        raise ValueError("exportiert must be 'J', 'N', True, False or None")
