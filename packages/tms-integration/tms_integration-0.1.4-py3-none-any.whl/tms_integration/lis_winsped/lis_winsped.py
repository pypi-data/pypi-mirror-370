import os
import shutil
import tempfile

from typing import Union, Tuple, List
from pydantic.dataclasses import dataclass
from tms_integration.utils.sftp import SftpBase

from .models import LisIn


@dataclass
class LisWinSped(SftpBase):
    import_dest_folder: str
    output_target_folder: str

    def import_auftrag(self, payload: LisIn, import_prefix: str = None):
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="cp1252",  # FORCE ANSI encoding
            prefix=import_prefix,
            suffix=".txt",
            delete=False,
        ) as tmp_file:
            tmp_file.write(payload.generate_txt())
            tmp_file.close()
            self.import_file(tmp_file.name, self.import_dest_folder)

    def import_document(self, dms_payload, file: str, import_prefix: str = None):
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="cp1252",  # FORCE ANSI encoding
            prefix=import_prefix,
            suffix=".txt",
            delete=False,
        ) as tmp_file:
            tmp_file.write(dms_payload.generate_txt())
            tmp_file.close()
            self.import_file(tmp_file.name, self.import_dest_folder)

        # send the file as well
        self.import_file(file, self.import_dest_folder)

    def export_auftrag(
        self, identifier: str
    ) -> Union[Tuple[None, None], Tuple[str, str]]:
        output_files = self.get_all_files(self.output_target_folder)
        dest_path = os.path.join(os.getcwd(), "tmp", "output")
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        os.makedirs(dest_path)
        for file in output_files:
            filename = os.path.basename(file)
            self.export_file(file, os.path.join(dest_path, filename))
            with open(os.path.join(dest_path, filename), "r", encoding="cp1252") as txt:
                text = txt.read()
                if identifier in text:
                    return (file, text)

        return None, None

    def export_auftrag_tour(self, identifier: str) -> List[Tuple[str, str]]:
        output: List[Tuple[str, str]] = []
        output_files = self.get_all_files(self.output_target_folder)
        dest_path = os.path.join(os.getcwd(), "tmp", "output")
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        os.makedirs(dest_path)
        for file in output_files:
            filename = os.path.basename(file)
            self.export_file(file, os.path.join(dest_path, filename))
            with open(os.path.join(dest_path, filename), "r", encoding="cp1252") as txt:
                text = txt.read()
                if identifier in text:
                    output.append((file, text))

        return output
