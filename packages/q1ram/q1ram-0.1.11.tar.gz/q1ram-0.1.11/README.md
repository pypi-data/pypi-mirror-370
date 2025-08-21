# Q1RAM Client API Methods

Q1RAM (Quantum Random Access Memory) is a quantum memory architecture designed to enable efficient storage and retrieval of quantum data at an any arbitrary address(es) with O(1) complexity, as introduced in the US patent ["A Novel Efficient Quantum Random Access Memory"](https://q1ram.com/storage/pdfs/1751819309_QRAM%20sy.pdf). This client API provides methods to interact with Q1RAM, allowing manipulation of quantum memory in both single and superposition states.
## Notes

- All API calls require valid authentication credentials, by registering on [https://q1ram.com](https://q1ram.com).
- The methods interact with the Q1RAM backend via HTTP requests and update the local quantum circuit accordingly.
- For advanced usage, you can provide custom quantum registers for address and data.
- 
## Authentication
Before using any method, authenticate with the API:
```python
from q1ram import authenticate
authenticate()
```

---
## 1. `read`

**Purpose:**  
Reads data from the Q1RAM at a specified address or in superposition.

**Signature:**  
```python
read(address_register=None, data_register=None, address_value=None, data_value=None)
```

**Parameters:**
- `address_register`: Optional. QuantumRegister or list specifying the address qubits.
- `data_register`: Optional. QuantumRegister or list specifying the data qubits.
- `address_value`: Optional. List of integers specifying the classical address to read from. If omitted, reads in superposition.
- `data_value`: Optional. List of integers specifying the classical data to match (rarely used for read).

**Usage Examples:**
- Read from a superposition address states:
  ```python
  qram.read(address_value=[0, 1])
  ```

---

## 2. `write`

**Purpose:**  
Writes data to the Q1RAM at a single or superposition address states.

**Signature:**  
```python
write(address_register=None, data_register=None, address_value=None, data_value=None)
```

**Parameters:**
- `address_register`: Optional. QuantumRegister or list specifying the address qubits.
- `data_register`: Optional. QuantumRegister or list specifying the data qubits.
- `address_value`: Optional. List of integers specifying the classical address to write to. If omitted, writes in superposition.
- `data_value`: Required. List of integers specifying the data to write.

**Usage Examples:**
- Write to a specific address:
  ```python
  qram.write(address_value=[0, 1], data_value=[5])
  ```

---

## 3. `read_all` 

**Purpose:**  
Reads all data from Q1RAM, typically used to retrieve the full memory contents.

**Signature:**  
```python
read_all()
```

**Usage Example:**
```python
qram.read_all()
```

---




## Example Workflow

```python
from q1ram_client.q1ram.circuit import Q1RAM, authenticate
from qiskit import QuantumCircuit

authenticate()
qc = QuantumCircuit()
qram = Q1RAM(qc, number_address_qubits=2, number_data_qubits=2)

# Write data to address [0, 1]
qram.write(address_value=[0, 1], data_value=[1, 0])

# Read data from address [0, 1]
qram.read(address_value=[0, 1])

# Write data in superposition
qram.write(data_value=[1, 1])

# Read all data in superposition
qram.read()
```

