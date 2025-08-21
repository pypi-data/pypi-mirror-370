import codecs
import hashlib
import json
import string
import random
import time
from typing import List

import requests
import urllib3

from ..kawa_log_manager import get_kawa_logger
from ...server.aes_cipher import AesCipher


class JobManagerClient:

    def __init__(self, kawa_url: str, aes_key: str):
        self.kawa_url = kawa_url
        self.aes_key = aes_key
        self._service_path = '/python-job-manager'
        self.last_health_error = time.time()
        urllib3.disable_warnings()

    def healthy(self) -> bool:
        try:
            res = self._get_request('/healthcheck')
            res.raise_for_status()
            return True
        except Exception as e:
            if time.time() - self.last_health_error > 10:
                self.last_health_error = time.time()
                get_kawa_logger().error(f'Kawa server seems to be down, error: {e}')
            return False

    def load_pending_job(self):
        return self._get_request('/pending-job')

    def load_pending_jobs(self, max_number_jobs: int) -> List[str]:
        data = {'maxJobs': max_number_jobs}
        return self._post_request('/pending-jobs', json.dumps(data)).json()

    def set_job_success(self, job_id: str, log: str):
        data = {
            'jobId': job_id,
            'log': log
        }
        self._patch_request('/set-job-success', json.dumps(data))

    def set_job_failure(self, job_id: str, error: str, log: str):
        data = {
            'jobId': job_id,
            'error': error,
            'log': log
        }
        self._patch_request('/set-job-failure', json.dumps(data))

    def set_job_log(self, job_id: str, log: str):
        data = {
            'jobId': job_id,
            'log': log
        }
        self._patch_request('/set-job-log', json.dumps(data))

    def _get_request(self, path: str) -> requests.Response:
        return self._request('get', path, '')

    def _post_request(self, path: str, data: str) -> requests.Response:
        return self._request('post', path, data)

    def _patch_request(self, path: str, data: str) -> requests.Response:
        return self._request('patch', path, data)

    def _request(self, http_method: str, path: str, data: str) -> requests.Response:
        timestamp_ms = int(time.time() * 1000)
        url = self._build_url(path)
        headers = self._headers(http_method, path, timestamp_ms, data)
        return requests.request(method=http_method,
                                verify=False,
                                url=url,
                                data=data,
                                headers=headers,
                                timeout=60)

    def _build_url(self, path: str):
        return f'{self.kawa_url}{self._service_path}{path}'

    def _headers(self, http_method: str, final_path: str, timestamp: int, data: str) -> dict:
        return {
            'X-Kawa-TimeStamp': str(timestamp),
            'X-Kawa-Signature': self._generate_aes_signature(http_method, final_path, timestamp, data)
        }

    def _generate_aes_signature(self, http_method: str, final_path: str, timestamp: int, data: str) -> dict:
        body_hash = hashlib.sha256(data.encode('utf-8')).hexdigest()
        canonical_string = f'{http_method}{final_path}{timestamp}{body_hash}'
        iv = ''.join(random.choices(string.digits, k=32))
        return iv + AesCipher(codecs.decode(self.aes_key, 'hex_codec'), codecs.decode(iv, 'hex_codec')).encrypt(
            canonical_string).decode("utf-8")
