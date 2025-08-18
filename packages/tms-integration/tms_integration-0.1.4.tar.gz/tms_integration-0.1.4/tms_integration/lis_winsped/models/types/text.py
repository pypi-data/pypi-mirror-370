from pydantic import BaseModel, field_validator
from typing import Optional, Literal
from datetime import datetime


class Text(BaseModel):
    satzart: Literal["TEXT"] = "TEXT"
    referenz: str
    tladenr: str
    aufnr: int
    txtartnr: int
    txtstr1: str
    gtext: Optional[str] = None  # changed from Optional[bool]
    txtstr2: Optional[str] = None
    txtstr3: Optional[str] = None
    txtstr4: Optional[str] = None
    txtstr5: Optional[str] = None
    txtdatum: Optional[datetime] = None

    @field_validator("txtdatum", mode="before")
    @classmethod
    def parse_date(cls, value):
        if isinstance(value, str):
            return datetime.strptime(value, "%Y%m%d")
        return value

    @field_validator("gtext")
    @classmethod
    def validate_gtext(cls, value):
        if value in {True, "J", "j"}:
            return "J"
        elif value in {False, "N", "n"}:
            return "N"
        elif value is None:
            return None
        raise ValueError("gtext must be 'J', 'N', True, False, or None")
