#  Quapp Platform Project
#  braket_circuit_export_task.py
#  Copyright © CITYNOW Co. Ltd. All rights reserved.
from braket.circuits import Circuit
from qiskit import QuantumCircuit
from quapp_common.async_tasks.export_circuit_task import CircuitExportTask
from quapp_common.data.async_task.circuit_export.backend_holder import \
    BackendDataHolder
from quapp_common.data.async_task.circuit_export.circuit_holder import \
    CircuitDataHolder
from quapp_common.data.response.custom_header import CustomHeader

from ..util.circuit_convert_utils import braket_to_qiskit


class BraketCircuitExportTask(CircuitExportTask):

    def __init__(self, circuit_data_holder: CircuitDataHolder,
                 backend_data_holder: BackendDataHolder,
                 project_header: CustomHeader, workspace_header: CustomHeader):
        super().__init__(circuit_data_holder, backend_data_holder,
                         project_header, workspace_header)

    def _transpile_circuit(self) -> QuantumCircuit:
        """
        Transpiles the circuit held in the circuit_data_holder to a Qiskit quantum circuit.

        This method checks if the circuit is an instance of Braket's Circuit. If so, it
        converts it to a Qiskit QuantumCircuit using the braket_to_qiskit utility function.

        Returns:
            QuantumCircuit: Transpiled Qiskit quantum circuit.

        Raises:
            ValueError: If the circuit is not of type Circuit.
        """
        self.logger.info('Transpiling Braket circuit to Qiskit')
        circuit = self.circuit_data_holder.circuit
        self.logger.debug(f'Fetched circuit from holder: {circuit}')

        if not circuit:
            self.logger.error('Circuit must not be None')
            raise ValueError('Circuit must not be None')

        if isinstance(circuit, Circuit):
            self.logger.debug('Converting Braket Circuit to Qiskit circuit.')
            return braket_to_qiskit(circuit)

        self.logger.error(f'Expected Braket Circuit, got {type(circuit)}')
        raise ValueError(f'Expected Braket Circuit, got {type(circuit)}')
