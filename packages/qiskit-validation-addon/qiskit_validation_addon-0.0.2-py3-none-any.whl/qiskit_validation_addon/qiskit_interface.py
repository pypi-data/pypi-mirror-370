from typing import Any
from qiskit import qasm2
from .classifier import classify_quantum_circuit, ClassificationResult

def classify_qiskit_circuit(circuit: Any) -> ClassificationResult:
    """
    Accepts a Qiskit QuantumCircuit object, dumps its QASM2 representation,
    and classifies it as 'Malicious' or 'Benign'.
    """
    try:
        # Qiskit >= 0.45 uses qasm2 exporter
        qasm_str = qasm2.dumps(circuit)
    except Exception:
        # Fallback for older Qiskit versions
        qasm_str = circuit.qasm()
    return classify_quantum_circuit(qasm_str)
