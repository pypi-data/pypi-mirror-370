"""
    QApp Platform Project
    qapp_pyquil_device.py
    Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
import time
import math
import os

from quapp_common.data.response.authentication import Authentication
from quapp_common.data.response.custom_header import CustomHeader
from quapp_common.model.device.device import Device
from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.model.provider.provider import Provider
from quapp_common.data.response.job_response import JobResponse

from quapp_common.component.callback.update_job_metadata import update_job_metadata
from quapp_common.enum.status.job_status import JobStatus
from quapp_common.enum.media_type import MediaType
from quapp_common.enum.status.status_code import StatusCode
from quapp_common.data.callback.callback_url import CallbackUrl
import pickle
import time


class RigettiPyquilDevice(Device):
    def __init__(self, provider: Provider, device_specification: str):
        super().__init__(provider, device_specification)
        self.logger.debug('[RigettiPyquilDevice] Initializing device specification')
        self.device_specification = device_specification

    def _create_job(self, circuit, options: CircuitRunningOption):
        self.logger.debug(
            '[RigettiPyquilDevice] Creating job with {0} shots'.format(
                options.shots))
        
        circuit.wrap_in_numshots_loop(options.shots)
        executable = self.device.compile(circuit)

        return self.device.qam.execute(executable)

    def _is_simulator(self) -> bool:
        self.logger.debug('[RigettiPyquilDevice] is quantum machine')
        return False

    def _get_provider_job_id(self, job) -> str:
        self.logger.debug('[PyquilDevice] Getting job id')

        return job.job_id

    def _get_job_status(self, job) -> str:
        self.logger.debug('[PyquilDevice] Getting job status')

        return "RUNNING"

    def _calculate_execution_time(self, job_result):
        self.logger.debug('[PyquilDevice] Getting execution time {}',job_result)

        # the time unit is miliseconds
        return job_result.execution_duration_microseconds/1000

    def _get_job_result(self, job):
        
        return self.device.qam.get_result(job)

    def _produce_histogram_data(self, job_result) -> dict | None:
        self.logger.info('[PyquilDevice] Producing histogram data')

        return None

    def _on_execution(self, authentication: Authentication,
        project_header: CustomHeader,
        workspace_header: CustomHeader,
        execution_callback: CallbackUrl,
        circuit,
        options: CircuitRunningOption):
        """

        @param authentication: authentication information
        @param project_header: project header information
        @param execution_callback: execution step callback urls
        @param circuit: circuit will be run
        @param options: options will use for running
        @return: job and job response
        """
        self.logger.debug("[Invocation] On execution")

        job_response = JobResponse(authentication=authentication,
                                   project_header=project_header,
                                   status_code=StatusCode.DONE,
                                   workspace_header=workspace_header)

        update_job_metadata(job_response=job_response,
                            callback_url=execution_callback.on_start)
        try:
            job = self._create_job(circuit=circuit, options=options)
            job_response.provider_job_id = self._get_provider_job_id(job)
            job_response.job_status = self._get_job_status(job)
            original_job_result = None

            while True:
                
                self.logger.debug("fetching job result")

                try:
                    res = self._get_job_result(job)
                    self.logger.debug("Job result: {}".format(res))
                    if res.execution_duration_microseconds is not None:
                        job_response.job_status = JobStatus.DONE.value
                        original_job_result = res
                        break
                except Exception as e:
                    self.logger.debug("Job result not ready yet: {}".format(str(e)))
                time.sleep(5)

            self.logger.debug("Job result: {}".format(job_response))

            update_job_metadata(job_response=job_response,
                                callback_url=execution_callback.on_done)

            return original_job_result, job_response

        except Exception as exception:
            self.logger.debug("Execute job failed with error {}".format(str(exception)))

            job_response.status_code = StatusCode.ERROR
            job_response.content_type = MediaType.APPLICATION_JSON
            job_response.job_status = JobStatus.ERROR.value
            job_response.job_result = {"error": str(exception)}

            update_job_metadata(job_response=job_response,
                                callback_url=execution_callback.on_error)
            return None, None

    def _on_analysis(self, job_response: JobResponse,
                      analysis_callback: CallbackUrl,
                      original_job_result):
        """

        @param job_response:
        @param analysis_callback:
        @param original_job_result:
        @return:
        """
        self.logger.debug("[Invocation] On analysis")

        update_job_metadata(job_response=job_response,
                            callback_url=analysis_callback.on_start)

        try:
            job_response.job_histogram = self._produce_histogram_data(original_job_result)

            self.execution_time = self._calculate_execution_time(original_job_result)
            
            job_response.execution_time = self.execution_time
            self.logger.debug("Execution time: {}".format(job_response.execution_time))

            update_job_metadata(
                job_response=job_response,
                callback_url=analysis_callback.on_done)

            return job_response

        except Exception as exception:
            self.logger.error("Invocation - Exception when analyst job result : {0}".format(
                str(exception)))

            job_response.status_code = StatusCode.ERROR
            job_response.content_type = MediaType.APPLICATION_JSON
            job_response.job_status = JobStatus.ERROR.value
            job_response.job_result = {"error": str(exception)}

            update_job_metadata(job_response=job_response,
                                callback_url=analysis_callback.on_error)
            return None
