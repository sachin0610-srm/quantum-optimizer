"""
Noise simulation module — runs circuits under configurable noise models
and compares original-vs-optimized fidelity.
"""

from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import (
    NoiseModel,
    depolarizing_error,
    thermal_relaxation_error,
)


@dataclass
class NoiseResult:
    """Simulation results under noise."""
    counts: dict
    total_shots: int
    success_probability: float    # probability of the most-likely outcome
    entropy: float                # Shannon entropy of the distribution


@dataclass
class NoiseComparison:
    """Comparison between original and optimized circuits under noise."""
    original: NoiseResult
    optimized: NoiseResult
    fidelity_improvement: float   # positive = optimized is better


def build_noise_model(
    error_rate: float = 0.01,
    t1_us: float = 50.0,
    t2_us: float = 70.0,
    gate_time_ns: float = 50.0,
) -> NoiseModel:
    """
    Build a simple noise model with depolarizing + thermal relaxation.

    Args:
        error_rate:    single-qubit depolarizing error probability
        t1_us:         T1 relaxation time (µs)
        t2_us:         T2 dephasing time (µs)
        gate_time_ns:  gate execution time (ns)
    """
    noise_model = NoiseModel()

    # Single-qubit errors
    error_1q = depolarizing_error(error_rate, 1)
    thermal_1q = thermal_relaxation_error(
        t1_us * 1e3,         # convert µs → ns for consistency
        min(t2_us, t1_us) * 1e3,
        gate_time_ns,
    )
    combined_1q = error_1q.compose(thermal_1q)
    noise_model.add_all_qubit_quantum_error(combined_1q, ["u1", "u2", "u3", "rx", "ry", "rz", "h", "x", "y", "z", "s", "t"])

    # Two-qubit errors (higher rate)
    error_2q = depolarizing_error(error_rate * 10, 2)
    noise_model.add_all_qubit_quantum_error(error_2q, ["cx", "cz", "swap"])

    return noise_model


def simulate_with_noise(
    qc: QuantumCircuit,
    noise_model: NoiseModel,
    shots: int = 4096,
) -> NoiseResult:
    """Run a circuit on the Aer simulator with a noise model."""
    backend = AerSimulator(noise_model=noise_model)
    t_qc = transpile(qc, backend=backend, optimization_level=0)
    result = backend.run(t_qc, shots=shots).result()
    counts = result.get_counts()

    # Compute statistics
    total = sum(counts.values())
    probs = np.array(list(counts.values())) / total
    success_prob = float(np.max(probs))
    entropy = float(-np.sum(probs * np.log2(probs + 1e-12)))

    return NoiseResult(
        counts=counts,
        total_shots=total,
        success_probability=round(success_prob, 4),
        entropy=round(entropy, 4),
    )


def compare_noise(
    original: QuantumCircuit,
    optimized: QuantumCircuit,
    noise_model: NoiseModel,
    shots: int = 4096,
) -> NoiseComparison:
    """Simulate both circuits under noise and compare."""
    orig_result = simulate_with_noise(original, noise_model, shots)
    opt_result  = simulate_with_noise(optimized, noise_model, shots)

    fid_improvement = opt_result.success_probability - orig_result.success_probability

    return NoiseComparison(
        original=orig_result,
        optimized=opt_result,
        fidelity_improvement=round(fid_improvement, 4),
    )
