#  Quapp Platform Project
#  d_wave_system_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from quapp_common.data.device.circuit_running_option import CircuitRunningOption

from ..device.d_wave_device import DWaveDevice


class DWaveSystemDevice(DWaveDevice):

    def _create_job(self, circuit, options: CircuitRunningOption):
        self.logger.debug("[DWave System] Create job")

        return self.device.sample(circuit)

    def _get_provider_job_id(self, job) -> str:
        self.logger.debug("[DWave System] Get provider job id")

        return job.info.get("problem_id")

    def _calculate_execution_time(self, job_result) -> None:
        self.logger.debug("[DWave System] Calculate execution time")

        self.execution_time = (job_result.get("_info").get("timing").get(
                "qpu_access_time") / 1000)

        self.logger.debug(
                f"[DWave System] Execution time calculation was: {self.execution_time} seconds")

    def _get_job_result(self, job):
        self.logger.debug('[DWave System] Get job result')

        return job
