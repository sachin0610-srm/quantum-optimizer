"""
AI Advisor — heuristic scoring engine that analyses circuit properties
and recommends the best optimization strategy.
"""

from __future__ import annotations
from dataclasses import dataclass
from qiskit import QuantumCircuit
from core.optimizer import CircuitMetrics


@dataclass
class AdvisorRecommendation:
    """Output of the AI advisor."""
    complexity_score: float          # 0-100
    recommended_strategy: str        # Light / Medium / Heavy / Full
    confidence: float                # 0-1
    reasoning: str                   # Natural-language explanation
    circuit_profile: dict            # Key properties used in scoring


def analyse_circuit(qc: QuantumCircuit) -> AdvisorRecommendation:
    """
    Analyse a circuit and recommend an optimization strategy.

    Heuristic factors:
      1. Gate density       — gates / qubits
      2. CX ratio           — 2-qubit gates / total gates
      3. Depth-to-width     — depth / num_qubits
      4. Redundancy score   — estimated cancellable gates
      5. Gate variety        — number of distinct gate types
    """
    metrics = CircuitMetrics.from_circuit(qc)

    # ── Compute heuristic features ───────────────────────────────────
    num_q = max(metrics.num_qubits, 1)
    total = max(metrics.gate_count, 1)

    gate_density   = metrics.gate_count / num_q
    cx_ratio       = metrics.two_qubit_gates / total
    depth_to_width = metrics.depth / num_q
    gate_variety   = len([k for k in metrics.operations
                         if k not in ("barrier", "measure")])
    redundancy     = _estimate_redundancy(qc)

    profile = {
        "gate_density":   round(gate_density, 2),
        "cx_ratio":       round(cx_ratio, 3),
        "depth_to_width": round(depth_to_width, 2),
        "gate_variety":   gate_variety,
        "redundancy_est": round(redundancy, 3),
    }

    # ── Compute complexity score (0-100) ─────────────────────────────
    score = (
        min(gate_density * 4, 30)
        + min(cx_ratio * 40, 25)
        + min(depth_to_width * 3, 20)
        + min(gate_variety * 2, 10)
        + min(redundancy * 30, 15)
    )
    score = round(min(max(score, 0), 100), 1)

    # ── Decision logic ───────────────────────────────────────────────
    strategy, confidence, reasoning = _decide_strategy(
        score, profile, metrics
    )

    return AdvisorRecommendation(
        complexity_score=score,
        recommended_strategy=strategy,
        confidence=confidence,
        reasoning=reasoning,
        circuit_profile=profile,
    )


def _estimate_redundancy(qc: QuantumCircuit) -> float:
    """
    Quick scan for obvious redundancies:
    – adjacent identical self-inverse gates (X-X, H-H, CX-CX)
    """
    self_inverse = {"x", "y", "z", "h", "cx", "cz", "swap", "ccx"}
    data = qc.data
    cancel_count = 0
    prev = None
    for inst in data:
        name = inst.operation.name
        qubits = tuple(qc.find_bit(q).index for q in inst.qubits)
        current = (name, qubits)
        if prev and current == prev and name in self_inverse:
            cancel_count += 1
            prev = None          # don't triple-count
        else:
            prev = current
    total = max(len(data), 1)
    return cancel_count / total


def _decide_strategy(
    score: float,
    profile: dict,
    metrics: CircuitMetrics,
) -> tuple[str, float, str]:
    """Rule-based decision tree for strategy recommendation."""

    reasons = []

    # Very simple circuits
    if score < 20:
        reasons.append(
            "This circuit has **low complexity** (score {:.0f}/100). "
            "Gate density and CX ratio are both modest. "
            "A **Light** pass (single-qubit optimization + CX cancellation) "
            "should be sufficient.".format(score)
        )
        return "Light", 0.90, "\n\n".join(reasons)

    # Moderate
    if score < 45:
        reasons.append(
            "The circuit has **moderate complexity** (score {:.0f}/100). "
            "There are commutative gate structures that can be reordered for "
            "additional cancellations.".format(score)
        )
        if profile["redundancy_est"] > 0.05:
            reasons.append(
                "Detected ~{:.0%} potential redundant gate pairs — "
                "commutative cancellation will help.".format(
                    profile["redundancy_est"]
                )
            )
        return "Medium", 0.82, "\n\n".join(reasons)

    # High
    if score < 70:
        reasons.append(
            "This circuit is **fairly complex** (score {:.0f}/100) with a "
            "significant two-qubit gate ratio ({:.1%}). Block consolidation "
            "and resynthesis will yield meaningful depth reduction.".format(
                score, profile["cx_ratio"]
            )
        )
        if profile["depth_to_width"] > 5:
            reasons.append(
                "The depth-to-width ratio ({:.1f}) is high, indicating "
                "long gate chains that block consolidation can compress.".format(
                    profile["depth_to_width"]
                )
            )
        return "Heavy", 0.78, "\n\n".join(reasons)

    # Very high
    reasons.append(
        "This circuit is **highly complex** (score {:.0f}/100) with dense "
        "gate structure and significant entanglement. Recommend the **Full** "
        "Qiskit optimization pipeline (level 3) for maximum reduction.".format(
            score
        )
    )
    if metrics.gate_count > 30:
        reasons.append(
            "With {} total gates, the aggressive resynthesis passes "
            "in Full mode can often find dramatically better decompositions.".format(
                metrics.gate_count
            )
        )
    return "Full", 0.75, "\n\n".join(reasons)
