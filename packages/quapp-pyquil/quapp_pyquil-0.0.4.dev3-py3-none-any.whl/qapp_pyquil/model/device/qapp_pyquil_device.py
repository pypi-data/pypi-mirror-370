"""
    QApp Platform Project
    qapp_pyquil_device.py
    Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
import time

from quapp_common.data.response.authentication import Authentication
from quapp_common.data.response.custom_header import CustomHeader
from quapp_common.model.device.device import Device
from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.model.provider.provider import Provider
from quapp_common.enum.invocation_step import InvocationStep


class QAppPyquilDevice(Device):
    def __init__(self, provider: Provider, device_specification: str):
        super().__init__(provider, device_specification)
        self.logger.debug('[QAppPyquilDevice] Initializing device specification')
        self.device_specification = device_specification

    def _create_job(self, circuit, options: CircuitRunningOption):
        self.logger.debug(
            '[QAppPyquilDevice] Creating job with {0} shots'.format(
                options.shots))
        
        circuit.wrap_in_numshots_loop(options.shots)
      
        start_time = time.time()
        executable = self.device.compile(circuit)
        result = self.device.run(executable)
        end_time = time.time()

        data = {"result": result, "time_taken_execute": end_time - start_time}

        # logger.info(data)
        return data

    def _is_simulator(self) -> bool:
        self.logger.debug('[QAppPyquilDevice] Is simulator')
        return True

    def _produce_histogram_data(self, job_result) -> dict | None:
        self.logger.info('[PyquilDevice] Producing histogram data')

        histogram = job_result.get('histogram')

        if histogram is None:
            self.logger.debug("[PyquilDevice] Can't produce histogram")

        return job_result.get('histogram')

    def _get_provider_job_id(self, job) -> str:
        self.logger.debug('[PyquilDevice] Getting job id')

        # no job id in local simulator
        return ""

    def _get_job_status(self, job) -> str:
        self.logger.debug('[PyquilDevice] Getting job status')

        return "DONE"

    def _get_job_result(self, job) -> dict:
        self.logger.debug('[PyquilDevice] Getting job result')

        return job

    def _calculate_execution_time(self, job_result):
        self.logger.debug('[PyquilDevice] Calculating execution time')

        self.execution_time = job_result.get('time_taken_execute')

        self.logger.debug(
            '[PyquilDevice] Execution time calculation was: {0} seconds'.format(
                self.execution_time))

    def run_circuit(self,
                    circuit,
                    post_processing_fn,
                    options: CircuitRunningOption,
                    callback_dict: dict,
                    authentication: Authentication,
                    project_header: CustomHeader,
                    workspace_header: CustomHeader):

        original_job_result, job_response = self._on_execution(
            authentication=authentication,
            project_header=project_header,
            workspace_header=workspace_header,
            execution_callback=callback_dict.get(InvocationStep.EXECUTION),
            circuit=circuit,
            options=options)

        if original_job_result is None:
            return

        job_response = self._on_analysis(
            job_response=job_response,
            original_job_result=original_job_result,
            analysis_callback=callback_dict.get(InvocationStep.ANALYSIS))

        if job_response is None:
            return

        self._on_finalization(job_result=original_job_result.get('result'),
                              authentication=authentication,
                              post_processing_fn=post_processing_fn,
                              finalization_callback=callback_dict.get(
                                  InvocationStep.FINALIZATION),
                              project_header=project_header,
                              workspace_header= workspace_header)
