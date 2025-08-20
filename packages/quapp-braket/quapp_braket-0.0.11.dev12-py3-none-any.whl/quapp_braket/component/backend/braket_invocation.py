#  Quapp Platform Project
#  braket_invocation.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

from braket.circuits import Circuit
from quapp_common.component.backend.invocation import Invocation
from quapp_common.config.thread_config import circuit_exporting_pool
from quapp_common.data.async_task.circuit_export.backend_holder import \
    BackendDataHolder
from quapp_common.data.async_task.circuit_export.circuit_holder import \
    CircuitDataHolder
from quapp_common.data.request.invocation_request import InvocationRequest
from quapp_common.model.provider.provider import Provider

from ...async_tasks.braket_circuit_export_task import BraketCircuitExportTask
from ...factory.braket_device_factory import create_device
from ...factory.braket_provider_factory import create_provider


class BraketInvocation(Invocation):

    def __init__(self, request_data: InvocationRequest):
        super().__init__(request_data)

    def _export_circuit(self, circuit):
        """
        Initiates the export of a quantum circuit using BraketCircuitExportTask.

        This method creates a BraketCircuitExportTask with the provided circuit
        and submits it to the circuit exporting pool for asynchronous execution.

        Args:
            circuit: The quantum circuit to be exported.

        Raises:
            ValueError: If circuit_export_url or backend_information is invalid.
        """
        self.logger.debug("Exporting circuit")

        if not self.circuit_export_url or not self.backend_information:
            self.logger.error(
                    "Invalid circuit_export_url or backend_information")
            raise ValueError(
                    "Circuit export URL and backend information must not be None")

        circuit_export_task = BraketCircuitExportTask(
                circuit_data_holder=CircuitDataHolder(circuit,
                                                      self.circuit_export_url),
                backend_data_holder=BackendDataHolder(self.backend_information,
                                                      self.authentication.user_token),
                project_header=self.project_header,
                workspace_header=self.workspace_header)
        circuit_exporting_pool.submit(circuit_export_task.do)
        self.logger.info("Circuit export task submitted")

    def _create_provider(self):
        """
        Creates a provider instance using the specified backend information.

        This method utilizes the `create_provider` function to generate a provider
        based on the provider tag, SDK, and authentication details from the
        backend information.

        Returns:
            Provider: An instance of the provider created using the specified details.

        Raises:
            ValueError: If backend_information or authentication is invalid.
        """
        self.logger.info("Creating provider")

        provider = create_provider(
                provider_type=self.backend_information.provider_tag,
                sdk=self.sdk,
                authentication=self.backend_information.authentication)
        self.logger.debug("Provider created")
        return provider

    def _create_device(self, provider: Provider):
        """
        Creates a device instance using the provider and specified backend information.

        This method uses the `create_device` function to generate a device
        based on the provider instance, device name, authentication details, and
        SDK from the backend information.

        Args:
            provider (Provider): An instance of the provider used to create the device.

        Returns:
            CustomDevice: An instance of the device created using the specified details.

        Raises:
            ValueError: If backend_information or authentication is invalid.
        """
        self.logger.debug('Creating device')
        device = create_device(provider=provider,
                               device_specification=self.backend_information.device_name,
                               authentication=self.backend_information.authentication,
                               sdk=self.sdk)

        self.logger.debug("Device created successfully")
        return device

    def _get_qubit_amount(self, circuit):
        """
        Retrieves the number of qubits used in the given quantum circuit.

        Args:
            circuit: The quantum circuit for which to retrieve the qubit count.

        Returns:
            int: The number of qubits used in the circuit.

        Raises:
            ValueError: If the circuit is not of type Circuit.
        """
        self.logger.debug("Retrieving qubit count")

        if isinstance(circuit, Circuit):
            qubit_count = circuit.qubit_count
            self.logger.info(f"Qubit count: {qubit_count}")
            return qubit_count

        self.logger.error(f"Invalid circuit type: {type(circuit)}")
        raise ValueError(f"Invalid circuit type: {type(circuit)}")
