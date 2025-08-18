#  Quapp Platform Project
#  job_fetching_handler.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.config.logging_config import logger
from quapp_common.data.request.job_fetching_request import JobFetchingRequest
from quapp_common.handler.handler import Handler

from ..component.backend.d_wave_ocean_job_fetching import DWaveOceanJobFetching


class JobFetchingHandler(Handler):
    def __init__(self,
                 request_data: dict,
                 post_processing_fn):
        super().__init__(request_data, post_processing_fn)

    def handle(self):
        """
        Handles the job fetching request.

        This method creates a JobFetchingRequest object using the provided
        request data, then creates a JobFetching object to fetch the job.
        The job fetching process uses a post-processing function
        to process the fetched result.

        Returns:
            The result of the job fetching process after applying
            post-processing.
        """
        self.logger.debug("[JobFetchingHandler] Creating JobFetchingRequest with data: {0}".format(
            self.request_data))
        request = JobFetchingRequest(self.request_data)

        self.logger.debug("[JobFetchingHandler] Initializing JobFetching with request.")
        job_fetching = DWaveOceanJobFetching(request)

        self.logger.debug("[JobFetchingHandler] Starting job fetching process.")
        fetching_result = job_fetching.fetch(post_processing_fn=self.post_processing_fn)

        self.logger.debug("[JobFetchingHandler] Job fetching result: {0}".format(fetching_result))
        return fetching_result
