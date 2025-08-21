"""
    QApp Platform Project job_fetching_handler.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from quapp_common.data.request.job_fetching_request import JobFetchingRequest
from quapp_common.handler.handler import Handler
from quapp_common.config.logging_config import logger

from ..component.backend.pyquil_job_fetching import PyquilJobFetching 


class JobFetchingHandler(Handler):
    def __init__(self,
                 request_data: dict,
                 post_processing_fn):
        super().__init__(request_data, post_processing_fn)

    def handle(self):
        logger.info("[JobFetchingHandler] handle()")

        request = JobFetchingRequest(self.request_data)
        device_name = self.request_data.get("authentication").get("deviceName")

        job_fetching = PyquilJobFetching(request,device_name = device_name, authentication=self.request_data.get("authentication"))

        fetching_result = job_fetching.fetch(post_processing_fn=self.post_processing_fn)

        return fetching_result
