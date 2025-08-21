from qiskit import (
    QuantumCircuit,
    QuantumRegister,
    AncillaRegister,
    qasm3,
    ClassicalRegister,
)
from .circuit_query_params import QueryParams
from qiskit.circuit import Qubit
import requests
import getpass
import os
from .auth import authenticate

API_BASE = "https://api.q1ram.com"


# authenticate()


def authenticate():
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    response = requests.post(
        f"{API_BASE}/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code == 200:
        token = response.json()["access_token"]
        os.environ["Q1RAM_TOKEN"] = token
        print("✅ Login successful!")
    else:
        raise Exception(f"Login failed: {response.text}")


class Q1RAM:
    def __init__(
        self,
        circuit: QuantumCircuit,
        number_address_qubits: int,
        number_data_qubits: int,
        prefix: str = "",
    ):
        self.base_url = API_BASE
        self.qc = circuit
        self.prefix = prefix
        self.number_address_qubits = number_address_qubits
        self.number_data_qubits = number_data_qubits
        self.qr_A = QuantumRegister(self.number_address_qubits, name=self.prefix + "A")
        self.qr_D = QuantumRegister(self.number_data_qubits, name=self.prefix + "D")
        self.qr_dq = QuantumRegister(1, name=self.prefix + "dq")

        self.qc.add_register(self.qr_A)
        self.qc.add_register(self.qr_D)
        self.qc.add_register(self.qr_dq)

        resp = requests.get(
            f"{self.base_url}/circuit/num_ancilla/?number_address_bits={self.number_address_qubits}"
        )
        if resp.status_code != 200:
            raise Exception(f"Failed to get number of ancilla qubits: {resp.text}")
        number_ancilla_qubits = resp.json()
        if number_ancilla_qubits > 0:
            self.qr_tof_ancilla = AncillaRegister(
                number_ancilla_qubits, name=self.prefix + "anc"
            )
            self.qc.add_register(self.qr_tof_ancilla)
        else:
            self.qr_tof_ancilla = None

        self.qr_AR: QuantumRegister | None = None
        self.qr_DR: QuantumRegister | None = None

        self.qc.h(self.qr_A)
        self.read_qasm = """ """  # to be initialized via api
        self.write_qasm = """"""  # to be initialized via api

    @property
    def ordered_qram_qubits(self):
        res = [
            self.qr_dq[0],
            *self.qr_A,
            *self.qr_D,
            *(self.qr_AR if self.qr_AR else []),
            *(self.qr_DR if self.qr_DR else []),
        ]

        if hasattr(self, "qr_tof_ancilla"):
            res += [*(self.qr_tof_ancilla if self.qr_tof_ancilla else [])]

        return res

    def read(
        self,
        address_register: QuantumRegister | list[Qubit] | list[int] = None,
        data_register: QuantumRegister | list[Qubit] | list[int] = None,
        address_value: list[int] | None = None,
    ):
        token = os.environ.get("Q1RAM_TOKEN")
        if not token:
            raise Exception("❌ No token found. Please login first.")

        headers = {"Authorization": f"Bearer {token}"}

        response = requests.post(
            f"{self.base_url}/circuit/read/",
            json={
                "number_address_bits": self.number_address_qubits,
                "number_data_bits": self.number_data_qubits,
                "address_value": address_value
                if isinstance(address_value, list)
                else [],
                "data_value": [],
            },
            headers=headers,
        )

        self.read_qasm = response.json().get("circuit")
        if not self.read_qasm:
            raise Exception("Failed to get the read circuit")
        qc_read = qasm3.loads(self.read_qasm)
        qc_read.name = "Q1RAM-Read"

        if address_register is not None:
            self.qr_AR = address_register
        elif self.qr_AR is None:
            self.qr_AR = QuantumRegister(
                self.number_address_qubits, name=self.prefix + "AR"
            )
            self.qc.add_register(self.qr_AR)

        if data_register is not None:
            self.qr_DR = data_register
        elif self.qr_DR is None:
            self.qr_DR = QuantumRegister(
                self.number_data_qubits, name=self.prefix + "DR"
            )
            self.qc.add_register(self.qr_DR)

        self.qc.append(qc_read, self.ordered_qram_qubits)

    def read_all(
        self,
        address_register: QuantumRegister | list[Qubit] | list[int] = None,
        data_register: QuantumRegister | list[Qubit] | list[int] = None,
    ):
        token = os.environ.get("Q1RAM_TOKEN")
        if not token:
            raise Exception("❌ No token found. Please login first.")

        headers = {"Authorization": f"Bearer {token}"}

        response = requests.post(
            f"{self.base_url}/circuit/read-all/",
            json={
                "number_address_bits": self.number_address_qubits,
                "number_data_bits": self.number_data_qubits,
                "address_value": [],
                "data_value": [],
            },
            headers=headers,
        )

        self.read_qasm = response.json().get("circuit")
        if not self.read_qasm:
            raise Exception("Failed to get the read circuit")
        qc_read = qasm3.loads(self.read_qasm)
        qc_read.name = "Q1RAM-Read ALL"

        if address_register is not None:
            self.qr_AR = address_register
        elif self.qr_AR is None:
            self.qr_AR = QuantumRegister(
                self.number_address_qubits, name=self.prefix + "AR"
            )
            self.qc.add_register(self.qr_AR)

        if data_register is not None:
            self.qr_DR = data_register
        elif self.qr_DR is None:
            self.qr_DR = QuantumRegister(
                self.number_data_qubits, name=self.prefix + "DR"
            )
            self.qc.add_register(self.qr_DR)

        self.qc.append(qc_read, self.ordered_qram_qubits)

    def write(
        self,
        address_register: QuantumRegister | list[Qubit] | list[int] = None,
        data_register: QuantumRegister | list[Qubit] | list[int] = None,
        address_value: list[int] | None = None,
        data_value: list[int] | None = None,
    ):
        token = os.environ.get("Q1RAM_TOKEN")
        if not token:
            raise Exception("❌ No token found. Please login first.")

        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{self.base_url}/circuit/write/",
            json={
                "number_address_bits": self.number_address_qubits,
                "number_data_bits": self.number_data_qubits,
                "address_value": address_value
                if isinstance(address_value, list)
                else None,
                "data_value": data_value if isinstance(data_value, list) else None,
            },
            headers=headers,
        )

        self.write_qasm = response.json().get("circuit")
        if not self.write_qasm:
            raise Exception("Failed to get the write circuit")
        qc_write = qasm3.loads(self.write_qasm)
        qc_write.name = "Q1RAM-Write"

        if address_register is not None:
            self.qr_AR = address_register
        elif self.qr_AR is None:
            self.qr_AR = QuantumRegister(
                self.number_address_qubits, name=self.prefix + "AR"
            )
            self.qc.add_register(self.qr_AR)

        if data_register is not None:
            self.qr_DR = data_register
        elif self.qr_DR is None:
            self.qr_DR = QuantumRegister(
                self.number_data_qubits, name=self.prefix + "DR"
            )
            self.qc.add_register(self.qr_DR)

        self.qc.append(qc_write, self.ordered_qram_qubits)

    def reset_bus(self):
        if self.qr_AR is None or self.qr_DR is None:
            raise Exception(
                "Address and Data registers must be set before resetting the bus."
            )

        self.qc.reset(self.qr_AR)
        self.qc.reset(self.qr_DR)

    def measure_bus(self):
        if self.qr_AR is None or self.qr_DR is None:
            raise Exception(
                "Address and Data registers must be set before measurement."
            )

        self.cr_address = ClassicalRegister(
            self.number_address_qubits, name=self.prefix + f"c_{self.qr_AR.name}"
        )
        self.cr_data = ClassicalRegister(
            self.number_data_qubits, name=self.prefix + f"c_{self.qr_DR.name}"
        )
        self.qc.add_register(self.cr_address)
        self.qc.add_register(self.cr_data)
        self.qc.measure(self.qr_AR, self.cr_address)
        self.qc.measure(self.qr_DR, self.cr_data)
