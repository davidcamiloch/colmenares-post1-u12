# Post-Contenido 1 — Computación Cuántica con Qiskit

Arquitectura de Computadores — Unidad 12 · David Camilo Colmenares Hernández · Ingeniería de Sistemas, UFPS

El repositorio reúne las dos partes del laboratorio. La Parte 1 simula en Qiskit el estado de Bell, el algoritmo de Deutsch-Jozsa, Grover de 2 qubits y Grover bajo ruido. La Parte 2 está en [`docs/analisis-pqc.md`](docs/analisis-pqc.md) y analiza el impacto cuántico en la criptografía y la migración a los estándares NIST FIPS 203, 204 y 205.

## Estructura

```
colmenares-post1-u12/
├── README.md
├── requirements.txt
├── src/
│   ├── bell_state.py             # |Φ+> y verificación de correlación
│   ├── deutsch_jozsa.py          # oráculo constante y dos balanceados, n = 2
│   ├── grover.py                 # Grover 2 qubits; --guia reproduce el oráculo original
│   ├── grover_noise.py           # ideal vs ruido; barridos de tasa y de profundidad
│   └── grover_backend_noise.py   # despolarizante vs modelo calibrado (FakeTorino)
├── capturas/                     # histogramas y salidas de Colab
└── docs/
    └── analisis-pqc.md           # Parte 2
```

## 1. Entorno y ejecución

| Elemento | Valor |
|---|---|
| Plataforma | Google Colab (Ubuntu 24.04) |
| Python | 3.13.18 |
| Qiskit / Qiskit Aer | 2.6.2 / 0.18.4 |
| Modelo calibrado | `qiskit-ibm-runtime` con `FakeTorino` (instantánea de un procesador IBM Heron) |
| Simulador | `AerSimulator` con `seed_simulator=2026`; los conteos son reproducibles |

```bash
pip install -r requirements.txt          # qiskit, qiskit-aer, matplotlib
python src/bell_state.py
python src/deutsch_jozsa.py
python src/grover.py
python src/grover.py --guia              # muestra el error del oráculo de la guía
python src/grover_noise.py
pip install qiskit-ibm-runtime && python src/grover_backend_noise.py
```

Los scripts se ejecutan desde la raíz del repositorio; cada uno crea `capturas/` si no existe y guarda allí sus histogramas.

## 2. Estado de Bell (Checkpoint 1)

```
     ┌───┐     ┌─┐
q_0: ┤ H ├──■──┤M├───
     └───┘┌─┴─┐└╥┘┌─┐
q_1: ─────┤ X ├─╫─┤M├
          └───┘ ║ └╥┘
c: 2/═══════════╩══╩═
```

| Estado | Conteos (1024 shots) | Porcentaje |
|---|---:|---:|
| \|00⟩ | 516 | 50.4 % |
| \|11⟩ | 508 | 49.6 % |
| \|01⟩ y \|10⟩ | 0 | 0 % |

La puerta H deja al qubit 0 en (|0⟩ + |1⟩)/√2. El CNOT copia esa base en el qubit 1 y produce (|00⟩ + |11⟩)/√2. Cada medición da 00 o 11 con probabilidad 1/2; los dos bits nunca difieren. La diferencia 516 frente a 508 está dentro del error estadístico de 1024 muestras (desviación estándar de 16 conteos).

## 3. Deutsch-Jozsa (Checkpoint 2)

```
     ┌───┐      ░            ░ ┌───┐┌─┐
q_0: ┤ H ├──────░───■────────░─┤ H ├┤M├───
     ├───┤      ░   │        ░ ├───┤└╥┘┌─┐
q_1: ┤ H ├──────░───┼────■───░─┤ H ├─╫─┤M├
     ├───┤┌───┐ ░ ┌─┴─┐┌─┴─┐ ░ └───┘ ║ └╥┘
q_2: ┤ X ├┤ H ├─░─┤ X ├┤ X ├─░───────╫──╫─
     └───┘└───┘ ░ └───┘└───┘ ░       ║  ║
c: 2/════════════════════════════════╩══╩═
```

| Oráculo | Función | Conteos | Conclusión |
|---|---|---|---|
| Constante | f(x) = 0 | {'00': 1024} | Constante |
| Balanceado 1 | f(x) = x0 ⊕ x1 | {'11': 1024} | Balanceada |
| Balanceado 2 | f(x) = x0 | {'01': 1024} | Balanceada |

