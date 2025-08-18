import os
import pysftp

from typing import Optional
from pydantic import BaseModel
from pydantic.dataclasses import dataclass


class SftpConfig(BaseModel):
    host: str
    port: int = 22
    username: Optional[str] = None
    password: Optional[str] = None
    private_key: Optional[str] = None
    private_key_pass: Optional[str] = None
    no_host_key: bool = False
    cnopts: Optional[pysftp.CnOpts] = None

    class Config:
        arbitrary_types_allowed = True


@dataclass
class SftpBase:
    config: SftpConfig

    def __post_init__(self):
        if self.config.no_host_key:
            self.config.cnopts = pysftp.CnOpts()
            self.config.cnopts.hostkeys = None
        conn = pysftp.Connection(
            host=self.config.host,
            port=self.config.port,
            username=self.config.username,
            password=self.config.password,
            private_key=self.config.private_key,
            private_key_pass=self.config.private_key_pass,
            cnopts=self.config.cnopts,
        )
        conn.close()

    def import_file(self, source_filepath: str, dest_path: str) -> None:
        """
        Uploads a file from the source path to the destination path on the SFTP server.

        Args:
            credentials: The credentials required to establish an SFTP connection.
            source_filepath: The local path of the file to be uploaded.
            dest_path: The destination path on the SFTP server where the file will be uploaded.
        """
        with pysftp.Connection(
            host=self.config.host,
            port=self.config.port,
            username=self.config.username,
            password=self.config.password,
            private_key=self.config.private_key,
            private_key_pass=self.config.private_key_pass,
            cnopts=self.config.cnopts,
        ) as sftp:
            filename = os.path.basename(source_filepath)
            dest_filepath = f"{dest_path}/{filename}"
            sftp.put(source_filepath, dest_filepath)

    def export_file(self, remote_filepath: str, local_filepath: str) -> None:
        """
        Export a file from a remote SFTP server using the provided credentials.

        Args:
            remote_filepath (str): The file path on the remote SFTP server.
            local_filepath (str): The local file path where the downloaded file will be saved.
        """
        with pysftp.Connection(
            host=self.config.host,
            port=self.config.port,
            username=self.config.username,
            password=self.config.password,
            private_key=self.config.private_key,
            private_key_pass=self.config.private_key_pass,
            cnopts=self.config.cnopts,
        ) as sftp:
            sftp.get(remote_filepath, local_filepath)

    def get_all_files(self, remote_folder: str):
        """Export all the files from a specific remove SFTP direction using the provided credentials

        Args:
            remote_folder (str): The directory from which the files should be taken
            local_folder (str): The local folder path where the downloaded files will be saved.
        """
        remote_files = []

        with pysftp.Connection(
            host=self.config.host,
            port=self.config.port,
            username=self.config.username,
            password=self.config.password,
            private_key=self.config.private_key,
            private_key_pass=self.config.private_key_pass,
            cnopts=self.config.cnopts,
        ) as sftp:
            with sftp.cd(remote_folder):
                files = sftp.listdir()
                for file_name in files:
                    remote_filepath = f"{remote_folder}/{file_name}"
                    remote_files.append(remote_filepath)

        return remote_files

    def delete_file(self, remote_filepath: str):
        """Remove a file from a remote SFTP sever

        Args:
            remote_filepath (str): the file path ont he remove SFTP sever
        """
        with pysftp.Connection(
            host=self.config.host,
            port=self.config.port,
            username=self.config.username,
            password=self.config.password,
            private_key=self.config.private_key,
            private_key_pass=self.config.private_key_pass,
            cnopts=self.config.cnopts,
        ) as sftp:
            if sftp.exists(remote_filepath):
                sftp.remove(remote_filepath)
