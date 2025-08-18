#  Quapp Platform Project
#  d_wave_hybrid_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.data.device.circuit_running_option import CircuitRunningOption

from ..device.d_wave_device import DWaveDevice


class DWaveHybridDevice(DWaveDevice):

    def _create_job(self, circuit, options: CircuitRunningOption):
        self.logger.debug("[DWave System] Create job")

        return self.device.sample_bqm(circuit, time_limit=10)

    def _get_provider_job_id(self, job) -> str:
        self.logger.debug("[DWave System] Get provider job id")

        return job.id

    def _get_job_result(self, job):
        self.logger.debug('[DWave System] Get job result')

        return job.result().get('sampleset')

    def _calculate_execution_time(self, job_result) -> None:
        self.logger.debug("[DWave System] Calculate execution time")

        self.execution_time = (
                job_result.get("_info").get('run_time') / 1000
        )

        self.logger.debug(
                "[DWave System] Execution time calculation was: {0} seconds".format(
                        self.execution_time
                )
        )
