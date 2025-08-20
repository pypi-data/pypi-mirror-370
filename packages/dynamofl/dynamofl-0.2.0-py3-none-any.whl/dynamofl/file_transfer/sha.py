import base64
import hashlib
from io import BufferedReader

CHUNK_SIZE = 1024 * 1024  # 1MB


def calculate_sha1_hash_base64(f: BufferedReader):
    # Read the file in chunks
    sha1 = hashlib.sha1()
    file_size = 0
    while True:
        data = f.read(CHUNK_SIZE)
        if not data:
            break
        sha1.update(data)
        file_size += len(data)
    # Seek back to the beginning of the file
    f.seek(0)
    return base64.b64encode(sha1.digest()).decode("utf-8"), file_size
