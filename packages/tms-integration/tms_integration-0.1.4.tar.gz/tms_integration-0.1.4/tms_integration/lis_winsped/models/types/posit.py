from pydantic import BaseModel, field_validator
from typing import Optional, Union, Literal
from datetime import datetime


class Posit(BaseModel):
    satzart: Literal["POSIT"] = "POSIT"
    referenz: Optional[str] = None
    tladenr: Optional[str] = None
    aufnr: Optional[int] = None
    aufposnr: Optional[int] = None
    refpos: Optional[str] = None
    tatsgew: Optional[Union[str, float]] = None
    fpflgew: Optional[Union[str, float]] = None
    ean: Optional[str] = None
    artnre: Optional[str] = None
    artnrl: Optional[str] = None
    artikel: Optional[str] = None
    zeichen: Optional[str] = None
    inhalt: Optional[str] = None
    tarifid: Optional[str] = None
    ggutklasse: Optional[str] = None
    ggutunr: Optional[str] = None
    ggutziffer: Optional[str] = None
    ggutgew: Optional[Union[str, float]] = None
    cdmanz: Optional[Union[str, float]] = None
    lmanz: Optional[Union[str, float]] = None
    qmanz: Optional[Union[str, float]] = None
    spanz: Optional[Union[str, float]] = None
    smenge: Optional[Union[str, float]] = None
    imenge: Optional[Union[str, float]] = None
    warenwert: Optional[Union[str, float]] = None
    qualitaet: Optional[int] = None
    wauftragid: Optional[int] = None
    waufposid: Optional[int] = None
    einhgew: Optional[str] = None
    einhvol: Optional[str] = None
    einhlaenge: Optional[str] = None
    einhflaech: Optional[str] = None
    tgew: Optional[Union[str, float]] = None
    hoehe: Optional[Union[str, float]] = None
    breite: Optional[Union[str, float]] = None
    laenge: Optional[Union[str, float]] = None
    taragew: Optional[Union[str, float]] = None
    stapelhoe: Optional[float] = None
    kammer: Optional[str] = None
    inhalt2: Optional[str] = None
    hbuchkto: Optional[str] = None
    kostena: Optional[str] = None
    innenaufnr: Optional[str] = None
    vertrieb: Optional[int] = None
    matart: Optional[str] = None
    matgrp: Optional[str] = None
    sparte: Optional[str] = None
    gklasse: Optional[str] = None
    ggruppe: Optional[str] = None
    verswert: Optional[Union[str, float]] = None
    shilf1: Optional[str] = None
    shilf2: Optional[str] = None
    shilf3: Optional[str] = None
    lhilf1: Optional[int] = None
    lhilf2: Optional[int] = None
    dtmhilf1: Optional[datetime] = None
    dtmhilf2: Optional[datetime] = None
    curhilf1: Optional[Union[str, float]] = None
    curhilf2: Optional[Union[str, float]] = None
    pspelement: Optional[str] = None
    befkat: Optional[str] = None
    fz: Optional[int] = None
    aendstatus: Optional[str] = None
    solttatsgew: Optional[Union[str, float]] = None
    sollpalanze: Optional[Union[str, float]] = None
    sollvpeanz: Optional[Union[str, float]] = None
    sollmeanz: Optional[Union[str, float]] = None
    sollspanz: Optional[Union[str, float]] = None
    beltxt: Optional[str] = None
    leergut: Optional[int] = None
    umweltgef: Optional[str] = None  # Changed from Optional[bool]
    curhilf3: Optional[Union[str, float]] = None
    curhilf4: Optional[Union[str, float]] = None
    curhilf5: Optional[Union[str, float]] = None
    curhilf6: Optional[Union[str, float]] = None
    curhilf7: Optional[Union[str, float]] = None

    @field_validator("dtmhilf1", "dtmhilf2", mode="before")
    @classmethod
    def parse_datetime(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y%m%d")
        return value

    @field_validator("aendstatus")
    @classmethod
    def validate_aendstatus(cls, value):
        if value and value not in {"N", "A", "L"}:
            raise ValueError("Invalid Aendstatus value")
        return value

    @field_validator("umweltgef")
    @classmethod
    def validate_umweltgef(cls, value):
        if value in {True, "J", "j"}:
            return "J"
        elif value in {False, "N", "n"}:
            return "N"
        elif value is None:
            return None
        raise ValueError("umweltgef must be 'J', 'N', True, False or None")
