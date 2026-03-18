"""
Hardware-aware optimization — transpile circuits to target device topologies
using Qiskit's GenericBackendV2 fake backends.
"""

from __future__ import annotations
from dataclasses import dataclass
from qiskit import QuantumCircuit, transpile
from qiskit.providers.fake_provider import GenericBackendV2


@dataclass
class HardwareResult:
    """Result of hardware-aware transpilation."""
    transpiled_circuit: QuantumCircuit
    backend_name: str
    num_qubits_device: int
    basis_gates: list[str]
    depth: int
    gate_count: int
    swap_count: int
    cx_count: int
    routing_overhead: str      # explanation of SWAP overhead


def get_fake_backend(num_qubits: int) -> GenericBackendV2:
    """Create a Qiskit GenericBackendV2 with the given qubit count."""
    return GenericBackendV2(num_qubits=num_qubits, seed=42)


def hardware_transpile(
    qc: QuantumCircuit,
    num_qubits_device: int,
    optimization_level: int = 2,
) -> HardwareResult:
    """
    Transpile a circuit for a target hardware topology.

    Args:
        qc:                  The quantum circuit to transpile
        num_qubits_device:   Number of qubits on the target device
        optimization_level:  Qiskit optimization level (0-3)
    """
    if qc.num_qubits > num_qubits_device:
        raise ValueError(
            f"Circuit has {qc.num_qubits} qubits but target device only "
            f"has {num_qubits_device}. Select a larger device."
        )

    backend = get_fake_backend(num_qubits_device)
    basis_gates = backend.operation_names

    transpiled = transpile(
        qc,
        backend=backend,
        optimization_level=optimization_level,
        seed_transpiler=42,
    )

    # Count operations
    ops = dict(transpiled.count_ops())
    gate_count = sum(v for k, v in ops.items() if k not in ("barrier", "measure"))
    swap_count = ops.get("swap", 0)
    cx_count   = ops.get("cx", 0) + ops.get("ecr", 0) + ops.get("cz", 0)

    # Build routing explanation
    routing = _routing_explanation(qc, transpiled, swap_count, cx_count)

    return HardwareResult(
        transpiled_circuit=transpiled,
        backend_name=f"Generic {num_qubits_device}-Qubit Device",
        num_qubits_device=num_qubits_device,
        basis_gates=list(basis_gates),
        depth=transpiled.depth(),
        gate_count=gate_count,
        swap_count=swap_count,
        cx_count=cx_count,
        routing_overhead=routing,
    )


def _routing_explanation(
    original: QuantumCircuit,
    transpiled: QuantumCircuit,
    swaps: int,
    cx: int,
) -> str:
    """Generate an explanation of routing overhead."""
    orig_ops = dict(original.count_ops())
    orig_cx  = orig_ops.get("cx", 0) + orig_ops.get("cnot", 0)

    lines = []
    if swaps > 0:
        lines.append(
            f"The transpiler inserted **{swaps} SWAP gate(s)** to route "
            f"qubits across the device's limited connectivity."
        )
    else:
        lines.append(
            "✅ No SWAP gates were needed — the circuit maps well to this topology."
        )

    added_cx = cx - orig_cx
    if added_cx > 0:
        lines.append(
            f"Routing added **{added_cx} extra CX gate(s)** (including SWAP decompositions)."
        )

    lines.append(
        f"\nFinal transpiled depth: **{transpiled.depth()}** | "
        f"Original depth: **{original.depth()}**"
    )
    return "\n".join(lines)
