"""
Sidebar controls for the Quantum Circuit Optimizer.
"""

import streamlit as st
import numpy as np
from config import (
    PREDEFINED_CIRCUITS,
    OPTIMIZATION_STRATEGIES,
    HARDWARE_BACKENDS,
    SINGLE_QUBIT_GATES,
    TWO_QUBIT_GATES,
    THREE_QUBIT_GATES,
)


def render_sidebar() -> dict:
    """
    Render the sidebar and return a dict with all user selections.

    Returns dict with keys:
        circuit_mode, circuit_name, custom_num_qubits, custom_gates,
        strategy, use_ai_advisor, enable_noise, noise_params,
        hardware_backend, hardware_opt_level
    """
    with st.sidebar:
        st.markdown("## ⚛️ Circuit")
        circuit_mode = st.radio(
            "Circuit source",
            ["Predefined", "Custom Builder"],
            horizontal=True,
            label_visibility="collapsed",
        )

        circuit_name = None
        custom_num_qubits = 3
        custom_gates = []

        if circuit_mode == "Predefined":
            circuit_name = st.selectbox(
                "Select circuit",
                PREDEFINED_CIRCUITS,
                index=0,
            )
        else:
            custom_num_qubits = st.slider(
                "Number of qubits", 2, 10, 3
            )
            custom_gates = _custom_gate_builder(custom_num_qubits)

        st.markdown("---")

        # ── Optimization strategy ────────────────────────────────────
        st.markdown("## 🔧 Optimization")
        use_ai = st.toggle("🤖 AI Advisor (auto-select)", value=False)

        strategy = None
        if not use_ai:
            strategy = st.selectbox(
                "Strategy",
                list(OPTIMIZATION_STRATEGIES.keys()),
                index=1,
                help="Choose optimization aggressiveness",
            )
            st.caption(f"_{OPTIMIZATION_STRATEGIES[strategy]}_")

        st.markdown("---")

        # ── Noise simulation ─────────────────────────────────────────
        st.markdown("## 🌊 Noise Simulation")
        enable_noise = st.toggle("Enable noise model", value=False)

        noise_params = {}
        if enable_noise:
            noise_params["error_rate"] = st.slider(
                "Depolarizing error rate",
                0.001, 0.1, 0.01, 0.001,
                format="%.3f",
            )
            noise_params["t1"] = st.slider(
                "T₁ relaxation (µs)", 10.0, 200.0, 50.0, 5.0
            )
            noise_params["t2"] = st.slider(
                "T₂ dephasing (µs)", 10.0, 200.0, 70.0, 5.0
            )

        st.markdown("---")

        # ── Hardware backend ─────────────────────────────────────────
        st.markdown("## 🖥️ Hardware Target")
        hw_name = st.selectbox(
            "Target device",
            list(HARDWARE_BACKENDS.keys()),
            index=0,
        )
        hw_qubits = HARDWARE_BACKENDS[hw_name]

        hw_opt_level = 2
        if hw_qubits is not None:
            hw_opt_level = st.slider(
                "Transpiler opt level", 0, 3, 2,
                help="Higher = more aggressive gate reduction",
            )

        st.markdown("---")
        st.markdown(
            "<div style='text-align:center;color:#8B949E;font-size:0.75rem;'>"
            "Built with Qiskit + Streamlit<br>"
            "Quantum Circuit Optimizer v2.0"
            "</div>",
            unsafe_allow_html=True,
        )

    return {
        "circuit_mode":       circuit_mode,
        "circuit_name":       circuit_name,
        "custom_num_qubits":  custom_num_qubits,
        "custom_gates":       custom_gates,
        "strategy":           strategy,
        "use_ai_advisor":     use_ai,
        "enable_noise":       enable_noise,
        "noise_params":       noise_params,
        "hardware_backend":   hw_qubits,
        "hardware_opt_level": hw_opt_level,
    }


def _custom_gate_builder(num_qubits: int) -> list[dict]:
    """Interactive gate-by-gate circuit builder."""
    if "custom_gates" not in st.session_state:
        st.session_state.custom_gates = []

    all_gates = SINGLE_QUBIT_GATES + TWO_QUBIT_GATES + THREE_QUBIT_GATES

    with st.expander("➕ Add Gates", expanded=True):
        gate = st.selectbox("Gate", all_gates, key="gate_select")

        qubit_indices = list(range(num_qubits))
        qubits_needed = 1
        if gate in TWO_QUBIT_GATES:
            qubits_needed = 2
        elif gate in THREE_QUBIT_GATES:
            qubits_needed = 3

        selected_qubits = []
        cols = st.columns(qubits_needed)
        for i in range(qubits_needed):
            with cols[i]:
                q = st.selectbox(
                    f"Qubit {i}",
                    qubit_indices,
                    index=min(i, len(qubit_indices) - 1),
                    key=f"qubit_{i}",
                )
                selected_qubits.append(q)

        param = 0.0
        if gate in ("Rx", "Ry", "Rz"):
            param = st.slider(
                "Angle (radians)",
                0.0, float(2 * np.pi), float(np.pi / 2),
                0.01,
                key="gate_param",
            )

        if st.button("Add Gate", use_container_width=True, type="primary"):
            st.session_state.custom_gates.append({
                "gate": gate,
                "qubits": selected_qubits,
                "param": param,
            })
            st.rerun()

    # Show current gates
    if st.session_state.custom_gates:
        st.markdown("**Current gates:**")
        for i, g in enumerate(st.session_state.custom_gates):
            q_str = ", ".join(f"q{q}" for q in g["qubits"])
            label = f"{g['gate']}({q_str})"
            if g.get("param") and g["gate"] in ("Rx", "Ry", "Rz"):
                label += f" θ={g['param']:.2f}"
            st.text(f"  {i+1}. {label}")

        if st.button("🗑️ Clear all", use_container_width=True):
            st.session_state.custom_gates = []
            st.rerun()

    return st.session_state.custom_gates
