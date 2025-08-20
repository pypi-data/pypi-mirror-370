"""" This module contains functions for generating file metadata. """
import base64
import hashlib
import os
from dataclasses import dataclass
from typing import List


@dataclass
class FilePart:
    """Class to hold part number and sha1 checksum for a part of the file"""

    part_number: int
    sha1_checksum: str


@dataclass
class FileMetadata:
    """Class to hold metadata for a file"""

    name: str
    size: int
    part_size: int
    file_path: str
    # AWS CompleteUpload Requirement: This sha1 checksum has to be
    # the digest of the combined sha1 checksums of all the parts of the file
    # appended with -<number of parts>
    sha1_checksum: str
    parts: List[FilePart]

    def __init__(self, file_path: str, part_size: int):
        self.name = os.path.basename(file_path)
        self.size = os.path.getsize(file_path)
        self.part_size = part_size
        self.file_path = file_path
        self.parts = []
        self.sha1_checksum = ""
        self.__post_init__()

    def __post_init__(self):
        part_digests = []
        with open(self.file_path, "rb") as f:
            part_number = 1
            while True:
                data = f.read(self.part_size)
                if not data:
                    break

                part_digest = hashlib.sha1(data).digest()
                part_digests.append(part_digest)
                self.parts.append(
                    FilePart(part_number, base64.b64encode(part_digest).decode("utf-8"))
                )
                part_number += 1
            combined_digest = b"".join(part_digests)
            file_hash = hashlib.sha1(combined_digest)
            self.sha1_checksum = base64.b64encode(file_hash.digest()).decode("utf-8")
