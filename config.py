"""
Global configuration for the Quantum Circuit Optimizer.
"""

# ── Available predefined circuits ────────────────────────────────────
PREDEFINED_CIRCUITS = [
    "GHZ State (3-qubit)",
    "GHZ State (5-qubit)",
    "Quantum Fourier Transform (4-qubit)",
    "Grover's Search (3-qubit)",
    "Bernstein-Vazirani (4-qubit)",
    "VQE Ansatz (4-qubit)",
    "Random Circuit (4-qubit)",
    "Quantum Teleportation (3-qubit)",
]

# ── Optimization strategies ──────────────────────────────────────────
OPTIMIZATION_STRATEGIES = {
    "Light":  "Basic single-qubit gate optimization and CX cancellation",
    "Medium": "Adds commutative cancellation and diagonal gate removal",
    "Heavy":  "Adds block consolidation and unitary synthesis",
    "Full":   "Qiskit optimization_level=3 with all available passes",
}

# ── Hardware backends ────────────────────────────────────────────────
HARDWARE_BACKENDS = {
    "None (Ideal)":   None,
    "5-Qubit Device":  5,
    "7-Qubit Device":  7,
    "20-Qubit Device": 20,
    "27-Qubit Device": 27,
}

# ── Supported gates for custom circuit builder ───────────────────────
SINGLE_QUBIT_GATES = ["H", "X", "Y", "Z", "S", "T", "Rx", "Ry", "Rz"]
TWO_QUBIT_GATES    = ["CX", "CZ", "SWAP"]
THREE_QUBIT_GATES  = ["CCX (Toffoli)", "CSWAP (Fredkin)"]

# ── Color palette ────────────────────────────────────────────────────
COLORS = {
    "primary":      "#6C63FF",
    "secondary":    "#00D2FF",
    "accent":       "#FF6B6B",
    "success":      "#00E676",
    "warning":      "#FFD600",
    "bg_dark":      "#0E1117",
    "bg_card":      "#1A1D24",
    "text_primary": "#FAFAFA",
    "text_muted":   "#8B949E",
    "border":       "#30363D",
    "gradient_1":   "#6C63FF",
    "gradient_2":   "#00D2FF",
}
