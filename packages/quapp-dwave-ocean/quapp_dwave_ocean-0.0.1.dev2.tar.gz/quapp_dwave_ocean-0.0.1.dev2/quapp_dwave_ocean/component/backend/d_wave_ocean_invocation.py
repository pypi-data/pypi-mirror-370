#  Quapp Platform Project
#  d_wave_ocean_invocation.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.

from dimod import BinaryQuadraticModel
from quapp_common.component.backend.invocation import Invocation
from quapp_common.config.thread_config import circuit_exporting_pool
from quapp_common.data.async_task.circuit_export.backend_holder import \
    BackendDataHolder
from quapp_common.data.async_task.circuit_export.circuit_holder import \
    CircuitDataHolder
from quapp_common.data.request.invocation_request import InvocationRequest
from quapp_common.model.provider.provider import Provider

from quapp_dwave_ocean.async_tasks.d_wave_ocean_circuit_export_task import \
    DWaveOceanCircuitExportTask
from quapp_dwave_ocean.factory.d_wave_device_factory import DWaveDeviceFactory
from quapp_dwave_ocean.factory.d_wave_provider_factory import \
    DWaveProviderFactory


class DWaveOceanInvocation(Invocation):
    def __init__(self, request_data: InvocationRequest):
        """
        Initialize DWaveOceanInvocation object

        Args:
             request_data: InvocationRequest object
        """
        super().__init__(request_data)
        try:
            provider_tag = getattr(self.backend_information, "provider_tag",
                                   None)
            device_name = getattr(self.backend_information, "device_name", None)
            self.logger.info("[DWaveOceanInvocation] Initialized")
            self.logger.debug(
                    "[DWaveOceanInvocation] init details: provider_tag=%s, device_name=%s, sdk=%s, export_url_present=%s",
                    provider_tag, device_name, getattr(self, "sdk", None),
                    bool(getattr(self, "circuit_export_url", None)), )
        except Exception as e:
            self.logger.exception(
                    "[DWaveOceanInvocation] Initialization logging failed: %s",
                    e)

    def _export_circuit(self, circuit):
        """
        Export circuit to svg file then send to QuaO server for saving

        @param circuit: Circuit was exported
        """
        self.logger.info("[DWaveOceanInvocation] _export_circuit() started")
        try:
            circuit_export_task = DWaveOceanCircuitExportTask(
                    circuit_data_holder=CircuitDataHolder(circuit,
                                                          self.circuit_export_url),
                    backend_data_holder=BackendDataHolder(
                            self.backend_information,
                            self.authentication.user_token),
                    project_header=self.project_header,
                    workspace_header=self.workspace_header, )
            self.logger.debug(
                    "[DWaveOceanInvocation] Prepared CircuitExportTask: export_url_present=%s, project_header=%s, workspace_header=%s",
                    bool(self.circuit_export_url),
                    bool(getattr(self, "project_header", None)),
                    bool(getattr(self, "workspace_header", None)), )

            future = circuit_exporting_pool.submit(circuit_export_task.do)
            self.logger.info(
                    "[DWaveOceanInvocation] Circuit export task submitted to thread pool")

            def _done_callback(fut):
                try:
                    fut.result()
                    self.logger.info(
                            "[DWaveOceanInvocation] Circuit export task completed successfully")
                except Exception as export_err:
                    self.logger.exception(
                            "[DWaveOceanInvocation] Circuit export task failed: %s",
                            export_err)

            future.add_done_callback(_done_callback)
        except Exception as e:
            self.logger.exception(
                    "[DWaveOceanInvocation] Failed to export circuit: %s", e)
            raise

    def _create_provider(self):
        """
        Create a provider based on the provider type and SDK

        Return: Provider object
        """
        self.logger.info("[DWaveOceanInvocation] _create_provider()")
        try:
            self.logger.debug(
                    "[DWaveOceanInvocation] Creating provider with provider_tag=%s, sdk=%s",
                    getattr(self.backend_information, "provider_tag", None),
                    getattr(self, "sdk", None), )
            return DWaveProviderFactory.create_provider(
                    provider_type=self.backend_information.provider_tag,
                    sdk=self.sdk,
                    authentication=self.backend_information.authentication, )
        except Exception as e:
            self.logger.exception(
                    "[DWaveOceanInvocation] _create_provider failed: %s", e)
            raise

    def _create_device(self, provider: Provider):
        """
        Create a device based on the provider and device specification

        Args:
            provider: Provider instance that this device belongs to
        Return:
            A device instance corresponding to the specified provider and device type
        """
        try:
            self.logger.debug(
                    f"[DWaveOceanInvocation] Creating device device_name="
                    f"{getattr(self.backend_information, 'device_name', None)}"
                    f", sdk={getattr(self, 'sdk', None)}")
            return DWaveDeviceFactory.create_device(provider=provider,
                                                    device_specification=self.backend_information.device_name,
                                                    authentication=self.backend_information.authentication,
                                                    sdk=self.sdk, )
        except Exception as exception:
            self.logger.exception(
                    f"[DWaveOceanInvocation] _create_device failed: {exception}")
            raise

    def _get_qubit_amount(self, circuit):
        """
        Get the number of qubits in the given circuit.

        Args:
            circuit: The quantum circuit for which the qubit count is needed.
        Returns:
            int: The number of qubits in the circuit.
        """
        try:
            if isinstance(circuit, BinaryQuadraticModel):
                qubit_amount = circuit.binary.num_variables
                self.logger.info(
                        f"[DWaveOceanInvocation] Circuit is a BinaryQuadraticModel with {qubit_amount} qubits.")
                return qubit_amount
            else:
                qubit_amount = getattr(circuit, "num_qubits", None)
                if qubit_amount is None:
                    raise AttributeError(
                            "circuit object has no attribute 'num_qubits'")
                self.logger.info(f"[DWaveOceanInvocation] Circuit is not a "
                                 f"BinaryQuadraticModel; it has {qubit_amount} qubits.")
                return qubit_amount
        except Exception as exception:
            self.logger.exception(
                    f"[DWaveOceanInvocation] Failed to get qubit amount: {exception}")
            raise
