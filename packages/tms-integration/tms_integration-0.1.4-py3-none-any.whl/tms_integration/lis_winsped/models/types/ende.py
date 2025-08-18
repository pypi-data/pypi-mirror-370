from typing import Literal
from pydantic import BaseModel, Field


class Ende(BaseModel):
    satzart: Literal["ENDE"] = "ENDE"
