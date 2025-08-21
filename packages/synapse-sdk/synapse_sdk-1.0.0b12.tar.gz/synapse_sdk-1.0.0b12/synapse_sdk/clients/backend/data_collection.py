from multiprocessing import Pool
from pathlib import Path
from typing import Dict, Optional

from tqdm import tqdm

from synapse_sdk.clients.base import BaseClient
from synapse_sdk.clients.utils import get_batched_list, get_default_url_conversion


class DataCollectionClientMixin(BaseClient):
    def list_data_collection(self):
        path = 'data_collections/'
        return self._list(path)

    def get_data_collection(self, data_collection_id):
        """Get data_collection from synapse-backend.

        Args:
            data_collection_id: The data_collection id to get.
        """
        path = f'data_collections/{data_collection_id}/?expand=file_specifications'
        return self._get(path)

    def create_data_file(self, file_path: Path):
        """Create data file to synapse-backend.

        Args:
            file_path: The file pathlib object to upload.
        """
        path = 'data_files/'
        return self._post(path, files={'file': file_path})

    def get_data_unit(self, data_unit_id: int, params=None):
        path = f'data_units/{data_unit_id}/'
        return self._get(path, params=params)

    def create_data_units(self, data):
        """Create data units to synapse-backend.

        Args:
            data: The data bindings to upload from create_data_file interface.
        """
        path = 'data_units/'
        return self._post(path, data=data)

    def list_data_units(self, params=None, url_conversion=None, list_all=False):
        path = 'data_units/'
        url_conversion = get_default_url_conversion(url_conversion, files_fields=['files'])
        return self._list(path, params=params, url_conversion=url_conversion, list_all=list_all)

    def upload_data_collection(
        self,
        data_collection_id: int,
        data_collection: Dict,
        project_id: Optional[int] = None,
        batch_size: int = 1000,
        process_pool: int = 10,
    ):
        """Upload data_collection to synapse-backend.

        Args:
            data_collection_id: The data_collection id to upload the data to.
            data_collection: The data_collection to upload.
                * structure:
                    - files: The files to upload. (key: file name, value: file pathlib object)
                    - meta: The meta data to upload.
            project_id: The project id to upload the data to.
            batch_size: The batch size to upload the data.
            process_pool: The process pool to upload the data.
        """
        # TODO validate data_collection with schema

        params = [(data, data_collection_id) for data in data_collection]

        with Pool(processes=process_pool) as pool:
            data_collection = pool.starmap(self.upload_data_file, tqdm(params))

        batches = get_batched_list(data_collection, batch_size)

        for batch in tqdm(batches):
            data_units = self.create_data_units(batch)

            if project_id:
                tasks_data = []
                for data, data_unit in zip(batch, data_units):
                    task_data = {'project': project_id, 'data_unit': data_unit['id']}
                    # TODO: Additional logic needed here if task data storage is required during import.

                    tasks_data.append(task_data)

                self.create_tasks(tasks_data)

    def upload_data_file(self, data: Dict, data_collection_id: int) -> Dict:
        """Upload files to synapse-backend.

        Args:
            data: The data to upload.
                * structure:
                    - files: The files to upload. (key: file name, value: file pathlib object)
                    - meta: The meta data to upload.
            data_collection_id: The data_collection id to upload the data to.

        Returns:
            Dict: The result of the upload.
        """
        for name, path in data['files'].items():
            data_file = self.create_data_file(path)
            data['data_collection'] = data_collection_id
            data['files'][name] = {'checksum': data_file['checksum'], 'path': str(path)}
        return data
