from quapp_common.component.backend.job_fetcher import JobFetcher
from quapp_common.data.request.job_fetching_request import JobFetchingRequest


class DWaveOceanJobFetching(JobFetcher):
    def __init__(self, request: JobFetchingRequest, ):
        super().__init__(request)

    def _collect_provider(self):
        pass

    def _retrieve_job(self, provider):
        pass

    def _get_job_status(self, job):
        pass

    def _get_job_result(self, job):
        pass

    def _produce_histogram_data(self, job_result) -> dict | None:
        pass

    def _get_execution_time(self, job_result):
        pass

    def _get_shots(self, job_result):
        pass
