"""
Visualization components for the Quantum Circuit Optimizer.
"""

from __future__ import annotations
import io
import base64
import streamlit as st
import plotly.graph_objects as go
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from qiskit import QuantumCircuit
from core.optimizer import OptimizationResult, CircuitMetrics
from core.ai_advisor import AdvisorRecommendation
from core.noise_sim import NoiseComparison
from core.hardware import HardwareResult


# ── Header ───────────────────────────────────────────────────────────

def render_header():
    st.markdown(
        """
        <div class="app-header">
            <h1>⚛️ Quantum Circuit Optimizer</h1>
            <p>Advanced circuit optimization with AI-powered strategy selection, noise simulation &amp; hardware-aware transpilation</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── Circuit diagram ─────────────────────────────────────────────────

def draw_circuit(qc: QuantumCircuit, title: str = "") -> None:
    """Render a circuit diagram using matplotlib."""
    fig, ax = plt.subplots(figsize=(max(12, qc.depth() * 0.8), max(3, qc.num_qubits * 0.6)))
    try:
        qc.draw(output="mpl", ax=ax, style={"backgroundcolor": "#161B22",
                                              "textcolor": "#FAFAFA",
                                              "linecolor": "#8B949E",
                                              "gatefacecolor": "#6C63FF",
                                              "gatetextcolor": "#FAFAFA",
                                              "barrierfacecolor": "#30363D"})
    except Exception:
        qc.draw(output="mpl", ax=ax)
    ax.set_facecolor("#161B22")
    fig.patch.set_facecolor("#161B22")
    if title:
        ax.set_title(title, color="#FAFAFA", fontsize=12, fontweight="bold", pad=10)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ── Metric cards ─────────────────────────────────────────────────────

def render_metric_card(label: str, value, delta=None, delta_suffix="%"):
    """Render a single glassmorphism metric card."""
    delta_html = ""
    if delta is not None:
        if delta > 0:
            delta_class = "delta-positive"
            delta_text = f"▼ {abs(delta)}{delta_suffix} reduction"
        elif delta < 0:
            delta_class = "delta-negative"
            delta_text = f"▲ {abs(delta)}{delta_suffix} increase"
        else:
            delta_class = "delta-neutral"
            delta_text = "— no change"
        delta_html = f'<div class="delta {delta_class}">{delta_text}</div>'

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metrics_row(result: OptimizationResult):
    """Render a row of metric cards for an optimization result."""
    imp = result.improvements
    cols = st.columns(5)
    items = [
        ("Circuit Depth",      imp["depth"]["optimized"],            imp["depth"]["improvement_pct"]),
        ("Total Gates",        imp["gate_count"]["optimized"],       imp["gate_count"]["improvement_pct"]),
        ("CX Gates",           imp["cx_count"]["optimized"],         imp["cx_count"]["improvement_pct"]),
        ("1-Q Gates",          imp["single_qubit_gates"]["optimized"],imp["single_qubit_gates"]["improvement_pct"]),
        ("2-Q Gates",          imp["two_qubit_gates"]["optimized"],  imp["two_qubit_gates"]["improvement_pct"]),
    ]
    for col, (label, val, delta) in zip(cols, items):
        with col:
            render_metric_card(label, val, delta)


# ── Comparison view ──────────────────────────────────────────────────

def render_comparison(result: OptimizationResult):
    """Side-by-side circuit comparison."""
    st.markdown(
        '<div class="section-header"><h3>📊 Circuit Comparison</h3></div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            '<div class="compare-panel">'
            '<span class="compare-label label-original">ORIGINAL</span>',
            unsafe_allow_html=True,
        )
        draw_circuit(result.original_circuit)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown(
            '<div class="compare-panel">'
            '<span class="compare-label label-optimized">OPTIMIZED</span>',
            unsafe_allow_html=True,
        )
        draw_circuit(result.optimized_circuit)
        st.markdown('</div>', unsafe_allow_html=True)


# ── Improvement charts ───────────────────────────────────────────────

def render_improvement_charts(result: OptimizationResult):
    """Plotly charts comparing before/after metrics."""
    st.markdown(
        '<div class="section-header"><h3>📈 Improvement Analysis</h3></div>',
        unsafe_allow_html=True,
    )

    tab1, tab2 = st.tabs(["📊 Bar Chart", "🕸️ Radar Chart"])

    with tab1:
        _bar_chart(result)

    with tab2:
        _radar_chart(result)


def _bar_chart(result: OptimizationResult):
    imp = result.improvements
    categories = ["Depth", "Total Gates", "CX Gates", "1-Q Gates", "2-Q Gates"]
    keys = ["depth", "gate_count", "cx_count", "single_qubit_gates", "two_qubit_gates"]

    orig_vals = [imp[k]["original"]  for k in keys]
    opt_vals  = [imp[k]["optimized"] for k in keys]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Original",
        x=categories,
        y=orig_vals,
        marker_color="#FF6B6B",
        marker_line=dict(color="#FF6B6B", width=1),
        opacity=0.85,
    ))
    fig.add_trace(go.Bar(
        name="Optimized",
        x=categories,
        y=opt_vals,
        marker_color="#00E676",
        marker_line=dict(color="#00E676", width=1),
        opacity=0.85,
    ))
    fig.update_layout(
        barmode="group",
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#161B22",
        font=dict(family="Inter", color="#FAFAFA"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(t=30, b=40, l=40, r=20),
        height=350,
    )
    st.plotly_chart(fig, use_container_width=True)


def _radar_chart(result: OptimizationResult):
    imp = result.improvements
    categories = ["Depth", "Gates", "CX", "1-Q", "2-Q"]
    keys = ["depth", "gate_count", "cx_count", "single_qubit_gates", "two_qubit_gates"]

    # Normalise to 0-1 range (original = 1.0)
    orig_norm = [1.0] * 5
    opt_norm = []
    for k in keys:
        o = imp[k]["original"]
        n = imp[k]["optimized"]
        opt_norm.append(n / o if o > 0 else 1.0)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=orig_norm + [orig_norm[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name="Original",
        line_color="#FF6B6B",
        fillcolor="rgba(255,107,107,0.15)",
    ))
    fig.add_trace(go.Scatterpolar(
        r=opt_norm + [opt_norm[0]],
        theta=categories + [categories[0]],
        fill="toself",
        name="Optimized",
        line_color="#00E676",
        fillcolor="rgba(0,230,118,0.15)",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#161B22",
            radialaxis=dict(visible=True, range=[0, 1.2], gridcolor="#30363D"),
            angularaxis=dict(gridcolor="#30363D"),
        ),
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        font=dict(family="Inter", color="#FAFAFA"),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
        margin=dict(t=40, b=40, l=60, r=60),
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── AI Advisor card ──────────────────────────────────────────────────

def render_ai_advisor(rec: AdvisorRecommendation):
    """Render the AI advisor recommendation."""
    st.markdown(
        '<div class="section-header"><h3>🤖 AI Advisor Recommendation</h3></div>',
        unsafe_allow_html=True,
    )

    # Score badge
    score = rec.complexity_score
    if score < 30:
        score_class = "score-low"
        score_label = "Low Complexity"
    elif score < 65:
        score_class = "score-medium"
        score_label = "Moderate Complexity"
    else:
        score_class = "score-high"
        score_label = "High Complexity"

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown(
            f'<div class="score-badge {score_class}">{score:.0f} <span style="font-size:0.7em;font-weight:400">/100</span></div>'
            f'<div style="margin-top:0.3rem;font-size:0.8rem;color:#8B949E">{score_label}</div>',
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Recommended Strategy</div>'
            f'<div class="value" style="font-size:1.4rem">{rec.recommended_strategy}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="label">Confidence</div>'
            f'<div class="value" style="font-size:1.4rem">{rec.confidence:.0%}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # Reasoning
    st.markdown(
        f'<div class="info-card"><h4>💡 Reasoning</h4>{rec.reasoning}</div>',
        unsafe_allow_html=True,
    )

    # Circuit profile
    with st.expander("📋 Circuit Profile Details"):
        profile_cols = st.columns(len(rec.circuit_profile))
        for col, (key, val) in zip(profile_cols, rec.circuit_profile.items()):
            with col:
                nice_key = key.replace("_", " ").title()
                st.metric(nice_key, val)


# ── Noise simulation results ────────────────────────────────────────

def render_noise_results(comparison: NoiseComparison):
    """Render noise simulation comparison."""
    st.markdown(
        '<div class="section-header"><h3>🌊 Noise Simulation Results</h3></div>',
        unsafe_allow_html=True,
    )

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card(
            "Original Success Prob",
            f"{comparison.original.success_probability:.1%}",
        )
    with col2:
        render_metric_card(
            "Optimized Success Prob",
            f"{comparison.optimized.success_probability:.1%}",
        )
    with col3:
        delta = comparison.fidelity_improvement
        color = "#00E676" if delta >= 0 else "#FF6B6B"
        render_metric_card(
            "Fidelity Improvement",
            f"{delta:+.2%}",
        )

    # Histogram comparison
    tab1, tab2 = st.tabs(["📊 Original Counts", "📊 Optimized Counts"])

    with tab1:
        _counts_histogram(comparison.original.counts, "Original Circuit (Noisy)", "#FF6B6B")

    with tab2:
        _counts_histogram(comparison.optimized.counts, "Optimized Circuit (Noisy)", "#00E676")


def _counts_histogram(counts: dict, title: str, color: str):
    """Plot a histogram of measurement counts."""
    sorted_items = sorted(counts.items(), key=lambda x: -x[1])[:20]
    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]

    fig = go.Figure(go.Bar(
        x=labels,
        y=values,
        marker_color=color,
        opacity=0.85,
    ))
    fig.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="#0E1117",
        plot_bgcolor="#161B22",
        font=dict(family="Inter", color="#FAFAFA"),
        xaxis_title="Measurement Outcome",
        yaxis_title="Counts",
        margin=dict(t=50, b=50, l=50, r=20),
        height=300,
    )
    st.plotly_chart(fig, use_container_width=True)


# ── Hardware results ─────────────────────────────────────────────────

def render_hardware_results(hw_result: HardwareResult):
    """Render hardware-aware transpilation results."""
    st.markdown(
        '<div class="section-header"><h3>🖥️ Hardware-Aware Transpilation</h3></div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Device", hw_result.backend_name.split("Generic ")[-1])
    with col2:
        render_metric_card("Transpiled Depth", hw_result.depth)
    with col3:
        render_metric_card("Total Gates", hw_result.gate_count)
    with col4:
        render_metric_card("SWAP Gates", hw_result.swap_count)

    st.markdown(
        f'<div class="info-card"><h4>🔀 Routing Analysis</h4>{hw_result.routing_overhead}</div>',
        unsafe_allow_html=True,
    )

    with st.expander("🔍 View Transpiled Circuit"):
        draw_circuit(hw_result.transpiled_circuit, "Hardware-Transpiled Circuit")

    with st.expander("📋 Basis Gates"):
        st.code(", ".join(hw_result.basis_gates))


# ── Explanation panel ────────────────────────────────────────────────

def render_explanation(explanation: str):
    """Render the optimization explanation with premium educational UI."""
    st.markdown(
        '<div class="section-header"><h3>📖 Optimization Reasoning</h3></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:0.9rem;color:#8B949E;margin-bottom:1rem;">'
        'Detailed breakdown of what was optimized, which transpiler passes were used, '
        'and the mathematical principles behind each transformation.'
        '</div>',
        unsafe_allow_html=True,
    )

    # Use Streamlit's native markdown rendering for proper formatting
    st.markdown(explanation)

