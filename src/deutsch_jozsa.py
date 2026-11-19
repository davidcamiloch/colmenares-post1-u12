"""Algoritmo de Deutsch-Jozsa para n = 2 con oráculos constante y balanceados.

Arquitectura de Computadores - Unidad 12 - Post-contenido 1.
Uso: python src/deutsch_jozsa.py
"""
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

SEED = 2026


def oracle_constante(n):
    """f(x) = 0 para toda x: el oráculo no modifica el ancilla."""
    return QuantumCircuit(n + 1, name="Uf constante")


def oracle_balanceada(n):
    """f(x) = x0 XOR x1 XOR ...: un CNOT de cada qubit de entrada al ancilla."""
    qc = QuantumCircuit(n + 1, name="Uf balanceada")
    for i in range(n):
        qc.cx(i, n)
    return qc


def oracle_balanceada_x0(n):
    """f(x) = x0: segundo oráculo balanceado (solo depende del qubit 0)."""
    qc = QuantumCircuit(n + 1, name="Uf x0")
    qc.cx(0, n)
    return qc


def deutsch_jozsa_circuit(oracle_qc, n):
    """H en todos, una sola consulta al oráculo, H en las entradas y medición."""
    qc = QuantumCircuit(n + 1, n)
    qc.x(n)                 # ancilla en |1>
    qc.h(range(n + 1))      # entradas en superposición; ancilla en |->
    qc.barrier()
    qc.compose(oracle_qc, inplace=True)   # ÚNICA evaluación del oráculo
    qc.barrier()
    qc.h(range(n))          # interferencia
    qc.measure(range(n), range(n))
    return qc


def deutsch_jozsa(oracle_qc, n, shots=1024):
    qc = deutsch_jozsa_circuit(oracle_qc, n)
    return AerSimulator(seed_simulator=SEED).run(qc, shots=shots).result().get_counts()


if __name__ == "__main__":
    n, shots = 2, 1024
    ceros = "0" * n
    print(deutsch_jozsa_circuit(oracle_balanceada(n), n).draw(output="text"))

    counts_c = deutsch_jozsa(oracle_constante(n), n, shots)
    counts_b = deutsch_jozsa(oracle_balanceada(n), n, shots)
    counts_b0 = deutsch_jozsa(oracle_balanceada_x0(n), n, shots)
    print(f"Constante        f(x)=0       : {counts_c}")
    print(f"Balanceada       f(x)=x0^x1   : {counts_b}")
    print(f"Balanceada       f(x)=x0      : {counts_b0}")

    # Resultado determinista: todo |00> para constante; nunca |00> si es balanceada
    assert counts_c == {ceros: shots}, "Error: el oráculo constante no retornó siempre 00"
    assert ceros not in counts_b and ceros not in counts_b0, "Error: un oráculo balanceado retornó 00"
    print(f"Consultas al oráculo: cuántico = 1 | clásico peor caso = 2^(n-1)+1 = {2 ** (n - 1) + 1}")
    print("OK: Deutsch-Jozsa verifica correctamente")
