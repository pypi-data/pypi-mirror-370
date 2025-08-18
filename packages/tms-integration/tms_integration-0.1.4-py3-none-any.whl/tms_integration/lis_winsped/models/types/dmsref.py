from pydantic import BaseModel, Field
from typing import Literal, Optional


class DmsRef(BaseModel):
    satzart: Literal["DMSREF"] = "DMSREF"
    referenz: str
    dmsdoknr: int
    dmsrefnr: int
    aufnr: int
    kundennr: Optional[str] = None
    liefnr: Optional[str] = None
    refnr: Optional[str] = None
    kommnr: Optional[str] = None
