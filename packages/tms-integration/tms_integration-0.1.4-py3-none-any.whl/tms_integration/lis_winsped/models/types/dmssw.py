from pydantic import BaseModel, Field
from typing import Literal, Optional


class DmsSw(BaseModel):
    satzart: Literal["DMSSW"] = "DMSSW"
    referenz: str
    dmsdoknr: int
    dmsswnr: int
    schluessel: str
    wert: str
