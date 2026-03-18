"""
Predefined quantum circuit library and custom circuit builder.
"""

import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit.library import QFT


def get_predefined_circuit(name: str) -> QuantumCircuit:
    """Return a predefined quantum circuit by name."""
    builders = {
        "GHZ State (3-qubit)":                 _ghz_3,
        "GHZ State (5-qubit)":                 _ghz_5,
        "Quantum Fourier Transform (4-qubit)": _qft_4,
        "Grover's Search (3-qubit)":           _grover_3,
        "Bernstein-Vazirani (4-qubit)":        _bv_4,
        "VQE Ansatz (4-qubit)":                _vqe_ansatz_4,
        "Random Circuit (4-qubit)":            _random_4,
        "Quantum Teleportation (3-qubit)":     _teleportation_3,
    }
    builder = builders.get(name)
    if builder is None:
        raise ValueError(f"Unknown circuit: {name}")
    return builder()


# ── Predefined circuit builders ──────────────────────────────────────

def _ghz_3() -> QuantumCircuit:
    qc = QuantumCircuit(3, name="GHZ-3")
    qc.h(0)
    qc.cx(0, 1)
    qc.cx(1, 2)
    qc.measure_all()
    return qc


def _ghz_5() -> QuantumCircuit:
    qc = QuantumCircuit(5, name="GHZ-5")
    qc.h(0)
    for i in range(4):
        qc.cx(i, i + 1)
    qc.measure_all()
    return qc


def _qft_4() -> QuantumCircuit:
    qc = QuantumCircuit(4, name="QFT-4")
    # Build a decomposed QFT so there's something to optimize
    qft = QFT(4, do_swaps=True).decompose()
    qc.compose(qft, inplace=True)
    qc.measure_all()
    return qc


def _grover_3() -> QuantumCircuit:
    """Simple 3-qubit Grover searching for |111⟩."""
    qc = QuantumCircuit(3, name="Grover-3")
    # Hadamards
    qc.h([0, 1, 2])
    # Oracle for |111⟩
    qc.ccx(0, 1, 2)
    qc.z(2)
    qc.ccx(0, 1, 2)
    # Diffusion
    qc.h([0, 1, 2])
    qc.x([0, 1, 2])
    qc.ccx(0, 1, 2)
    qc.z(2)
    qc.ccx(0, 1, 2)
    qc.x([0, 1, 2])
    qc.h([0, 1, 2])
    qc.measure_all()
    return qc


def _bv_4() -> QuantumCircuit:
    """Bernstein-Vazirani with secret string s=1011."""
    secret = "1011"
    n = len(secret)
    qc = QuantumCircuit(n + 1, n, name="BV-4")
    # Put auxiliary in |−⟩
    qc.x(n)
    qc.h(n)
    # Hadamards on input
    qc.h(range(n))
    qc.barrier()
    # Oracle
    for i, bit in enumerate(reversed(secret)):
        if bit == "1":
            qc.cx(i, n)
    qc.barrier()
    # Hadamards & measure
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def _vqe_ansatz_4() -> QuantumCircuit:
    """Hardware-efficient VQE ansatz with two layers."""
    qc = QuantumCircuit(4, name="VQE-Ansatz-4")
    rng = np.random.default_rng(42)
    for layer in range(2):
        for q in range(4):
            qc.ry(rng.uniform(0, np.pi), q)
            qc.rz(rng.uniform(0, np.pi), q)
        for q in range(3):
            qc.cx(q, q + 1)
        if layer == 0:
            qc.barrier()
    qc.measure_all()
    return qc


def _random_4() -> QuantumCircuit:
    """A reproducible random circuit with redundancy to optimise away."""
    qc = QuantumCircuit(4, name="Random-4")
    rng = np.random.default_rng(123)
    gates_1q = ["h", "x", "y", "z", "s", "t"]
    for _ in range(12):
        g = rng.choice(gates_1q)
        q = int(rng.integers(0, 4))
        getattr(qc, g)(q)
        if rng.random() > 0.4:
            c, t = int(rng.integers(0, 4)), int(rng.integers(0, 4))
            if c != t:
                qc.cx(c, t)
    # Add some intentional redundancy (X-X cancels, H-H cancels)
    qc.x(0); qc.x(0)
    qc.h(1); qc.h(1)
    qc.cx(2, 3); qc.cx(2, 3)
    qc.measure_all()
    return qc


def _teleportation_3() -> QuantumCircuit:
    """Quantum teleportation protocol."""
    qc = QuantumCircuit(3, 3, name="Teleportation")
    # Prepare state to teleport
    qc.rx(np.pi / 4, 0)
    qc.barrier()
    # Create Bell pair
    qc.h(1)
    qc.cx(1, 2)
    qc.barrier()
    # Bell measurement
    qc.cx(0, 1)
    qc.h(0)
    qc.barrier()
    qc.measure(0, 0)
    qc.measure(1, 1)
    # Corrections
    qc.x(2).c_if(1, 1)
    qc.z(2).c_if(0, 1)
    qc.measure(2, 2)
    return qc


# ── Custom circuit builder ───────────────────────────────────────────

def build_custom_circuit(num_qubits: int, gate_list: list[dict]) -> QuantumCircuit:
    """
    Build a circuit from a list of gate dicts.

    Each dict has:
        gate:   str   — gate name (H, X, CX, Rx, …)
        qubits: list  — qubit indices
        param:  float — (optional) rotation angle
    """
    qc = QuantumCircuit(num_qubits, name="Custom")

    for g in gate_list:
        name   = g["gate"].upper()
        qubits = g["qubits"]
        param  = g.get("param", 0.0)

        if name == "H":
            qc.h(qubits[0])
        elif name == "X":
            qc.x(qubits[0])
        elif name == "Y":
            qc.y(qubits[0])
        elif name == "Z":
            qc.z(qubits[0])
        elif name == "S":
            qc.s(qubits[0])
        elif name == "T":
            qc.t(qubits[0])
        elif name == "RX":
            qc.rx(param, qubits[0])
        elif name == "RY":
            qc.ry(param, qubits[0])
        elif name == "RZ":
            qc.rz(param, qubits[0])
        elif name == "CX":
            qc.cx(qubits[0], qubits[1])
        elif name == "CZ":
            qc.cz(qubits[0], qubits[1])
        elif name == "SWAP":
            qc.swap(qubits[0], qubits[1])
        elif name in ("CCX", "CCX (TOFFOLI)"):
            qc.ccx(qubits[0], qubits[1], qubits[2])
        elif name in ("CSWAP", "CSWAP (FREDKIN)"):
            qc.cswap(qubits[0], qubits[1], qubits[2])

    qc.measure_all()
    return qc
