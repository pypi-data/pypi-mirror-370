from pydantic import BaseModel, Field, validator
from typing import Literal, Optional, Union
from datetime import datetime


class Lademi(BaseModel):
    satzart: Literal["LADEMI"] = "LADEMI"
    referenz: Optional[str] = None
    tladenr: Optional[str] = None
    aufnr: Union[str, int, None] = None
    aufposnr: Union[str, int, None] = None
    palanz: Optional[int] = None
    pal: Optional[str] = None
    laenge: Optional[Union[str, float]] = None
    breite: Optional[Union[str, float]] = None
    hoehe: Optional[Union[str, float]] = None
    eigengew: Optional[Union[str, float]] = None
    nve: Optional[str] = None
    lmart: Union[str, int]
    waufragid: Optional[Union[str, int]] = None
    waufposid: Optional[Union[str, int]] = None
    einhgew: Optional[str] = None
    einhlaenge: Optional[str] = None
    einhbreite: Optional[str] = None
    einhhoehe: Optional[str] = None
    lageplatz: Optional[str] = None