El ancilla en |−⟩ convierte la evaluación del oráculo en una fase (−1)^f(x) sobre cada entrada. Las H finales hacen interferir las cuatro fases. Si f es constante todas las fases son iguales y la amplitud se concentra en |00⟩. Si f es balanceada la mitad de las fases se cancela con la otra mitad y la amplitud de |00⟩ es exactamente cero. Por eso basta una sola evaluación del oráculo. Un algoritmo clásico determinista con n = 2 necesita en el peor caso 2^(n−1) + 1 = 3 evaluaciones: si las dos primeras coinciden, solo la tercera decide.

## 4. Grover de 2 qubits (Checkpoint 3)

```
     ┌───┐ ░     ░ ┌───┐┌───┐   ┌───┐┌───┐┌─┐
q_0: ┤ H ├─░──■──░─┤ H ├┤ X ├─■─┤ X ├┤ H ├┤M├───
     ├───┤ ░  │  ░ ├───┤├───┤ │ ├───┤├───┤└╥┘┌─┐
q_1: ┤ H ├─░──■──░─┤ H ├┤ X ├─■─┤ X ├┤ H ├─╫─┤M├
     └───┘ ░     ░ └───┘└───┘   └───┘└───┘ ║ └╥┘
c: 2/══════════════════════════════════════╩══╩═
```

| Objetivo | Conteos del objetivo | Éxito | Oráculo de la guía |
|---|---:|---:|---|
| \|00⟩ | 1024 | 100 % | Correcto |
| \|01⟩ | 1024 | 100 % | Mide \|10⟩: ERROR |
| \|10⟩ | 1024 | 100 % | Mide \|01⟩: ERROR |
| \|11⟩ | 1024 | 100 % | Correcto |

Una iteración basta porque N = 4. El estado inicial forma un ángulo θ con los estados no marcados, con sen θ = 1/√N = 1/2; es decir θ = 30°. Cada iteración rota el estado 2θ hacia el objetivo y la amplitud del objetivo después de k iteraciones es sen((2k + 1)θ). Con k = 1 el argumento vale 90° y la probabilidad es exactamente 1. Una segunda iteración llevaría el ángulo a 150° y la probabilidad bajaría a 25 %.

## 5. Grover bajo ruido despolarizante (Checkpoint 4)

| Configuración (target \|11⟩) | Éxito | Detalle |
|---|---:|---|
| Sin ruido, 1024 shots | 100.0 % | {'11': 1024} |
| p1q = 0.1 %, p2q = 1 %, 1024 shots | 97.9 % | {'00': 8, '01': 8, '10': 6, '11': 1002}; error estándar 0.45 pp |
| Degradación | 2.1 pp | |

| p2q (p1q = p2q/10), 4096 shots | 0.1 % | 0.5 % | 1 % | 3 % | 5 % | 10 % |
|---|---:|---:|---:|---:|---:|---:|
| Éxito medido | 99.8 % | 98.9 % | 98.0 % | 93.6 % | 89.8 % | 81.1 % |
| Modelo 1/4 + 3/4·(1−p1q)^n1·(1−p2q)^n2 | 99.8 % | 98.9 % | 97.8 % | 93.5 % | 89.4 % | 79.9 % |

| Puertas CZ en el circuito (p2q = 1 %) | 2 | 12 | 22 | 52 | 102 | 202 | 402 |
|---|---:|---:|---:|---:|---:|---:|---:|
| Éxito medido | 98.0 % | 90.7 % | 84.5 % | 69.7 % | 51.3 % | 33.6 % | 25.8 % |
| Modelo | 97.8 % | 90.8 % | 84.5 % | 69.0 % | 51.6 % | 34.8 % | 26.3 % |

La profundidad se aumentó insertando k pares CZ·CZ, que equivalen a la identidad: el circuito lógico no cambia y solo crece el número de puertas ruidosas. La guía anuncia 89.4 % de éxito con p2q = 1 %. El valor medido es 97.9 %; la cifra de la guía corresponde a p2q cercano a 5 % (89.8 % medido).

## 6. Despolarizante uniforme vs modelo calibrado

