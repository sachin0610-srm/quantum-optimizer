# ⚛️ Quantum Circuit Optimizer v2

**An advanced interactive web application for optimizing quantum circuits with AI-powered strategy selection, noise simulation, and hardware-aware transpilation.**

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.11%2B-brightgreen)
![Qiskit](https://img.shields.io/badge/qiskit-1.0%2B-orange)
![Streamlit](https://img.shields.io/badge/streamlit-1.30%2B-red)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 Overview

The **Quantum Circuit Optimizer** is an educational tool designed for students, professors, and quantum computing enthusiasts. It provides:

- **🔧 Circuit Optimization** - 4 optimization strategies (Light → Full) using Qiskit transpiler passes
- **🤖 AI Advisor** - Automatically recommends best optimization strategy based on circuit complexity
- **📊 Detailed Reasoning** - Complete educational breakdown of what was optimized and why
- **🌊 Noise Simulation** - Test circuits under realistic error models (depolarizing + thermal relaxation)
- **🖥️ Hardware-Aware Transpilation** - Adapt circuits to specific device topologies
- **📈 Rich Visualizations** - Circuit diagrams, comparison charts, and metrics

---

## ✨ What's New in v2

### Enhanced Explanation/Reasoning System
Users now get **complete educational insights** into circuit optimizations:

1. **🎯 Optimization Strategy Overview** - What the strategy does
2. **🔧 Transpiler Passes Applied** - Each pass with technical details
3. **📊 What Changed** - Exact metric improvements (depth, gates, CX, etc.)
4. **🔬 Gate-by-Gate Breakdown** - Table showing each gate type's changes
5. **🎓 Why This Works** - Mathematical principles and educational notes

Perfect for **professors and students** to understand quantum optimization concepts!

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/sachin0610-srm/quantum-optimizer.git
cd quantum-optimizer

# Install dependencies
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

---

## 📋 Requirements

```
qiskit>=1.0
qiskit-aer
streamlit>=1.30
matplotlib
numpy
plotly
pylatexenc
```

---

## 💡 How to Use

### 1. Select or Build a Circuit
- **Predefined Circuits**: GHZ State, Quantum Fourier Transform, Grover's Search, Bernstein-Vazirani, VQE Ansatz, Random Circuit, Quantum Teleportation
- **Custom Builder**: Add gates interactively with parameters

### 2. Choose Optimization Strategy (or use AI Advisor)
- **Light**: Single-qubit optimization + CX cancellation
- **Medium**: + Commutative cancellation + Diagonal gate removal
- **Heavy**: + Block consolidation & KAK decomposition
- **Full**: Qiskit level-3 optimization (most aggressive)

### 3. View Results
- **Original Circuit Metrics** - Depth, gate count, CX gates, etc.
- **Optimized Circuit Metrics** - Side-by-side comparison
- **📖 Optimization Reasoning** - Detailed explanation of what was optimized
- **📈 Charts** - Bar and radar charts showing improvements

### 4. Optional: Test Noise Resilience
- Configure depolarizing error rate, T1, T2 parameters
- Simulate both circuits under noise
- Compare fidelity improvements

### 5. Optional: Hardware-Aware Transpilation
- Select target device (5/7/20/27-qubit)
- Transpile for device topology
- See routing analysis and SWAP overhead

---

## 🏗️ Project Structure

```
quantum-optimizer/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration (circuits, strategies, colors)
├── requirements.txt          # Python dependencies
│
├── core/                     # Core optimization engine
│   ├── circuits.py          # Predefined & custom circuit builders
│   ├── optimizer.py         # Optimization strategies & metrics
│   ├── ai_advisor.py        # AI-powered strategy recommendation
│   ├── noise_sim.py         # Noise model simulation
│   └── hardware.py          # Hardware-aware transpilation
│
├── ui/                      # Streamlit UI components
│   ├── styles.py           # Custom dark theme CSS
│   ├── sidebar.py          # Sidebar controls
│   └── visualizer.py       # Visualization components
│
└── .devcontainer/          # Docker dev environment
```

---

## 🧠 Educational Features

### For Students
- Learn quantum gate operations and circuit structure
- Understand optimization techniques (gate cancellation, block consolidation, KAK decomposition)
- See real circuit optimizations with detailed explanations
- Explore different optimization strategies

### For Professors
- Demonstrate quantum optimization concepts in class
- Show students exactly how circuits are optimized
- Explain mathematical principles behind each transformation
- Use as an interactive teaching tool

### Example: What Students See

```
📖 Optimization Reasoning

🎯 Optimization Strategy: Medium
Built on Light optimizations, adding commutative gate cancellation 
and removal of diagonal gates before measurement...

🔧 Transpiler Passes Applied
- Optimize1qGatesDecomposition: Merges consecutive single-qubit gates...
- CommutativeCancellation: Reorders commuting gates to reveal cancellations...
- RemoveDiagonalGatesBeforeMeasure: Removes phase-only gates...

📊 What Changed
- Circuit depth reduced by 4 (16 → 12)
- Total gates reduced by 8 (32 → 24)
- CX gates reduced by 2 (10 → 8)

🔬 Gate-by-Gate Breakdown
| Gate | Original | Optimized | Change  |
|------|----------|-----------|---------|
| cx   | 10       | 8         | 🟢 −2   |
| h    | 8        | 8         | —       |

🎓 Why This Works (Educational Notes)
- Single-Qubit Merging: Unitary matrix composition...
- CX Cancellation: Self-inverse gates (CX·CX = I)...
```

---

## 🎨 UI/UX Highlights

- **Dark Theme** - Purple/cyan gradient with glassmorphic design
- **Responsive Layout** - Adapts to desktop and tablet screens
- **Interactive Charts** - Plotly visualizations with hover details
- **Real-time Updates** - Changes reflect immediately
- **Educational Focus** - Explanations for every optimization

---

## 🔬 Optimization Strategies Explained

### Light Strategy
Uses basic gate optimization and CX cancellation. Best for simple circuits.

**Passes:**
- Optimize1qGatesDecomposition
- CommutativeCancellation

### Medium Strategy
Adds commutative reordering and diagonal gate removal. Good for most circuits.

**Passes:**
- Optimize1qGatesDecomposition
- CommutativeCancellation
- RemoveDiagonalGatesBeforeMeasure
- RemoveResetInZeroState

### Heavy Strategy
Includes block consolidation with KAK decomposition. Best for circuits with many 2-qubit gates.

**Passes:**
- All Medium passes
- Collect2qBlocks
- ConsolidateBlocks

### Full Strategy
Qiskit's most aggressive optimization (level 3). Best for circuits that need maximum optimization.

**Passes:**
- All Heavy passes
- Layout-aware routing
- Gate direction optimization
- Aggressive unitary resynthesis

---

## 📊 Supported Circuits

### Predefined Circuits
- **GHZ State (3/5-qubit)** - Entanglement example
- **Quantum Fourier Transform (4-qubit)** - QFT algorithm
- **Grover's Search (3-qubit)** - Search algorithm
- **Bernstein-Vazirani (4-qubit)** - Hidden string problem
- **VQE Ansatz (4-qubit)** - Variational quantum eigensolver
- **Random Circuit (4-qubit)** - With built-in redundancy
- **Quantum Teleportation (3-qubit)** - Teleportation protocol

### Custom Circuits
Build your own circuits gate-by-gate:

**Single-Qubit Gates:** H, X, Y, Z, S, T, Rx, Ry, Rz  
**Two-Qubit Gates:** CX, CZ, SWAP  
**Three-Qubit Gates:** CCX (Toffoli), CSWAP (Fredkin)

---

## 🌊 Noise Simulation

Test circuit robustness under realistic quantum hardware noise:

- **Depolarizing Error** - Single and 2-qubit gate errors
- **Thermal Relaxation** - T1 (amplitude damping) and T2 (dephasing)
- **Configurable Parameters**:
  - Error rate: 0.001 - 0.1
  - T1 relaxation: 10 - 200 µs
  - T2 dephasing: 10 - 200 µs

**Output:**
- Success probability of each circuit
- Entropy of measurement distribution
- Fidelity improvement of optimized circuit

---

## 🖥️ Hardware-Aware Transpilation

Adapt circuits to real quantum devices:

- **Device Selection**: 5, 7, 20, or 27-qubit devices
- **Automatic Routing**: Inserts SWAP gates as needed
- **Optimization Levels**: 0-3 (more aggressive = more optimization)
- **Output**: Routing analysis, SWAP count, final depth

---

## 🤖 AI Advisor

The AI Advisor automatically recommends the best optimization strategy based on:

- **Gate Density** - Gates per qubit
- **CX Ratio** - Two-qubit gates / total gates
- **Depth-to-Width** - Circuit depth / number of qubits
- **Gate Variety** - Number of distinct gate types
- **Redundancy** - Estimated cancellable gates

**Output:**
- Complexity score (0-100)
- Recommended strategy with confidence level
- Circuit profile analysis
- Reasoning for recommendation

---

## 📈 Metrics Tracked

- **Circuit Depth** - Longest path in DAG
- **Total Gates** - All gates excluding barriers and measurements
- **CX/CNOT Gates** - Two-qubit entangling gates (most expensive)
- **Single-Qubit Gates** - 1-qubit operations
- **Two-Qubit Gates** - 2-qubit operations

---

## 🔧 Configuration

All settings in `config.py`:

```python
PREDEFINED_CIRCUITS = [...]
OPTIMIZATION_STRATEGIES = {...}
HARDWARE_BACKENDS = {...}
SINGLE_QUBIT_GATES = [...]
TWO_QUBIT_GATES = [...]
THREE_QUBIT_GATES = [...]
COLORS = {...}
```

---

## 📚 Technical Details

### Circuit Representation
Uses Qiskit's `QuantumCircuit` object for circuit management and optimization.

### Optimization Pipeline
1. Build circuit
2. Extract metrics (depth, gate count, operations)
3. Apply selected transpiler passes
4. Extract optimized metrics
5. Generate educational explanation
6. Display results with visualizations

### Transpiler Passes
All passes from Qiskit's transpiler module:
- Gate optimization (1-qubit decomposition)
- Commutative cancellation
- Diagonal gate removal
- 2-qubit block consolidation
- Unitary synthesis (KAK decomposition)

---

## 🖥️ Docker Development

This project includes a dev container configuration for VS Code:

```bash
# Open in Dev Container
1. Install VS Code Remote - Containers extension
2. Open folder in container
3. Will automatically install dependencies and start the app
```

---

## 📝 Examples

### Example 1: Optimize a GHZ State

```
1. Sidebar: Select "Predefined" → "GHZ State (3-qubit)"
2. Toggle: Enable "AI Advisor"
3. Click: Optimize
4. Result: See AI recommendation and detailed explanation
```

### Example 2: Build Custom Circuit

```
1. Sidebar: Select "Custom Builder"
2. Add gates: H(q0), CX(q0, q1), CX(q1, q2)
3. Strategy: Choose "Medium"
4. Optimize
5. See: Side-by-side circuits + reasoning
```

### Example 3: Test with Noise

```
1. Build/select circuit
2. Enable: "Noise Simulation"
3. Set: Error rate 0.01, T1=50µs, T2=70µs
4. Optimize
5. Compare: Fidelity of original vs optimized under noise
```

---

## 🚀 Performance

- **Lightweight UI** - Runs smoothly on standard laptops
- **Fast Optimization** - Most circuits optimize in <1 second
- **Scalable** - Can handle circuits up to 27+ qubits
- **Real-time Rendering** - Streamlit enables instant updates

---

## 🐛 Known Limitations

- Circuits larger than 27 qubits may slow down hardware transpilation
- Noise simulation is classical (not actual quantum)
- Custom circuits limited to ~100 gates for performance

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Additional predefined circuits
- [ ] More noise models (amplitude damping, phase damping)
- [ ] Custom optimization pass chains
- [ ] Export to Qasm/OpenQASM format
- [ ] Support for parametrized circuits

---

## 📖 References

- **Qiskit**: https://qiskit.org/
- **Streamlit**: https://streamlit.io/
- **Quantum Computing Concepts**:
  - Nielsen & Chuang, "Quantum Computation and Quantum Information"
  - Pathak, "The Theory of Quantum Computation"

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👨‍💻 Author

**Sachin Kumar**  
Quantum Computing Enthusiast | SRM University

---

## 🙏 Acknowledgments

- Built with [Qiskit](https://qiskit.org/) - IBM's quantum computing framework
- UI built with [Streamlit](https://streamlit.io/) - Python web app framework
- Visualizations with [Plotly](https://plotly.com/) and [Matplotlib](https://matplotlib.org/)

---

## 📞 Support & Contact

For questions or issues, please open an issue on GitHub:  
https://github.com/sachin0610-srm/quantum-optimizer/issues

---

## 🔄 Version History

### v2.0 (Current)
- ✨ Enhanced explanation/reasoning system with 5 detailed sections
- 🎓 Educational content explaining mathematical principles
- 📖 Positioned reasoning below circuit comparison
- 🧹 Improved markdown rendering

### v1.0
- Initial release with basic optimization features
- AI advisor for strategy selection
- Noise simulation and hardware transpilation

---

**Happy Optimizing! ⚛️** 🚀
