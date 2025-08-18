from pydantic import BaseModel
from typing import Literal, Optional


class DmsDok(BaseModel):
    satzart: Literal["DMSDOK"] = "DMSDOK"
    referenz: str
    dmsdoknr: int
    archiv: str
    ordner: str
    doktyp: str
    quellpfad: str
    aendstatus: Optional[str] = None
