"""Compara el ruido despolarizante uniforme con un modelo calibrado de IBM.

Arquitectura de Computadores - Unidad 12 - Post-contenido 1.
Uso: pip install qiskit-ibm-runtime && python src/grover_backend_noise.py

FakeTorino guarda una instantánea de calibración de un procesador IBM Heron:
T1 y T2 por qubit, duración y error de cada puerta, error de lectura. Con
AerSimulator.from_backend() esos datos se convierten en un NoiseModel
(relajación térmica + despolarizante + lectura) sin acceso a hardware real.
"""
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeTorino

from grover_noise import build_grover_circuit, build_noise_model, run

SEED = 2026
SHOTS = 4096


def main():
    backend = FakeTorino()
    q0, q1 = list(backend.coupling_map.get_edges())[0]   # par acoplado: sin SWAP
    sim_cal = AerSimulator.from_backend(backend, seed_simulator=SEED)

    t = backend.target
    print(f"Backend: {backend.name} | qubits físicos usados: {q0}, {q1}")
    for q in (q0, q1):
        p = backend.qubit_properties(q)
        print(f"  q{q}: T1 = {p.t1 * 1e6:6.1f} us | T2 = {p.t2 * 1e6:6.1f} us | "
              f"error de lectura = {t['measure'][(q,)].error * 100:.2f}% | "
              f"sx: {t['sx'][(q,)].duration * 1e9:.0f} ns, error {t['sx'][(q,)].error * 100:.3f}%")
    cz = t["cz"][(q0, q1)]
    print(f"  cz({q0},{q1}): duración {cz.duration * 1e9:.0f} ns | error {cz.error * 100:.3f}%")

    print("\nÉxito de Grover |11> (4096 shots): despolarizante uniforme vs calibrado")
    for k in [0, 10, 50]:
        qc = build_grover_circuit("11", extra_cz_pairs=k)
        tqc = transpile(qc, backend=backend, initial_layout=[q0, q1],
                        optimization_level=0, seed_transpiler=SEED)
        p_dep = run(qc, SHOTS, build_noise_model()).get("11", 0) / SHOTS
        p_cal = sim_cal.run(tqc, shots=SHOTS).result().get_counts().get("11", 0) / SHOTS
        ops = dict(tqc.count_ops())
        print(f"  k = {k:2d} | despolarizante {p_dep * 100:5.1f}% | calibrado {p_cal * 100:5.1f}% | "
              f"puertas nativas {ops}")


if __name__ == "__main__":
    main()
