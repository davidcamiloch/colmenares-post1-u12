"""Grover 2 qubits bajo un NoiseModel despolarizante y efecto de la profundidad.

Arquitectura de Computadores - Unidad 12 - Post-contenido 1.
Uso: python src/grover_noise.py

Experimentos:
  1. Ideal vs ruido con p1q = 0.1 % y p2q = 1 % (configuración de la guía).
  2. Barrido de la tasa de error de 2 qubits.
  3. Profundidad: se insertan k pares CZ-CZ (identidad lógica) para medir cómo
     se acumula el error cuando el circuito tiene más puertas de 2 qubits.
"""
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error
from qiskit.visualization import plot_histogram

from grover import add_diffuser, add_oracle

SEED = 2026


def build_grover_circuit(target="11", extra_cz_pairs=0):
    """Mismo circuito del Paso 3; opcionalmente con k pares CZ-CZ (= identidad)."""
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])
    add_oracle(qc, target)
    for _ in range(extra_cz_pairs):
        qc.cz(0, 1)
        qc.cz(0, 1)
    add_diffuser(qc)
    qc.measure([0, 1], [0, 1])
    return qc


def build_noise_model(p1q=0.001, p2q=0.01):
    """Error despolarizante p1q en h y x; p2q en cz."""
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p1q, 1), ["h", "x"])
    noise_model.add_all_qubit_quantum_error(depolarizing_error(p2q, 2), ["cz"])
    return noise_model


def run(qc, shots, noise_model=None):
    sim = AerSimulator(noise_model=noise_model, seed_simulator=SEED)
    return sim.run(qc, shots=shots).result().get_counts()


def gate_counts(qc):
    ops = qc.count_ops()
    return ops.get("h", 0) + ops.get("x", 0), ops.get("cz", 0)


def modelo(p1q, p2q, n1, n2):
    """Aproximación: la señal sobrevive con (1-p1q)^n1 (1-p2q)^n2; el resto es uniforme."""
    f = (1 - p1q) ** n1 * (1 - p2q) ** n2
    return 0.25 + 0.75 * f


def grover_noise_experiment(target="11", shots=1024):
    qc = build_grover_circuit(target)
    counts_ideal = run(qc, shots)
    counts_noisy = run(qc, shots, build_noise_model())

    p_ideal = counts_ideal.get(target, 0) / shots
    p_noisy = counts_noisy.get(target, 0) / shots
    se = math.sqrt(p_noisy * (1 - p_noisy) / shots)
    print(f"Grover |{target}> sin ruido: {p_ideal * 100:.1f}%")
    print(f"Grover |{target}> con ruido: {p_noisy * 100:.1f}%  (error estándar {se * 100:.2f} pp)")
    print(f"Degradacion: {(p_ideal - p_noisy) * 100:.1f} puntos porcentuales")
    print(f"Conteos con ruido: {dict(sorted(counts_noisy.items()))}")

    fig, axs = plt.subplots(1, 2, figsize=(10, 4))
    plot_histogram(counts_ideal, ax=axs[0], title="Sin ruido")
    plot_histogram(counts_noisy, ax=axs[1], title="Con ruido (despolarizante)")
    fig.tight_layout()
    os.makedirs("capturas", exist_ok=True)
    fig.savefig("capturas/grover_noise_comparison.png", dpi=150)
    plt.close(fig)
    return p_ideal, p_noisy


def barrido_tasa(target="11", shots=4096):
    print("\nBarrido de la tasa de error (p1q = p2q / 10):")
    qc = build_grover_circuit(target)
    n1, n2 = gate_counts(qc)
    for p2q in [0.001, 0.005, 0.01, 0.03, 0.05, 0.10]:
        counts = run(qc, shots, build_noise_model(p2q / 10, p2q))
        p = counts.get(target, 0) / shots
        print(f"  p2q = {p2q * 100:5.1f}% | éxito medido {p * 100:5.1f}% | "
              f"modelo {modelo(p2q / 10, p2q, n1, n2) * 100:5.1f}%")


def barrido_profundidad(target="11", shots=4096):
    print("\nProfundidad con p1q = 0.1 % y p2q = 1 % (k pares CZ-CZ insertados):")
    ks = [0, 5, 10, 25, 50, 100, 200]
    medidos = []
    nm = build_noise_model()
    for k in ks:
        qc = build_grover_circuit(target, extra_cz_pairs=k)
        n1, n2 = gate_counts(qc)
        p = run(qc, shots, nm).get(target, 0) / shots
        medidos.append(p)
        print(f"  k = {k:3d} | puertas CZ = {n2:3d} | éxito medido {p * 100:5.1f}% | "
              f"modelo {modelo(0.001, 0.01, n1, n2) * 100:5.1f}%")

    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot([2 + 2 * k for k in ks], [m * 100 for m in medidos], "o-", label="Medido (4096 shots)")
    ax.axhline(25, color="gray", ls="--", label="Azar (25 %)")
    ax.set_xlabel("Puertas CZ en el circuito")
    ax.set_ylabel("Probabilidad de |11> (%)")
    ax.set_title("Grover 2 qubits: éxito vs. profundidad (p2q = 1 %)")
    ax.legend()
    fig.tight_layout()
    fig.savefig("capturas/grover_noise_profundidad.png", dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    grover_noise_experiment()
    barrido_tasa()
    barrido_profundidad()
