#  Quapp Platform Project
#  quapp_d_wave_device.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

import time
import uuid
from abc import ABC

import numpy as np
from dimod import SampleSet
from quapp_common.data.device.circuit_running_option import CircuitRunningOption
from quapp_common.enum.status.job_status import JobStatus
from quapp_common.model.device.custom_device import CustomDevice
from quapp_common.model.provider.provider import Provider


class QuappDWaveOceanDevice(CustomDevice, ABC):
    def __init__(self, provider: Provider, device_specification: str):
        super().__init__(provider, device_specification)

    def _create_job(self, circuit, options: CircuitRunningOption):
        """
        Creates a D-Wave job for the provided BQM (Binary Quadratic Model) circuit.

        This method creates a job by sampling the provided BQM circuit and records
        the execution time for the job creation. The job is then returned.

        Args:
            circuit (dimod.BinaryQuadraticModel): The BQM circuit to sample.
            options (CircuitRunningOption): The options for running the circuit.

        Returns:
            dimod.SampleSet: The created job as a SampleSet.
        """
        self.logger.debug(
                '[QuappDWaveOceanDevice] Creating job with {0} shots'.format(
                        options.shots))

        # Record the start time for execution time measurement
        start_time = time.time()

        # Create a job by sampling the provided BQM (Binary Quadratic Model) circuit
        job = self.device.sample(bqm=circuit, num_reads=options.shots)

        # Calculate the execution time by subtracting the start time from the current time
        self.execution_time = time.time() - start_time

        # Log the execution time for the job creation
        self.logger.debug(
                '[QuappDWaveOceanDevice] Job created in {0:.2f} seconds'.format(
                        self.execution_time))

        # Return the created job
        return job

    def _produce_histogram_data(self, job_result) -> dict | None:
        """
        Converts the samples of a SampleSet into a histogram data.

        Args:
            job_result (SampleSet): The SampleSet object returned by the D-Wave Ocean Solver.

        Returns:
            dict | None: A dictionary containing the histogram data in the format {'0': int, '1': int}.
        """
        self.logger.debug('[QuappDWaveOceanDevice] Produce histogram data')

        # Check if job_result is an instance of SampleSet
        if isinstance(job_result, SampleSet):
            try:
                # Retrieve the sample from the job_result
                sample = job_result.record.sample
                # Convert the first sample to a NumPy array
                sample = np.array(sample[0])

                # Count the occurrences of each value (0 and 1) in the sample
                counts = np.bincount(sample, minlength=2)

                # Return a dictionary with the counts of values 0 and 1
                return {"0": int(counts[0]), "1": int(counts[1]), }
            except Exception as e:
                self.logger.error(
                        f"[QuappDWaveOceanDevice] Error producing histogram data: {e}")
                return None

        self.logger.debug(
                '[QuappDWaveOceanDevice] Job result is not an instance of SampleSet. Returning None.')
        return None

    def _get_provider_job_id(self, job) -> str:
        self.logger.debug('[QuappDWaveOceanDevice] Get provider job id')

        provider_job_id = str(uuid.uuid4())
        self.logger.debug(f'[QuappDWaveOceanDevice] Provider job ID:'
                          f' {provider_job_id}')
        return provider_job_id

    def _get_job_status(self, job) -> str:
        self.logger.debug('[QuappDWaveOceanDevice] Get job status')

        return JobStatus.DONE.value

    def _get_job_result(self, job):
        """
        Retrieves the result of the job from the provider.

        If the job is a SampleSet, it is returned directly. Otherwise, the result of the job is retrieved by calling `job.result()`.

        Args:
            job (SampleSet or Job): The job to retrieve the result from.

        Returns:
            SampleSet or Any: The result of the job if it is a SampleSet, otherwise the result of calling `job.result()`.
        """
        self.logger.debug('[QuappDWaveOceanDevice] Get job result')

        # Check if the job is an instance of SampleSet
        if isinstance(job, SampleSet):
            # Log that the job is a SampleSet and will be returned directly
            self.logger.debug(
                    f'[QuappDWaveOceanDevice] Job is a SampleSet. Returning the job directly: {job}')
            return job

        # Log that the job is not a SampleSet and will return the result of the job
        self.logger.debug(
                f'[QuappDWaveOceanDevice] Job is not a SampleSet. Returning job.result(): {job.result()}')
        return job.result()

    def _get_shots(self, job_result) -> int | None:
        """
        Get the number of shots of a job.

        Args:
            job_result (SampleSet): The SampleSet object returned by the D-Wave Ocean Solver.

        Returns:
            int | None: The number of shots if the job_result is a SampleSet, otherwise None.
        """
        self.logger.debug('[QuappDWaveOceanDevice] Get shots')
        if isinstance(job_result, SampleSet):
            # Log the size of the 'num_occurrences' data vector
            occurrences_size = job_result.data_vectors['num_occurrences'].size
            self.logger.debug(
                    f'[QuappDWaveOceanDevice] Number of occurrences size: {occurrences_size}')
            return occurrences_size

        # Log a warning if job_result is not a SampleSet
        self.logger.warning(
                f'[QuappDWaveOceanDevice] Job result is not a SampleSet, is {type(job_result)}. Returning None.')
        return None

    def _is_simulator(self) -> bool:
        self.logger.info('[QuappDWaveOceanDevice] Is simulator')
        return True

    def _calculate_execution_time(self, job_result) -> None:
        """
        Calculate the execution time of a job in seconds.

        The execution time is calculated from the timing information in the job info,
        which is extracted and summed directly. The result is stored in the
        `execution_time` attribute.

        If the `job_result` is not a SampleSet, the extract timing information from the job info skipped.

        Parameters
        ----------
        job_result : SampleSet
            The result of the job.

        Returns
        -------
        None
        """
        timing = None
        # Extract timing information from the job information
        if isinstance(job_result, SampleSet):
            timing = job_result.info.get('timing', {})
        else:
            if isinstance(job_result, dict) and '_info' in job_result:
                timing = job_result['_info'].get('timing', {})
        if timing is not None:
            # Calculate total time in seconds by summing the values directly
            self.execution_time = sum(timing.values()) / 1_000_000_000

            # Log the execution time calculation
            self.logger.debug(
                    f'[QuappDWaveOceanDevice] Execution time calculation was: {self.execution_time} seconds')
        else:
            self.logger.warning(
                    '[QuappDWaveOceanDevice] Extract timing information from the job info skipped.')
