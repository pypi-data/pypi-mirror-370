from pydantic import BaseModel, field_validator
from typing import Literal, Optional


class Ggut(BaseModel):
    satzart: Literal["GGUT"] = "GGUT"
    tladenr: str
    aufnr: int
    lfdnrggut: int
    aufposnr: Optional[int] = None
    klasse: str
    klassecode: Optional[str] = None
    verpackgrp: Optional[str] = None
    befkat: Optional[str] = None
    befvorschr: Optional[str] = None
    unnummer: str
    nrgefahr: Optional[str] = None
    begrmenge: Optional[str] = None
    verpart: Optional[str] = None
    anzvpe: Optional[float] = None
    gewicht: Optional[float] = None
    gewichtbrt: Optional[float] = None
    gewichtnet: Optional[float] = None
    cdmanz: Optional[float] = None
    flammpunkt: Optional[float] = None
    multiplika: Optional[float] = None
    stoffname: Optional[str] = None
    chemname: Optional[str] = None
    buchstabe: Optional[str] = None
    nebengf1: Optional[str] = None
    nebengf2: Optional[str] = None
    nebengf3: Optional[str] = None
    nve: Optional[str] = None
    sonvorschr: Optional[str] = None
    nagtext: Optional[str] = None
    gefahrzett: Optional[str] = None
    tunnelcode: Optional[str] = None
    punkte: Optional[float] = None
    herausgeb: Optional[str] = None
    liskatnr: Optional[int] = None
    unnr_lfdnr: Optional[int] = None
    un_lfdnr: Optional[int] = None
    freimenge: Optional[str] = None
    vertraeggr: Optional[str] = None
    umweltgef: Optional[bool] = None

    @field_validator("umweltgef")
    @classmethod
    def validate_boolean(cls, value):
        if value not in {None, True, False}:
            raise ValueError("Invalid boolean value")
        if value == False:
            return "N"  # Nein
        elif value == True:
            return "J"  # Ja
        return value
