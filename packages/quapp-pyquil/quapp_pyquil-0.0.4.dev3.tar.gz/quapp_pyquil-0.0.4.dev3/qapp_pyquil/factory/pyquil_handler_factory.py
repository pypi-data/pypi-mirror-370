"""
    QApp Platform Project pyquil_handler_factory.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""

from quapp_common.factory.handler_factory import HandlerFactory
from quapp_common.handler.handler import Handler

from ..handler.invocation_handler import InvocationHandler
from quapp_common.config.logging_config import job_logger
class PyquilHandlerFactory(HandlerFactory):

    @staticmethod
    def create_handler(event, circuit_preparation_fn, post_processing_fn) -> Handler:

        request_data = event.json()
        provider_job_id = request_data.get("providerJobId")

        logger = job_logger(request_data.get('jobId'))
        logger.debug('Creating handler')

        if provider_job_id is None:
            logger.debug("[PyquilHandlerFactory] Create InvocationHandler")
            return InvocationHandler(
                request_data=request_data,
                circuit_preparation_fn=circuit_preparation_fn,
                post_processing_fn=post_processing_fn,
            )
        # logger.debug("Create JobFetchingHandler")
        # return JobFetchingHandler(
        #     request_data=request_data, post_processing_fn=post_processing_fn
        # )
