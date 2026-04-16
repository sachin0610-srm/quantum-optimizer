"""
Quantum Circuit Optimizer — Streamlit App
==========================================
Main entry point.  Run with:
    streamlit run app.py
"""

import sys, os
# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

# ── Page config (must be first Streamlit call) ───────────────────────
st.set_page_config(
    page_title="Quantum Circuit Optimizer",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from ui.styles import inject_custom_css
from ui.sidebar import render_sidebar
from ui.visualizer import (
    render_header,
    render_metrics_row,
    render_comparison,
    render_improvement_charts,
    render_ai_advisor,
    render_noise_results,
    render_hardware_results,
    render_explanation,
    render_metric_card,
    draw_circuit,
)
from core.circuits import get_predefined_circuit, build_custom_circuit
from core.optimizer import optimize_circuit, get_metrics
from core.ai_advisor import analyse_circuit
from core.noise_sim import build_noise_model, compare_noise
from core.hardware import hardware_transpile


def main():
    # Inject premium CSS
    inject_custom_css()

    # Render header
    render_header()

    # Sidebar controls
    cfg = render_sidebar()

    # ── Build circuit ────────────────────────────────────────────────
    circuit = None

    if cfg["circuit_mode"] == "Predefined":
        if cfg["circuit_name"]:
            circuit = get_predefined_circuit(cfg["circuit_name"])
    else:
        if cfg["custom_gates"]:
            circuit = build_custom_circuit(
                cfg["custom_num_qubits"],
                cfg["custom_gates"],
            )
        else:
            st.info("👈 Add gates in the sidebar to build your custom circuit.")
            return

    if circuit is None:
        st.info("👈 Select a circuit from the sidebar to get started.")
        return

    # ── Display original circuit ─────────────────────────────────────
    st.markdown(
        '<div class="section-header"><h3>🔬 Original Circuit</h3></div>',
        unsafe_allow_html=True,
    )

    orig_metrics = get_metrics(circuit)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Qubits", orig_metrics.num_qubits)
    with col2:
        render_metric_card("Depth", orig_metrics.depth)
    with col3:
        render_metric_card("Total Gates", orig_metrics.gate_count)
    with col4:
        render_metric_card("CX Gates", orig_metrics.cx_count)

    with st.expander("🔍 View Original Circuit Diagram", expanded=True):
        draw_circuit(circuit)

    # ── AI Advisor ───────────────────────────────────────────────────
    strategy = cfg["strategy"]

    if cfg["use_ai_advisor"]:
        with st.spinner("🤖 AI Advisor analysing circuit..."):
            recommendation = analyse_circuit(circuit)
        render_ai_advisor(recommendation)
        strategy = recommendation.recommended_strategy

    if strategy is None:
        strategy = "Medium"

    # ── Optimize ─────────────────────────────────────────────────────
    st.markdown("---")

    with st.spinner(f"⚡ Optimizing with **{strategy}** strategy..."):
        result = optimize_circuit(circuit, strategy)

    # Metrics row
    st.markdown(
        '<div class="section-header"><h3>🎯 Optimization Results</h3></div>',
        unsafe_allow_html=True,
    )
    render_metrics_row(result)

    # Overall improvement summary
    avg_improvement = _average_improvement(result)
    imp_col1, imp_col2 = st.columns([1, 3])
    with imp_col1:
        color = "#00E676" if avg_improvement > 0 else "#FFD600"
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Overall Improvement</div>'
            f'<div class="value" style="color:{color}">{avg_improvement:.1f}%</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with imp_col2:
        # Progress bar
        bar_pct = max(0, min(100, avg_improvement))
        st.markdown(
            f'<div style="margin-top:1.2rem">'
            f'<div style="font-size:0.85rem;color:#8B949E;margin-bottom:0.3rem">'
            f'Optimization efficiency</div>'
            f'<div class="improvement-bar">'
            f'<div class="improvement-bar-fill" style="width:{bar_pct}%"></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

    # Side-by-side comparison
    render_comparison(result)

    # Explanation (REASON) — directly below the circuit comparison
    render_explanation(result.explanation)

    # Charts
    render_improvement_charts(result)

    # ── Noise simulation ─────────────────────────────────────────────
    if cfg["enable_noise"]:
        st.markdown("---")
        with st.spinner("🌊 Running noise simulation..."):
            noise_model = build_noise_model(
                error_rate=cfg["noise_params"]["error_rate"],
                t1_us=cfg["noise_params"]["t1"],
                t2_us=cfg["noise_params"]["t2"],
            )
            noise_comparison = compare_noise(
                result.original_circuit,
                result.optimized_circuit,
                noise_model,
            )
        render_noise_results(noise_comparison)

    # ── Hardware-aware transpilation ─────────────────────────────────
    if cfg["hardware_backend"] is not None:
        st.markdown("---")
        with st.spinner("🖥️ Transpiling for target hardware..."):
            try:
                hw_result = hardware_transpile(
                    result.optimized_circuit,
                    cfg["hardware_backend"],
                    cfg["hardware_opt_level"],
                )
                render_hardware_results(hw_result)
            except ValueError as e:
                st.error(f"❌ {e}")


def _average_improvement(result) -> float:
    """Compute average improvement across all metrics."""
    imp = result.improvements
    pcts = [v["improvement_pct"] for v in imp.values()]
    return sum(pcts) / len(pcts) if pcts else 0.0


if __name__ == "__main__":
    main()
