import datetime
import json
import os
import queue
import threading
import time
from queue import Queue
from typing import List

from ...server.jobs.job_runner import JobRunner
from ...server.jobs.job_manager_client import JobManagerClient
from ...server.kawa_directory_manager import KawaDirectoryManager

from ...server.kawa_log_manager import get_kawa_logger


class KawaJobExecutorBatched:

    def __init__(self,
                 job_manager_client: JobManagerClient,
                 job_runner: JobRunner,
                 directory_manager: KawaDirectoryManager):
        self.job_requests_queue: Queue = Queue()
        self.job_manager_client: JobManagerClient = job_manager_client
        self.job_runner: JobRunner = job_runner
        self.directory_manager: KawaDirectoryManager = directory_manager
        _max_workers = min(32, (os.cpu_count() or 1) + 4)

        self.polling_thread: threading.Thread = threading.Thread(target=self.polling_thread,
                                                                 name='polling_thread')
        self.polling_thread.daemon = True
        self.polling_thread.start()

        # we do not use a ThreadPoolExecutor because we want to set the threads as daemon,
        # so they will be stopped when the main process stops
        self.threads: List[threading.Thread] = [
            threading.Thread(target=self.worker_loop, args=(f'worker_loop_{i}',), name=f'worker_loop_{i}')
            for i in range(_max_workers)
        ]
        for thread in self.threads:
            thread.daemon = True
            thread.start()

    #     maybe add a check that will regularly check if the threads are still alive and if not create a new one

    def polling_thread(self):
        while True:
            time.sleep(1)
            if not self.job_manager_client.healthy():
                continue
            waiting_worker_job_queues = []
            while not self.job_requests_queue.empty():
                try:
                    waiting_worker_job_queues.append(self.job_requests_queue.get_nowait())
                except queue.Empty:
                    break

            if not waiting_worker_job_queues:
                continue

            jobs = self._load_pending_jobs_safe(len(waiting_worker_job_queues))

            for index, job_queue in enumerate(waiting_worker_job_queues):
                if index <= len(jobs) - 1:
                    job_queue.put(jobs[index])
                else:
                    job_queue.put(None)

    def _load_pending_jobs_safe(self, max_number_jobs):
        jobs = []
        try:
            jobs = self.job_manager_client.load_pending_jobs(max_number_jobs=max_number_jobs)
        except Exception as e:
            pass
        if jobs:
            get_kawa_logger().info(f'{len(jobs)} jobs loaded from the job manager')
        elif datetime.datetime.now().second % 30 == 0:
            get_kawa_logger().info(f'No job pending on kawa side')
        return jobs

    def worker_loop(self, worker_id):
        while True:
            job_queue = Queue(maxsize=1)
            self.job_requests_queue.put(job_queue)
            try:
                job = job_queue.get(timeout=60)
                if job:
                    self._process_one_job(job)
                else:
                    time.sleep(0.5)
            # we should never timeout
            except queue.Empty:
                continue

    def _process_one_job(self, job):
        json_action_payload = json.loads(job)
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
            self._add_to_job_log(job_id, f'Issue when running the job, error is : {e}')
            self.job_manager_client.set_job_log(job_id, self._get_job_log(job_id))
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

    def _add_to_job_log(self, job_id: str, message: str):
        job_log_path = self.directory_manager.log_path(job_id)
        with job_log_path.open('a') as file:
            file.write(message)


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
