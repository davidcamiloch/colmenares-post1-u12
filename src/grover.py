"""Algoritmo de Grover para n = 2 qubits (espacio de 4 estados, 1 iteración).

Arquitectura de Computadores - Unidad 12 - Post-contenido 1.
Uso:
  python src/grover.py          -> busca los 4 objetivos con el oráculo corregido
  python src/grover.py --guia   -> reproduce el oráculo de la guía (falla en 01 y 10)

Convención de Qiskit: la cadena de conteos es "c1c0"; el bit de la derecha es
el qubit 0. El oráculo debe leer el objetivo en ese mismo orden.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_histogram

SEED = 2026


def add_oracle(qc, target):
    """Oráculo de fase: multiplica por -1 solo la amplitud de |target>.

    target se escribe como Qiskit imprime los conteos ("q1q0"). Se aplica X a
    cada qubit cuyo bit objetivo es 0, luego CZ y se deshacen las X.
    """
    flips = [q for q, bit in enumerate(reversed(target)) if bit == "0"]
    if flips:
        qc.x(flips)
    qc.cz(0, 1)
    if flips:
        qc.x(flips)


def add_oracle_guia(qc, target):
    """Oráculo tal como aparece en la guía: confunde el orden de los qubits."""
    if target == "11":
        qc.cz(0, 1)
    elif target == "00":
        qc.x([0, 1]); qc.cz(0, 1); qc.x([0, 1])
    elif target == "01":
        qc.x(0); qc.cz(0, 1); qc.x(0)     # marca en realidad |10>
    elif target == "10":
        qc.x(1); qc.cz(0, 1); qc.x(1)     # marca en realidad |01>


def add_diffuser(qc):
    """Inversión alrededor de la media: H X CZ X H."""
    qc.h([0, 1])
    qc.x([0, 1])
    qc.cz(0, 1)
    qc.x([0, 1])
    qc.h([0, 1])


def grover_circuit(target="11", guia=False):
    qc = QuantumCircuit(2, 2)
    qc.h([0, 1])                       # superposición uniforme
    qc.barrier()
    (add_oracle_guia if guia else add_oracle)(qc, target)
    qc.barrier()
    add_diffuser(qc)
    qc.measure([0, 1], [0, 1])
    return qc


def grover_2qubits(target="11", shots=1024, guia=False, save=True):
    qc = grover_circuit(target, guia)
    counts = AerSimulator(seed_simulator=SEED).run(qc, shots=shots).result().get_counts()

    print(f"Grover buscando |{target}> ({shots} shots){' [oráculo de la guía]' if guia else ''}:")
    for state, count in sorted(counts.items()):
        print(f"  |{state}>: {count:4d} ({count / shots * 100:.1f}%)")
    top = max(counts, key=counts.get)
    veredicto = "CORRECTO" if top == target else "ERROR"   # comillas simples: válido en Python 3.9+
    print(f"Estado más probable: |{top}> - {veredicto}")

    if save:
        os.makedirs("capturas", exist_ok=True)
        fig = plot_histogram(counts, title=f"Grover 2 qubits, objetivo |{target}>")
        fig.savefig(f"capturas/grover_{target}.png", dpi=150, bbox_inches="tight")
    return counts, top == target


if __name__ == "__main__":
    guia = "--guia" in sys.argv
    if not guia:
        print(grover_circuit("11").draw(output="text"))
    resultados = {}
    for t in ["00", "01", "10", "11"]:
        counts, ok = grover_2qubits(target=t, guia=guia, save=not guia)
        resultados[t] = ok
        print()
    print("Resumen:", {t: ("OK" if ok else "FALLA") for t, ok in resultados.items()})