`grover_backend_noise.py` transpila el mismo circuito a las puertas nativas de `FakeTorino` (rz, sx, x, cz) sobre el par acoplado de qubits 0 y 1 y lo simula con `AerSimulator.from_backend()`. Ese modelo combina error despolarizante, relajación térmica con T1 y T2 por qubit y error de lectura (Qiskit Aer, s.f.).

| Dato de calibración | q0 | q1 |
|---|---:|---:|
| T1 | 224.1 µs | 266.0 µs |
| T2 | 314.6 µs | 204.0 µs |
| Error de lectura | 16.67 % | 2.29 % |
| Puerta sx | 32 ns; error 0.034 % | 32 ns; error 0.017 % |
| Puerta cz(0,1) | 68 ns; error 0.485 % | |

| Puertas CZ | Despolarizante uniforme | Calibrado FakeTorino |
|---:|---:|---:|
| 2 | 98.0 % | 80.3 % |
| 22 | 84.5 % | 73.2 % |
| 102 | 51.3 % | 54.3 % |

## 7. Desviaciones respecto al código guía

| # | Código guía | Problema detectado | Corrección aplicada |
|---|---|---|---|
| 1 | Oráculo de `grover.py` para 01 y 10 | Qiskit ordena los bits como q1q0; `x(0)` antes de CZ marca \|10⟩ y no \|01⟩. Con el código original el objetivo 01 mide 10 y viceversa (`python src/grover.py --guia`) | `add_oracle()` aplica X a los qubits cuyo bit es 0 leyendo el objetivo de derecha a izquierda |
| 2 | f-string con comillas dobles anidadas en `grover.py` | Solo es válido desde Python 3.12 (PEP 701); la guía exige Python 3.9 o superior y en 3.9 a 3.11 es error de sintaxis | El veredicto se calcula antes en una variable |
| 3 | `savefig("capturas/...")` sin crear la carpeta | `FileNotFoundError` si se ejecuta en un clon limpio | `os.makedirs("capturas", exist_ok=True)` |
| 4 | Sin semilla en `AerSimulator` | Los conteos cambian en cada corrida y la tabla del README no se puede reproducir | `seed_simulator=2026` |
| 5 | `print(f"Diagrama: {qc.draw()}")` | Imprime el diagrama pegado al texto y descuadrado | `print(qc.draw(output="text"))` en su propia salida |
| 6 | Deutsch-Jozsa verifica `"00" in counts_c` | Pasaría aunque apareciera otro estado; el resultado debe ser determinista | `counts_c == {"00": shots}` y un segundo oráculo balanceado |
| 7 | Salida esperada de `grover_noise.py`: 89.4 % | Con p1q = 0.1 % y p2q = 1 % el circuito solo tiene 2 CZ; el valor medido es 97.9 % | Se documentó la cifra real y se agregaron barridos de tasa y profundidad |

## 8. Capturas

| Checkpoint | Archivos |
|---|---|
| 1. Bell | `capturas/bell_histogram.png`, `capturas/cp1-bell-salida.png` |
| 2. Deutsch-Jozsa | `capturas/cp2-deutsch-jozsa-salida.png`, `capturas/cp2-deutsch-jozsa-conteos.png` |
| 3. Grover | `capturas/grover_00.png`, `capturas/grover_01.png`, `capturas/grover_10.png`, `capturas/grover_11.png`, `capturas/cp3-grover-salida.png`, `capturas/cp3-grover-oraculo-guia.png` |
| 4. Grover con ruido | `capturas/grover_noise_comparison.png`, `capturas/grover_noise_profundidad.png`, `capturas/cp4-grover-noise-salida.png` |
| 5. Decisiones | `capturas/cp5-modelo-calibrado.png` |

Los histogramas de `capturas/` se dibujaron a partir de los conteos que imprimió cada script en Colab con la semilla 2026; al ejecutar los scripts se regeneran con los mismos nombres.

## Referencias

- Acharya, R., et al. (Google Quantum AI). (2024). *Quantum error correction below the surface code threshold*. arXiv. https://arxiv.org/abs/2408.13687
- Qiskit Aer. (s.f.). *NoiseModel*. Recuperado el 19 de noviembre de 2026 de https://qiskit.github.io/qiskit-aer/stubs/qiskit_aer.noise.NoiseModel.html
