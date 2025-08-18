from typing import List, Optional
from datetime import datetime, time
from pydantic import BaseModel

from .types import *


class LisIn(BaseModel):
    start: Start
    records: List[RecordTypes] = []
    ende: Optional[Ende] = None

    def validate_records(self):
        raise NotImplemented

    @staticmethod
    def model_to_line(model):
        fields = []
        for field_key in model.__fields__.keys():
            field_value = model.dict().get(field_key)
            if field_value is not None:
                if isinstance(field_value, datetime):
                    fields.append(field_value.strftime("%Y%m%d"))
                elif isinstance(field_value, time):
                    fields.append(field_value.strftime("%H%M"))
                else:
                    fields.append(str(field_value))
            else:
                fields.append("")
        return "|".join(fields)

    def generate_txt(self) -> str:
        self.validate_records()
        lines = []

        lines.append(self.model_to_line(self.start))
        for record in self.records:
            lines.append(self.model_to_line(record))
        if self.ende:
            lines.append(self.model_to_line(self.ende))

        return "\n".join(lines)


class LisInAuftrag(LisIn):
    mandatory_records_type: List = [Auftrag, Adr, Ladeli, Posit]

    def validate_records(self):
        records_type = {type(r) for r in self.records}
        types_missing = set(self.mandatory_records_type) - records_type
        if types_missing:
            raise ValueError(f"Some mandatory types are missing: {types_missing}")


class LisInDMS(LisIn):
    mandatory_records_type: List = [DmsDok, DmsRef, DmsSw]

    def validate_records(self):
        records_type = {type(r) for r in self.records}
        types_missing = set(self.mandatory_records_type) - records_type
        if types_missing:
            raise ValueError(f"Some mandatory types are missing: {types_missing}")
