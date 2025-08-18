#  Quapp Platform Project
#  d_wave_ocean_circuit_export_task.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.
from io import BytesIO

import numpy as np
import requests
from dimod import BinaryQuadraticModel
from matplotlib import pyplot as plt
from quapp_common.async_tasks.export_circuit_task import CircuitExportTask
from quapp_common.config.logging_config import job_logger
from quapp_common.data.async_task.circuit_export.backend_holder import \
    BackendDataHolder
from quapp_common.data.async_task.circuit_export.circuit_holder import \
    CircuitDataHolder
from quapp_common.data.response.custom_header import CustomHeader
from quapp_common.enum.media_type import MediaType
from quapp_common.util.file_utils import FileUtils
from quapp_common.util.http_utils import create_bearer_header, \
    get_job_id_from_url


class DWaveOceanCircuitExportTask:
    MAX_CIRCUIT_IMAGE_SIZE = 5 * (1024 ** 2)

    def __init__(self, circuit_data_holder: CircuitDataHolder,
                 backend_data_holder: BackendDataHolder,
                 project_header: CustomHeader, workspace_header: CustomHeader):
        super().__init__()
        self.project_header = project_header
        self.workspace_header = workspace_header
        self.circuit_data_holder = circuit_data_holder
        self.backend_data_holder = backend_data_holder
        self.logger = job_logger(
                get_job_id_from_url(self.circuit_data_holder.export_url))

    def do(self):
        """
          Export circuit to svg file, then send it to QuaO server for saving
        """
        self.logger.info("Starting circuit export task...")

        circuit_export_url = self.circuit_data_holder.export_url

        if circuit_export_url is None or len(circuit_export_url) < 1:
            self.logger.warning("Export URL is missing. Task will exit.")
            return

        try:
            self.logger.debug('Converting circuit to SVG')
            figure_buffer = self._render_circuit_svg(self._transpile_circuit())
        except Exception as e:
            self.logger.exception("Error converting circuit to SVG: %s", e,
                                  exc_info=True)
            return

        try:
            self.logger.debug('Determining if circuit SVG should be zipped')
            # Use protected helpers from base class (single underscore), not name-mangled privates
            io_buffer_value, content_type = self.__determine_zip(
                    figure_buffer=figure_buffer)
            size_bytes = (
                io_buffer_value.getbuffer().nbytes
                if isinstance(io_buffer_value, BytesIO)
                else len(io_buffer_value)
            )
            self.logger.debug("Content type: %s", content_type)
            self.logger.debug("Buffer size: %s bytes", size_bytes)
        except Exception as e:
            self.logger.exception(
                    "Error determining if circuit SVG should be zipped: %s", e,
                    exc_info=True)
            return

        try:
            self.logger.debug('Sending circuit to backend')
            self.__send(io_buffer_value=io_buffer_value,
                        content_type=content_type)
            self.logger.debug("Circuit sent to backend successfully.")
            return
        except Exception as e:
            self.logger.exception(
                    "Error sending exported circuit to backend: %s", e,
                    exc_info=True)
            return

    def _render_circuit_svg(self,
                            transpiled_circuit: BinaryQuadraticModel) -> BytesIO:
        """
        Render a BinaryQuadraticModel as an SVG figure and return it as a BytesIO buffer.

        This matches the transpile output type (BinaryQuadraticModel) from _transpile_circuit.
        """
        self.logger.info("Rendering BinaryQuadraticModel to SVG")
        try:
            linear_items = list(transpiled_circuit.linear.items())
            quadratic_items = list(transpiled_circuit.quadratic.items())

            # Prepare figure
            fig, axes = plt.subplots(1, 2, figsize=(10, 4))
            fig.suptitle("D-Wave Ocean BQM Visualization", fontsize=12)

            # Left: Linear biases (bar chart)
            ax0 = axes[0]
            if linear_items:
                vars_, lin_vals = zip(*linear_items)
                x = np.arange(len(vars_))
                ax0.bar(x, lin_vals, color="#1f77b4")
                ax0.set_xticks(x)
                ax0.set_xticklabels([str(v) for v in vars_], rotation=45,
                                    ha="right", fontsize=8)
                ax0.set_title("Linear biases")
                ax0.set_ylabel("bias")
            else:
                ax0.text(0.5, 0.5, "No linear biases", ha="center", va="center",
                         transform=ax0.transAxes)
                ax0.set_axis_off()

            # Right: Quadratic couplers (scatter)
            ax1 = axes[1]
            if quadratic_items:
                uvs = [f"{u}-{v}" for (u, v), _ in quadratic_items]
                q_vals = [b for _, b in quadratic_items]
                x = np.arange(len(uvs))
                ax1.scatter(x, q_vals, c=np.sign(q_vals), cmap="bwr",
                            edgecolor="k")
                ax1.set_xticks(x)
                ax1.set_xticklabels(uvs, rotation=45, ha="right", fontsize=8)
                ax1.set_title("Quadratic couplers")
                ax1.set_ylabel("coupling")
                ax1.axhline(0, color="gray", linewidth=0.8)
            else:
                ax1.text(0.5, 0.5, "No quadratic couplers", ha="center",
                         va="center", transform=ax1.transAxes)
                ax1.set_axis_off()

            fig.tight_layout(rect=[0, 0.03, 1, 0.95])

            self.logger.debug("Converting rendered figure to SVG buffer")
            figure_buffer = BytesIO()
            try:
                fig.savefig(figure_buffer, format="svg", bbox_inches="tight")
                figure_buffer.seek(0)
                self.logger.debug("SVG export complete. Size: %s bytes",
                                  figure_buffer.getbuffer().nbytes)
            except Exception as exception:
                self.logger.exception("Error saving BQM figure to SVG: %s",
                                      exception, exc_info=True)
                raise
            finally:
                plt.close(fig)

            return figure_buffer

        except Exception as exception:
            self.logger.exception(
                    "Error rendering BinaryQuadraticModel to SVG: %s",
                    exception,
                    exc_info=True)
            raise

    def _transpile_circuit(self) -> BinaryQuadraticModel:
        self.logger.info('Transpiling D-Wave Ocean circuit')
        circuit = self.circuit_data_holder.circuit
        self.logger.debug('Fetched circuit from holder: %s', circuit)

        if circuit is None:
            self.logger.error('Circuit must not be None')
            raise ValueError('Circuit must not be None')

        if isinstance(circuit, BinaryQuadraticModel):
            self.logger.debug(
                    'Circuit is BinaryQuadraticModel; no transpilation needed')
            return circuit

        self.logger.error('Expected BinaryQuadraticModel, got %s',
                          type(circuit))
        raise ValueError(f'Expected BinaryQuadraticModel, got {type(circuit)}')

    def __determine_zip(self, figure_buffer):
        """
        Determine if the buffer needs to be zipped; return (buffer, content_type).
        """
        self.logger.debug("Checking if SVG file needs to be zipped.")
        buffer_value = figure_buffer.getvalue()
        content_type = MediaType.SVG_XML

        self.logger.debug("Checking max file size")
        estimated_file_size = len(buffer_value)

        if estimated_file_size > CircuitExportTask.MAX_CIRCUIT_IMAGE_SIZE:
            self.logger.debug("Zip file")
            zip_file_buffer = FileUtils.zip(io_buffer_value=buffer_value,
                                            file_name="circuit_image.svg")

            buffer_value = zip_file_buffer.getvalue()
            content_type = MediaType.APPLICATION_ZIP

        return buffer_value, content_type

    def __send(self, io_buffer_value, content_type: MediaType):
        """
       Send circuit SVG (or zipped SVG) to the backend.
       """
        url = self.circuit_data_holder.export_url

        self.logger.debug(
                f"Sending circuit svg image to [{url}] with POST method ...")

        payload = {'circuit': ('circuit_image.svg', io_buffer_value,
                               content_type.value)}

        try:
            response = requests.post(url=url, headers=create_bearer_header(
                    self.backend_data_holder.user_token, self.project_header,
                    self.workspace_header), files=payload)
        except Exception as exception:
            self.logger.exception(f"HTTP request failed: {exception}",
                                  exc_info=True)
            raise

        if response.ok:
            self.logger.info("Request sent to QuaO backend successfully.")
        else:
            self.logger.exception(
                    f"Sending request to QuaO backend failed with status {response.status_code}! Response: {response.content}")

        self.logger.debug("HTTP request complete.")
