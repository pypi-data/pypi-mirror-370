import hashlib
import os
from pathlib import Path

from synapse_sdk.clients.base import BaseClient


class CoreClientMixin(BaseClient):
    def create_chunked_upload(self, file_path):
        def read_file_in_chunks(file_path, chunk_size=1024 * 1024 * 50):
            with open(file_path, 'rb') as file:
                while chunk := file.read(chunk_size):
                    yield chunk

        file_path = Path(file_path)
        size = os.path.getsize(file_path)
        hash_md5 = hashlib.md5()

        url = 'chunked_upload/'
        offset = 0
        for chunk in read_file_in_chunks(file_path):
            hash_md5.update(chunk)
            data = self._put(
                url,
                data={'filename': file_path.name},
                files={'file': chunk},
                headers={'Content-Range': f'bytes {offset}-{offset + len(chunk) - 1}/{size}'},
            )
            offset = data['offset']
            url = data['url']

        return self._post(url, data={'md5': hash_md5.hexdigest()})
