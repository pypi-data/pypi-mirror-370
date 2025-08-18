from datetime import datetime, time
from typing import Literal, Optional
from pydantic import BaseModel, Field


class Status(BaseModel):
    satzart: Literal["STATUS"] = "STATUS"
    referenz: str
    tladenr: str
    aufnr: int
    aufposnr: Optional[int] = None
    refpos: Optional[str] = None
    aufintnr: Optional[int] = None
    statusnr: str
    diffmenge: Optional[float] = None
    diffeinh: Optional[str] = None
    hinweis: Optional[str] = None
    statusdat: Optional[datetime] = None
    statuszeit: Optional[time] = None
    ean: Optional[str] = None
    refnr: Optional[str] = None
    ffnr: Optional[int] = None
    lkw: Optional[str] = None
    belvondat: Optional[datetime] = None
    tournr: Optional[str] = None
    tatsgew: Optional[float] = None
    waehrung: Optional[str] = None
    gsbetrag: Optional[float] = None
    rebetrag: Optional[float] = None
    aufart: Optional[str] = None
    belvonzeit: Optional[time] = None
    statusbez: Optional[str] = None
    kstelle: Optional[int] = None
    ktotab: Optional[str] = None
    wtourid: Optional[int] = None
    wauftragid: Optional[int] = None
    wauftposid: Optional[int] = None
    ktraeger: Optional[int] = None
    entbisdat: Optional[datetime] = None
    entbiszeit: Optional[time] = None
    kommnr: Optional[str] = None
    aenddat: Optional[datetime] = None
    aendus: Optional[str] = None
    statusart: Optional[int] = None
    quitgeber: Optional[str] = None
    aufunternr: Optional[int] = None
    liefnr: Optional[str] = None
    ffpausch: Optional[float] = None
    stalfdnr: Optional[int] = None
    lkwpolkz: Optional[str] = None
    anh: Optional[str] = None
    anhpolkz: Optional[str] = None
    fahld: Optional[int] = None
    bfahld: Optional[int] = None
