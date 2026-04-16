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
    """Generate a detailed, educational explanation of what the optimization did."""

    sections = []

    # ── Section 1: Strategy Overview ─────────────────────────────────
    sections.append(f"### 🎯 Optimization Strategy: **{strategy}**\n")

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
    sections.append(strategy_descriptions.get(strategy, ""))

    # ── Section 2: Qiskit Transpiler Passes Applied ──────────────────
    sections.append("\n### 🔧 Transpiler Passes Applied\n")

    pass_details = {
        "Light": [
            ("**Optimize1qGatesDecomposition**", "Merges consecutive single-qubit "
             "gates (e.g., Rz·Ry·Rz) into a single U gate. "
             "Mathematically, any sequence of single-qubit rotations can be "
             "composed into one unitary: U = Rz(γ)·Ry(β)·Rz(α)."),
            ("**CommutativeCancellation**", "Identifies gates that commute "
             "(AB = BA) and reorders them to expose cancellation pairs. "
             "For example, two adjacent CX gates on the same qubits cancel: "
             "CX · CX = I (identity)."),
        ],
        "Medium": [
            ("**Optimize1qGatesDecomposition**", "Merges consecutive single-qubit "
             "gates into a single U gate using Euler decomposition."),
            ("**CommutativeCancellation**", "Reorders commuting gates to reveal "
             "cancellation opportunities (e.g., CX·CX = I)."),
            ("**RemoveDiagonalGatesBeforeMeasure**", "Removes Z, S, T, Rz gates "
             "that appear immediately before a measurement. These gates only "
             "change the global/relative phase, which is destroyed by the "
             "projective measurement — so they have no observable effect."),
            ("**RemoveResetInZeroState**", "Removes reset operations on qubits "
             "that are already in the |0⟩ state at the start of the circuit, "
             "since resetting |0⟩ to |0⟩ is a no-op."),
        ],
        "Heavy": [
            ("**Optimize1qGatesDecomposition**", "Euler decomposition of single-qubit gate chains."),
            ("**CommutativeCancellation**", "Reorder + cancel commuting gate pairs."),
            ("**RemoveDiagonalGatesBeforeMeasure**", "Strip phase-only gates before measurements."),
            ("**RemoveResetInZeroState**", "Remove redundant resets on |0⟩ qubits."),
            ("**Collect2qBlocks**", "Scans the circuit DAG to identify maximal "
             "blocks of consecutive 2-qubit gates that act on the same pair of qubits."),
            ("**ConsolidateBlocks**", "Takes each 2-qubit block, computes its "
             "total 4×4 unitary matrix, and re-synthesizes it using the KAK "
             "decomposition — which guarantees at most 3 CX gates for any "
             "2-qubit unitary. This is the most powerful pass and can "
             "dramatically reduce CX count."),
        ],
        "Full": [
            ("**All of the above** + Qiskit Level-3 passes", "Includes "
             "layout-aware qubit mapping, SWAP routing, gate direction "
             "correction, and aggressive unitary resynthesis across the "
             "entire circuit."),
        ],
    }

    for pass_name, desc in pass_details.get(strategy, []):
        sections.append(f"- {pass_name}: {desc}")

    # ── Section 3: Results Summary ───────────────────────────────────
    sections.append("\n### 📊 What Changed\n")

    depth_change = orig.depth - opt.depth
    gate_change  = orig.gate_count - opt.gate_count
    cx_change    = orig.cx_count - opt.cx_count
    sq_change    = orig.single_qubit_gates - opt.single_qubit_gates
    tq_change    = orig.two_qubit_gates - opt.two_qubit_gates

    if depth_change > 0:
        sections.append(f"- **Circuit depth** reduced by {depth_change} "
                        f"({orig.depth} → {opt.depth})")
    elif depth_change < 0:
        sections.append(f"- ⚠️ **Circuit depth** increased by {abs(depth_change)} "
                        f"({orig.depth} → {opt.depth}) — "
                        "this can happen when resynthesis trades depth for gate count")
    else:
        sections.append(f"- Circuit depth unchanged at {orig.depth}")

    if gate_change > 0:
        sections.append(f"- **Total gates** reduced by {gate_change} "
                        f"({orig.gate_count} → {opt.gate_count})")
    elif gate_change < 0:
        sections.append(f"- Total gates increased by {abs(gate_change)} "
                        f"({orig.gate_count} → {opt.gate_count})")
    else:
        sections.append(f"- Total gates unchanged at {orig.gate_count}")

    if cx_change > 0:
        sections.append(f"- **CX gates** (most expensive) reduced by {cx_change} "
                        f"({orig.cx_count} → {opt.cx_count})")
    elif cx_change == 0 and orig.cx_count > 0:
        sections.append(f"- CX gates unchanged at {orig.cx_count}")

    if sq_change > 0:
        sections.append(f"- **Single-qubit gates** reduced by {sq_change} "
                        f"({orig.single_qubit_gates} → {opt.single_qubit_gates})")
    if tq_change > 0:
        sections.append(f"- **Two-qubit gates** reduced by {tq_change} "
                        f"({orig.two_qubit_gates} → {opt.two_qubit_gates})")

    # ── Section 4: Gate-by-gate diff ─────────────────────────────────
    gate_diff = _gate_level_diff(orig.operations, opt.operations)
    if gate_diff:
        sections.append("\n### 🔬 Gate-by-Gate Breakdown\n")
        sections.append("| Gate | Original | Optimized | Change |")
        sections.append("|------|----------|-----------|--------|")
        for row in gate_diff:
            sections.append(row)

    # ── Section 5: Educational Notes ─────────────────────────────────
    sections.append("\n### 🎓 Why This Works (Educational Notes)\n")

    edu_notes = []

    if sq_change > 0:
        edu_notes.append(
            "**Single-Qubit Merging:** Any sequence of single-qubit gates on the same qubit "
            "can be combined into one gate. This is because single-qubit gates are 2×2 unitary "
            "matrices, and the product of unitaries is still unitary. For example, "
            "Rz(θ₁)·Ry(θ₂)·Rz(θ₃) can be represented as a single U(θ,φ,λ) gate with "
            "equivalent action — this is the ZYZ Euler decomposition."
        )

    if cx_change > 0:
        edu_notes.append(
            "**CX Cancellation:** Two consecutive CNOT (CX) gates on the same control-target "
            "pair cancel perfectly: CX · CX = I. This is because CX is its own inverse "
            "(it is a self-inverse or involutory gate). The optimizer detects these patterns "
            "even when other commuting gates are interleaved between them."
        )

    if strategy in ("Medium", "Heavy", "Full"):
        edu_notes.append(
            "**Diagonal Gate Removal:** Gates like Z, S, T, and Rz are diagonal in the "
            "computational basis — they only add phase to |1⟩ and leave |0⟩ unchanged. "
            "Since measurement in the computational basis only distinguishes |0⟩ from |1⟩ "
            "(discarding phase information), any diagonal gate right before measurement "
            "has zero effect on the measurement outcome and can be safely removed."
        )

    if strategy in ("Heavy", "Full"):
        edu_notes.append(
            "**KAK Decomposition (Block Consolidation):** Any 2-qubit unitary (a 4×4 matrix) "
            "can be decomposed into at most 3 CNOT gates plus single-qubit rotations. "
            "This is the Cartan/KAK decomposition. When the optimizer finds a long sequence "
            "of interleaved CX and single-qubit gates on two qubits, it multiplies all the "
            "matrices together into one 4×4 unitary, then re-synthesizes it — often using "
            "fewer CX gates than the original."
        )

    if not edu_notes:
        edu_notes.append(
            "The circuit was already fairly optimal. The optimizer verified that no "
            "significant simplifications were possible with the selected strategy."
        )

    for note in edu_notes:
        sections.append(f"- {note}\n")

    return "\n".join(sections)


def _gate_level_diff(orig_ops: dict, opt_ops: dict) -> list[str]:
    """Produce a markdown table of per-gate changes, excluding barriers/measures."""
    all_gates = sorted(set(orig_ops) | set(opt_ops))
    rows = []
    for gate in all_gates:
        if gate in ("barrier", "measure"):
            continue
        o = orig_ops.get(gate, 0)
        n = opt_ops.get(gate, 0)
        diff = o - n
        if diff > 0:
            change = f"🟢 −{diff}"
        elif diff < 0:
            change = f"🔴 +{abs(diff)}"
        else:
            change = "—"
        rows.append(f"| `{gate}` | {o} | {n} | {change} |")
    return rows