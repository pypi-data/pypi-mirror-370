from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from datetime import datetime, time


class Auftrag(BaseModel):
    satzart: Literal["AUFTR"] = "AUFTR"
    referenz: str
    tladenr: str
    aufnr: Optional[int] = None
    liefnr: Optional[str] = None
    lieftxt: Optional[str] = None
    aufdatum: Optional[datetime] = None
    belvondat: Optional[datetime] = None
    belvonzeit: Optional[time] = None
    belbisdat: Optional[datetime] = None
    belbiszeit: Optional[time] = None
    entvondat: Optional[datetime] = None
    entvonzeit: Optional[time] = None
    entbisdat: Optional[datetime] = None
    entbiszeit: Optional[time] = None
    lagnr: Optional[str] = None
    lagauftrag: Optional[str] = None
    verkart: Optional[str] = None
    frankatur: Optional[str] = None
    fnach: Optional[float] = None
    fnachfrei: Optional[float] = None
    wnachfrei: Optional[float] = None
    bar: Optional[bool] = None
    vorkosten: Optional[float] = None
    gefahrgut: Optional[bool] = None
    kuehlgut: Optional[bool] = None
    direkt: Optional[bool] = None
    komnr: Optional[str] = None
    chargenr: Optional[str] = None
    km: Optional[float] = None
    aufklasse: Optional[str] = None
    kostenst: Optional[int] = None
    refnr: Optional[str] = None
    rel: Optional[str] = None
    aendstatus: Optional[str] = None
    wwwaehr: Optional[str] = None
    wauftragid: Optional[int] = None
    ktraeger: Optional[int] = None
    fobfrank: Optional[str] = None
    dispoinfo1: Optional[str] = None
    dispoinfo2: Optional[str] = None
    dispoinfo3: Optional[str] = None
    dispoinfo4: Optional[str] = None
    ffpausch: Optional[float] = None
    fzpausch: Optional[float] = None
    belfixdat: Optional[datetime] = None
    belfixzeit: Optional[time] = None
    entfixdat: Optional[datetime] = None
    entfixzeit: Optional[time] = None
    tmittel: Optional[int] = None
    tvpausch: Optional[float] = None
    aufunternr: Optional[int] = None
    ablauf: Optional[int] = None
    aufart: Optional[str] = None
    borderonr: Optional[str] = None
    belsolldat: Optional[datetime] = None
    belsollzeit: Optional[time] = None
    entsolldat: Optional[datetime] = None
    entsollzeit: Optional[time] = None
    dsinr: Optional[str] = None
    erfdr: Optional[int] = None
    abteilung: Optional[int] = None
    bereich: Optional[int] = None
    ffpwaehr: Optional[str] = None
    fzpwaehr: Optional[str] = None
    dosnr: Optional[str] = None
    dispoinfo5: Optional[str] = None
    dispoinfo6: Optional[str] = None
    dispoinfo7: Optional[str] = None
    dispoinfo8: Optional[str] = None
    dispoinfo9: Optional[str] = None
    dispoinfo10: Optional[str] = None
    tourlfdnr: Optional[int] = None
    belsolldatbis: Optional[datetime] = None
    belsollzeitbis: Optional[time] = None
    entsolldatbis: Optional[datetime] = None
    entsollzeitbis: Optional[time] = None
    belfixdatbis: Optional[datetime] = None
    belfixzeitbis: Optional[time] = None
    entfixdatbis: Optional[datetime] = None
    entfixzeitbis: Optional[time] = None
    fnachw: Optional[str] = None
    wnachfreiw: Optional[str] = None
    vdisintnr: Optional[int] = None
    renettoant: Optional[float] = None
    gsnettoant: Optional[float] = None
    eigenuser: Optional[str] = None
    sollgew: Optional[float] = None
    austourent: Optional[int] = None
    vdisnrext: Optional[str] = None
    umweltgef: Optional[bool] = None
    kontotab: Optional[int] = None
    dlaart: Optional[str] = None

    @field_validator(
        "aufdatum",
        "belvondat",
        "belbisdat",
        "entvondat",
        "entbisdat",
        "belfixdat",
        "entfixdat",
        "belsolldat",
        "entsolldat",
        "belsolldatbis",
        "entsolldatbis",
        "belfixdatbis",
        "entfixdatbis",
        mode="before",
    )
    @classmethod
    def parse_date(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y%m%d")
        return value

    @field_validator(
        "belvonzeit",
        "belbiszeit",
        "entvonzeit",
        "entbiszeit",
        "belfixzeit",
        "entfixzeit",
        "belsollzeit",
        "entsollzeit",
        "belsollzeitbis",
        "entsollzeitbis",
        "belfixzeitbis",
        "entfixzeitbis",
        mode="before",
    )
    @classmethod
    def parse_time(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%H%M").time()
        return value

    @field_validator("aendstatus")
    @classmethod
    def validate_aendstatus(cls, value):
        if value and value not in {"N", "A", "L", "W"}:
            raise ValueError("Invalid Aendstatus value")
        return value

    @field_validator("bar", "gefahrgut", "kuehlgut", "direkt", "umweltgef")
    @classmethod
    def validate_boolean(cls, value):
        if value not in {None, True, False}:
            raise ValueError("Invalid boolean value")
        if value == False:
            return "N"  # Nein
        elif value == True:
            return "J"  # Ja
        return value
