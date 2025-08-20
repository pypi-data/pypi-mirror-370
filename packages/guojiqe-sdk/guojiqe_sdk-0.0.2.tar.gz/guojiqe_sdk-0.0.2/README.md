# GuojiQE-SDK
GuojiQE-SDK is a Python SDK for interacting with the Guoji Quantum and Electronic Computing Service Platform.

This SDK supports submitting and executing Qiskit circuit code on Guoji Quantum's superconducting quantum computers and simulators.

# Installation
You can install GuojiQE-SDK using pip:

```bash
pip install guojiqe-sdk
```

# Usage
## Step 1: Create a service instance
```python
from guojiqe_sdk.runtime_service import GjqRuntimeService
service = GjqRuntimeService(channel="CPU_FULL_AMPLITUDE_SIMULATOR")
```
channel: Selects the specified type of quantum device, including simulators and quantum computers. 
- "CPU_FULL_AMPLITUDE_SIMULATOR", 
- "CPU_NOISY_SIMULATOR", 
- "CPU_SINGLE_AMPLITUDE_SIMULATOR", 
- "CPU_PARTIAL_AMPLITUDE_SIMULATOR", 
- "GPU_FULL_AMPLITUDE_SIMULATOR", 
- "GPU_NOISY_SIMULATOR", 
- "GPU_SINGLE_AMPLITUDE_SIMULATOR", 
- "GPU_PARTIAL_AMPLITUDE_SIMULATOR", 
- "NPU_FULL_AMPLITUDE_SIMULATOR", 
- "NPU_NOISY_SIMULATOR", 
- "NPU_SINGLE_AMPLITUDE_SIMULATOR", 
- "NPU_PARTIAL_AMPLITUDE_SIMULATOR", 
- "SUPERCONDUCTING_QUANTUM_COMPUTER"

## Step 2: Get the backend
### Method 1: Automatically select the least busy backend
```python
backend = service.least_busy()
```

### Method 2: Provide the user with a list of available backends of a specified type, allowing the user to select a backend by viewing this information.
#### 2.1 Viewing a list of available backends of a specified type
```python
backends = service.backends()
for backend in backends:
    print("Name:", backend.name, "Number of qubits:", backend.num_qubits, "Device ID:", backend.device_id)
```

#### 2.2 Selecting a backend with a specified `device_id` based on the output
```python
backend = service.backend("tgq-super-0001")
```

### Step 3: Create a circuit
Create a circuit using Qiskit

```python
from qiskit import QuantumCircuit
circuit = QuantumCircuit(2)
circuit.x(range(2))
circuit.cz(0, 1)
circuit.measure_all()
```

## Step 4: Run the circuit on the backend
Submit the circuit using `run()` in the backend, and get the calculation results in Qiskit Result format using `result()` in the job

```python
job = backend.run(circuit)
result = job.result().results[0].data.to_dict()
print("Backend run result:", result)
```