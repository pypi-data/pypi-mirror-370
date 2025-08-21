"""
    QApp Platform Project qiskit_job_fetching.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from quapp_common.component.backend.job_fetcher import JobFetcher
from quapp_common.data.request.job_fetching_request import JobFetchingRequest
from quapp_common.config.logging_config import logger
from quapp_common.enum.provider_tag import ProviderTag
from quapp_common.enum.sdk import Sdk
from quapp_common.enum.status.job_status import JobStatus
from pyquil import get_qc
import pickle
import os

from ...factory.pyquil_provider_factory import PyquilProviderFactory


class PyquilJobFetching(JobFetcher):

    def __init__(self, request_data: JobFetchingRequest, device_name: str, authentication: dict):
        super().__init__(request_data)
        self.request_data = request_data
        self.device_name = device_name
        self.authentication = authentication

    def _collect_provider(self):

        device = PyquilProviderFactory.create_provider(authentication=self.authentication,
                                              sdk=Sdk.PYQUIL,
                                              provider_type=ProviderTag.RIGETTI)

        print(f"Device name in fetching: {self.device_name}")
        return device.get_backend(self.device_name)
        

    def _retrieve_job(self, job):
        
        job_id = self.provider_job_id
        device = self._collect_provider()

        save_dir = "/home/app"

        file_path = os.path.join(save_dir, f"{job_id}.pkl")

        with open(file_path, 'rb') as file:
            data = pickle.load(file)
        
        res = device.qam.get_result(data)
        print(f"Result: {res}")

        return res

    def _get_job_status(self, job):

        if job.execution_duration_microseconds is not None:
            
            if os.path.exists(self.provider_job_id+".pkl"):
                os.remove(self.provider_job_id+".pkl")
            return JobStatus.DONE.value

        return "POLLING"

    def _get_job_result(self, job):
        return job

    def _produce_histogram_data(self, job_result) -> dict | None:
        return None

    def _get_execution_time(self, job_result):
        return job_result.execution_duration_microseconds
        
    def _get_shots(self, job_result):
        return None
