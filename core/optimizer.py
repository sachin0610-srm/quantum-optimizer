"""
Optimization engine — wraps Qiskit transpiler passes into named strategies.
"""

from dataclasses import dataclass, field
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import PassManager
from qiskit.transpiler.passes import (
    Optimize1qGates,
    Optimize1qGatesDecomposition,
    CommutativeCancellation,
    RemoveDiagonalGatesBeforeMeasure,
    RemoveResetInZeroState,
    Collect2qBlocks,
    ConsolidateBlocks,
)

@dataclass
class CircuitMetrics:
    """Metrics for a quantum circuit."""
    depth: int = 0
    gate_count: int = 0
    cx_count: int = 0
    single_qubit_gates: int = 0
    two_qubit_gates: int = 0
    num_qubits: int = 0
    operations: dict = field(default_factory=dict)

    @classmethod
    def from_circuit(cls, qc: QuantumCircuit) -> "CircuitMetrics":
        ops = dict(qc.count_ops())
        # Exclude barriers and measurements from gate count
        gate_count = sum(v for k, v in ops.items() if k not in ("barrier", "measure"))
        cx_count = ops.get("cx", 0) + ops.get("cnot", 0)

        # Count single vs two-qubit gates
        single_q = 0
        two_q = 0
        for instruction in qc.data:
            if instruction.operation.name in ("barrier", "measure"):
                continue
            n = len(instruction.qubits)
            if n == 1:
                single_q += 1
            elif n >= 2:
                two_q += 1

        return cls(
            depth=qc.depth(),
            gate_count=gate_count,
            cx_count=cx_count,
            single_qubit_gates=single_q,
            two_qubit_gates=two_q,
            num_qubits=qc.num_qubits,
            operations=ops,
        )


@dataclass
class OptimizationResult:
    """Result of an optimization run."""
    original_circuit: QuantumCircuit
    optimized_circuit: QuantumCircuit
    original_metrics: CircuitMetrics
    optimized_metrics: CircuitMetrics
    strategy: str
    explanation: str
    improvements: dict = field(default_factory=dict)

    def __post_init__(self):
        self.improvements = self._compute_improvements()

    def _compute_improvements(self) -> dict:
        """Compute percentage improvements for each metric."""
        results = {}
        for metric_name in ["depth", "gate_count", "cx_count", "single_qubit_gates", "two_qubit_gates"]:
            orig = getattr(self.original_metrics, metric_name)
            opt  = getattr(self.optimized_metrics, metric_name)
            if orig > 0:
                pct = ((orig - opt) / orig) * 100
            else:
                pct = 0.0
            results[metric_name] = {
                "original": orig,
                "optimized": opt,
                "improvement_pct": round(pct, 1),
            }
        return results


def get_metrics(qc: QuantumCircuit) -> CircuitMetrics:
    """Extract metrics from a circuit."""
    return CircuitMetrics.from_circuit(qc)


def optimize_circuit(qc: QuantumCircuit, strategy: str = "Medium") -> OptimizationResult:
    """
    Optimize a quantum circuit using the specified strategy.

    Strategies:
        Light  — Optimize1qGates + CXCancellation
        Medium — + CommutativeCancellation + RemoveDiagonalGatesBeforeMeasure
        Heavy  — + ConsolidateBlocks (block collection + unitary synthesis)
        Full   — Qiskit transpile with optimization_level=3
    """
    original_metrics = get_metrics(qc)

    if strategy == "Full":
        optimized = transpile(qc, optimization_level=3, seed_transpiler=42)
        explanation = _build_explanation("Full", original_metrics, get_metrics(optimized))
    else:
        pm = _build_pass_manager(strategy)
        optimized = pm.run(qc)
        explanation = _build_explanation(strategy, original_metrics, get_metrics(optimized))

    optimized_metrics = get_metrics(optimized)

    return OptimizationResult(
        original_circuit=qc,
        optimized_circuit=optimized,
        original_metrics=original_metrics,
        optimized_metrics=optimized_metrics,
        strategy=strategy,
        explanation=explanation,
    )


def _build_pass_manager(strategy: str) -> PassManager:
    """Build a Qiskit PassManager for the given strategy."""
    passes = []

    if strategy in ("Light", "Medium", "Heavy"):
        passes.extend([
            Optimize1qGatesDecomposition(),
            CommutativeCancellation(),  # replaced CXCancellation
        ])

    if strategy in ("Medium", "Heavy"):
        passes.extend([
            CommutativeCancellation(),
            RemoveDiagonalGatesBeforeMeasure(),
            RemoveResetInZeroState(),
        ])

    if strategy == "Heavy":
        passes.extend([
            Collect2qBlocks(),
            ConsolidateBlocks(),
            Optimize1qGatesDecomposition(),
            CommutativeCancellation(),  # replaced CXCancellation
        ])

    return PassManager(passes)


def _build_explanation(strategy: str, orig: CircuitMetrics, opt: CircuitMetrics) -> str:
    """Generate a human-readable explanation of what the optimization did."""
    lines = [f"### Optimization Strategy: **{strategy}**\n"]

    strategy_descriptions = {
        "Light": (
            "Applied basic single-qubit gate optimization and CX gate cancellation. "
            "This merges consecutive single-qubit rotations and removes adjacent "
            "CX pairs that cancel each other out."
        ),
        "Medium": (
            "Built on Light optimizations, adding commutative gate cancellation "
            "(reorders commuting gates to reveal new cancellation opportunities) "
            "and removal of diagonal gates before measurement (since they only "
            "affect phase, which is lost during measurement)."
        ),
        "Heavy": (
            "Applied the full pipeline including block consolidation, which "
            "collects sequences of 2-qubit gates into unitary blocks and "
            "re-synthesizes them using fewer gates. This is particularly "
            "effective for circuits with many consecutive CNOT gates."
        ),
        "Full": (
            "Used Qiskit's highest optimization level (level 3), which applies "
            "all available transpiler passes including layout-aware routing, "
            "gate direction optimization, and aggressive resynthesis."
        ),
    }
    lines.append(strategy_descriptions.get(strategy, ""))
    lines.append("")

    # Results summary
    depth_change = orig.depth - opt.depth
    gate_change  = orig.gate_count - opt.gate_count
    cx_change    = orig.cx_count - opt.cx_count

    if depth_change > 0:
        lines.append(f"- **Circuit depth** reduced by {depth_change} "
                      f"({orig.depth} → {opt.depth})")
    elif depth_change < 0:
        lines.append(f"- ⚠️ **Circuit depth** increased by {abs(depth_change)} "
                      f"({orig.depth} → {opt.depth}) — "
                      "this can happen when resynthesis trades depth for gate count")
    else:
        lines.append(f"- Circuit depth unchanged at {orig.depth}")

    if gate_change > 0:
        lines.append(f"- **Total gates** reduced by {gate_change} "
                      f"({orig.gate_count} → {opt.gate_count})")
    elif gate_change < 0:
        lines.append(f"- Total gates increased by {abs(gate_change)} "
                      f"({orig.gate_count} → {opt.gate_count})")
    else:
        lines.append(f"- Total gates unchanged at {orig.gate_count}")

    if cx_change > 0:
        lines.append(f"- **CX gates** (most expensive) reduced by {cx_change} "
                      f"({orig.cx_count} → {opt.cx_count})")

    return "\n".join(lines)