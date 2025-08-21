import shutil
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import io
import time

from .kawa_log_manager import get_kawa_logger

dataset = 'dataset'
etl_preview = 'etl_preview'
repo = 'repo'
log = 'log'
pex = 'pex'
metadata = 'metadata'


folders = [dataset, etl_preview, repo, log, pex, metadata]


class KawaDirectoryManager:

    def __init__(self,
                 working_directory: Path):
        self._working_directory = working_directory
        self._working_directory.mkdir(exist_ok=True)
        self._ensure_directories()

    def _ensure_directories(self):
        for folder in folders:
            (self._working_directory / folder).mkdir(parents=True, exist_ok=True)

    def dataset_path(self, job_id: str):
        return self._working_directory / dataset / job_id

    def etl_preview_path(self, job_id: str):
        return self._working_directory / etl_preview / job_id

    def repo_path(self, job_id: str):
        return self._working_directory / repo / job_id

    def log_path(self, job_id: str):
        return self._working_directory / log / job_id

    def metadata_path(self, job_id: str):
        return self._working_directory / metadata / job_id

    def create_log_file(self, job_id: str):
        self.log_path(job_id).touch()

    def pex_path(self):
        return self._working_directory / pex

    def repository_root_path(self):
        return self._working_directory / repo

    def working_directory(self):
        return self._working_directory

    def write_table(self, job_id: str, data_table: pa.Table):
        try:
            pq.write_table(data_table, self.dataset_path(job_id))
        except Exception as err:
            get_kawa_logger().error(f'Issue when writing the table for job_id: {job_id}: {err}')
            raise err

    def read_table(self, job_id: str) -> pa.Table:
        try:
            return pq.read_table(self.dataset_path(job_id))
        except Exception as err:
            get_kawa_logger().error(f'Issue when reading the table for job_id: {job_id}: {err}')
            raise err

    def write_json_etl_preview(self, job_id: str, json: str):
        try:
            with io.open(self.etl_preview_path(job_id), 'w', encoding='utf8') as f:
                f.write(json)
        except Exception as err:
            get_kawa_logger().error(f'Issue writing the json of the elt preview for job_id: {job_id}: {err}')
            raise err

    def read_json_etl_preview(self, job_id: str) -> str:
        try:
            with io.open(self.etl_preview_path(job_id), 'r', encoding='utf8') as f:
                etl_preview = f.read()
            return etl_preview
        except Exception as err:
            get_kawa_logger().error(f'Issue reading the json of the elt preview for job_id: {job_id}: {err}')
            raise err

    def write_json_metadata(self, job_id: str, json: str):
        try:
            with io.open(self.metadata_path(job_id), 'w', encoding='utf8') as f:
                f.write(json)
        except Exception as err:
            get_kawa_logger().error(f'Issue writing the metadata for jobId: {job_id}: {err}')
            raise err

    def read_json_metadata(self, job_id: str) -> str:
        try:
            with io.open(self.metadata_path(job_id), 'r', encoding='utf8') as f:
                metadata = f.read()
            return metadata
        except Exception as err:
            get_kawa_logger().error(f'Issue reading the metadata for jobId: {job_id}: {err}')
            raise err

    def remove_job_working_files(self, job_id):
        get_kawa_logger().debug('Remove working files for job: %s', job_id)
        self._remove_file_if_exists(self.dataset_path(job_id))

    def remove_repo_files(self, job_id):
        get_kawa_logger().debug('Remove repo files for job: %s', job_id)
        self._remove_folder_and_files_if_exists(self.repo_path(job_id))

    def remove_job_log(self, job_id):
        get_kawa_logger().debug('Remove log file for job: %s', job_id)
        self._remove_file_if_exists(self.log_path(job_id))

    def remove_etl_preview(self, job_id):
        get_kawa_logger().debug('Remove etl preview file: %s', job_id)
        self._remove_file_if_exists(self.etl_preview_path(job_id))

    def remove_metadata(self, job_id):
        get_kawa_logger().debug('Remove metadata file: %s', job_id)
        self._remove_file_if_exists(self.metadata_path(job_id))

    def remove_files_older_than(self, max_age: int):
        self._remove_files_older_than(max_age, '*/*')

    def _remove_files_older_than(self, max_age: int, pattern: str):
        for item in self._working_directory.glob(pattern):
            if item.is_file():
                modification_time = item.stat().st_mtime
                if time.time() - modification_time > max_age:
                    self._remove_file_if_exists(item)

    @staticmethod
    def _remove_file_if_exists(file):
        try:
            get_kawa_logger().debug('remove file: %s' + file.name)
            file.unlink()
        except Exception:
            pass

    @staticmethod
    def _remove_folder_and_files_if_exists(file):
        try:
            get_kawa_logger().debug('remove path: %s' + file.name)
            shutil.rmtree(file)
        except Exception:
            pass

    @staticmethod
    def is_dataset_file(file):
        return file.name().endswith('_dataset')
