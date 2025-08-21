import os
import threading
import time
from typing import List

from ...server.jobs.job_runner import JobRunner
from ...server.jobs.job_manager_client import JobManagerClient
from ...server.kawa_directory_manager import KawaDirectoryManager

from ...server.kawa_log_manager import get_kawa_logger


class KawaJobExecutor:

    def __init__(self,
                 job_manager_client: JobManagerClient,
                 job_runner: JobRunner,
                 directory_manager: KawaDirectoryManager):
        self.job_manager_client: JobManagerClient = job_manager_client
        self.job_runner: JobRunner = job_runner
        self.directory_manager: KawaDirectoryManager = directory_manager
        _max_workers = min(32, (os.cpu_count() or 1) + 4)
        # we do not use a ThreadPoolExecutor because we want to set the threads as daemon,
        # so they will be stopped when the main process stops
        self.threads: List[threading.Thread] = [
            threading.Thread(target=self.worker_loop, name=f'worker_loop_{i}')
            for i in range(_max_workers)
        ]
        for thread in self.threads:
            thread.daemon = True
            thread.start()

    #     maybe add a check that will regularly check if the threads are still alive and if not create a new one

    def worker_loop(self):
        while True:
            try:
                self._process_one_job()
            except Exception as e:
                get_kawa_logger().error(f'Unexpected exception in worker loop: {e}')
            time.sleep(1)

    def _process_one_job(self):
        if not self.job_manager_client.healthy():
            return

        json_action_payload = self.job_manager_client.load_pending_job().json()

        if not json_action_payload:
            return
        job_id = json_action_payload['job']
        stop_event = threading.Event()
        self.directory_manager.create_log_file(job_id)
        log_upload_consumer = lambda: self.job_manager_client.set_job_log(job_id, self._get_job_log(job_id))
        log_thread = ConsumerThread(log_upload_consumer, interval=2, stop_event=stop_event)
        log_thread.start()
        try:
            self.job_runner.run_job(job_id, json_action_payload)
            stop_event.set()
            self.job_manager_client.set_job_success(job_id, self._get_job_log(job_id))

        except Exception as e:
            stop_event.set()
            self.job_manager_client.set_job_failure(job_id,
                                                    str(e),
                                                    self._get_job_log(job_id))
        finally:
            stop_event.set()
            log_thread.join()

    def _get_job_log(self, job_id: str):
        job_log_path = self.directory_manager.log_path(job_id)
        try:
            with job_log_path.open('r') as file:
                return file.read()
        except Exception as e:
            return ""


class ConsumerThread(threading.Thread):
    def __init__(self, consumer, interval, stop_event):
        super().__init__(daemon=True)
        self.consumer = consumer
        self.interval = interval
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            self.consumer()
            self.stop_event.wait(self.interval)
