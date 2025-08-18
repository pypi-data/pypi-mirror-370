import tempfile
from pydantic.dataclasses import dataclass
from tms_integration.utils.sftp import SftpBase

from .models.order import NormalOrderData


@dataclass
class SoloplanCarlo(SftpBase):
    import_dest_folder: str

    def import_auftrag(self, payload: NormalOrderData, import_prefix: str = None):
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            prefix=import_prefix,
            suffix=".xml",
            delete=False,
        ) as tmp_file:
            tmp_file.write(payload.generate_xml())
            tmp_file.close()
            self.import_file(tmp_file.name, self.import_dest_folder)

    def export_auftrag(self):
        raise NotImplementedError
