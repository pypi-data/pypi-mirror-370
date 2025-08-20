#  Quapp Platform Project
#  circuit_convert_utils.py
#  Copyright © CITYNOW Co. Ltd.All rights reserved.

from braket.circuits import Circuit
from pytket.extensions.braket import braket_to_tk
from pytket.qasm import circuit_to_qasm_str
from qiskit import QuantumCircuit
from qiskit.qasm2 import loads
from quapp_common.config.logging_config import logger

logger = logger.bind(context="CircuitConvertUtils")


def braket_to_qasm2_str(circuit: Circuit) -> str:
    logger.debug("braket_to_qasm2_str()")

    return circuit_to_qasm_str(braket_to_tk(circuit))


def qasm2_str_to_qiskit(qasm_str: str) -> QuantumCircuit:
    logger.debug("qasm2_str_to_qiskit()")

    return loads(qasm_str)


def braket_to_qiskit(circuit: Circuit) -> QuantumCircuit:
    logger.debug("braket_to_qiskit()")

    qasm_str = braket_to_qasm2_str(circuit)
    return qasm2_str_to_qiskit(qasm_str)
