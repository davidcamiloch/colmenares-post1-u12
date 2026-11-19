"""Estado de Bell |Phi+> = (|00> + |11>)/sqrt(2) con verificación de correlación.

Arquitectura de Computadores - Unidad 12 - Post-contenido 1.
Uso: python src/bell_state.py   (desde la raíz del repositorio)
"""
import os

import matplotlib
matplotlib.use("Agg")  # sin ventana: funciona en Colab, terminal y CI
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

SEED = 2026  # semilla fija: los conteos son reproducibles


def bell_circuit():
    """Construye el circuito H(q0) + CNOT(q0 -> q1) + medición."""
    qc = QuantumCircuit(2, 2)  # 2 qubits, 2 bits clásicos
    qc.h(0)                    # superposición (|0> + |1>)/sqrt(2) en q0
    qc.cx(0, 1)                # entrelazamiento: q1 copia la base de q0
    qc.measure([0, 1], [0, 1])
    return qc


def bell_state_experiment(shots=1024):
    """Prepara |Phi+>, mide y verifica que solo aparecen |00> y |11>."""
    qc = bell_circuit()
    counts = AerSimulator(seed_simulator=SEED).run(qc, shots=shots).result().get_counts()

    print(qc.draw(output="text"))
    print(f"Resultados Bell |Phi+> ({shots} shots):")
    for state, count in sorted(counts.items()):
        print(f"  |{state}> : {count:4d} ({count / shots * 100:.1f}%)")

    # Correlación perfecta: los dos bits medidos siempre coinciden
    assert set(counts) <= {"00", "11"}, "ERROR: aparecieron estados no entrelazados"
    assert sum(counts.values()) == shots
    print("OK: correlación perfecta verificada (0 resultados |01> o |10>)")

    os.makedirs("capturas", exist_ok=True)
    fig = plot_histogram(counts, title="Estado de Bell |Φ+> (1024 shots)")
    fig.savefig("capturas/bell_histogram.png", dpi=150, bbox_inches="tight")
    return counts


if __name__ == "__main__":
    bell_state_experiment()
