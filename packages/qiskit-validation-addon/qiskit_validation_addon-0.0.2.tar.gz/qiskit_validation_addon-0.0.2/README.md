# QASM Validator

Classify quantum circuits as "Malicious" or "Benign" using a finetuned LLM adapter.

## Installation

```bash
pip install .
```

## Usage

```python
from qiskit_validation_addon import classify_quantum_circuit

result = classify_quantum_circuit("""
OPENQASM 2.0;
include "qelib1.inc";
qreg q[2];
creg c[2];
h q[0];
cx q[0],q[1];
measure q[0] -> c[0];
measure q[1] -> c[1];
""")
print(result.label)  # "Malicious" or "Benign"
print(result.raw_response)  # Raw model output
```
