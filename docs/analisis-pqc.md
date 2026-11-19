# Impacto de la computación cuántica en la ciberseguridad y plan de migración post-cuántica

David Camilo Colmenares Hernández · Arquitectura de Computadores 1154507-B · Unidad 12 · Universidad Francisco de Paula Santander

## Introducción

El documento analiza qué parte de la criptografía actual rompe una computadora cuántica tolerante a fallos y cómo se migra a los tres estándares que el NIST publicó el 13 de agosto de 2024: ML-KEM (FIPS 203), ML-DSA (FIPS 204) y SLH-DSA (FIPS 205). Las cifras de tamaño provienen de las tablas oficiales de cada FIPS. Las cifras de rendimiento y de despliegue provienen de Google Chrome y de Cloudflare.

La tesis es directa. Shor rompe toda la criptografía de clave pública basada en factorización y logaritmo discreto; Grover solo debilita la simétrica y los hash. La amenaza ya es actual para los datos de vida larga porque un adversario puede guardar hoy el tráfico cifrado y descifrarlo cuando exista la máquina: el ataque harvest now, decrypt later (HNDL) (O'Brien, 2023).

## 1. Inventario de algoritmos vulnerables

| Algoritmo | Tipo | Vulnerabilidad cuántica | Algoritmo atacante | Acción |
|---|---|---|---|---|
| RSA-2048 / RSA-4096 | Cifrado y firma asimétricos | Roto completamente | Shor (factorización en tiempo polinomial) | Reemplazar: ML-KEM para cifrado; ML-DSA para firma |
| ECDSA P-256 / P-384 | Firma digital | Roto completamente | Shor (logaritmo discreto en curvas elípticas) | Reemplazar con ML-DSA |
| ECDH / X25519 | Intercambio de clave | Roto completamente | Shor | Reemplazar con ML-KEM; transición híbrida X25519MLKEM768 |
| Diffie-Hellman finito | Intercambio de clave | Roto completamente | Shor | Reemplazar con ML-KEM |
| AES-128 | Cifrado simétrico | Debilitado: búsqueda de 2^128 a unas 2^64 evaluaciones | Grover | Aceptable para uso general; AES-256 donde la norma lo exija |
| AES-256 | Cifrado simétrico | Margen amplio: unas 2^128 evaluaciones | Grover | Mantener |
| SHA-256 | Función hash | Debilitada en preimagen (2^256 a 2^128) y en colisión | Grover; Brassard-Høyer-Tapp | Mantener para integridad; SHA-384 en sistemas CNSA 2.0 |
| SHA3-256 | Función hash | Igual que SHA-256 | Grover | SHA3-384 o mayor en sistemas de seguridad nacional |

El análisis distingue dos categorías. Un algoritmo roto pierde toda su seguridad: quien capturó el tráfico protegido con RSA o ECDH recupera la clave de sesión y lee todo el pasado. Esa es la amenaza HNDL. Un algoritmo debilitado conserva seguridad útil: Grover da solo una aceleración cuadrática y no se paraleliza bien. Cloudflare sostiene que duplicar las claves simétricas no es necesario y que AES-128 sigue siendo seguro (Westerbaan, 2024). La NSA, en cambio, exige AES-256 y SHA-384 para sus sistemas (Elevate Consult, 2026). Ambas posiciones coinciden en lo esencial: la urgencia está en la clave pública.

## 2. Estándares NIST PQC 2024

ML-KEM es un mecanismo de encapsulamiento de clave basado en Module Learning With Errors (NIST, 2024a). ML-DSA es un esquema de firma basado en retículos modulares (NIST, 2024b). SLH-DSA es un esquema de firma sin estado basado en funciones hash; su seguridad depende de la dificultad de encontrar preimágenes y propiedades relacionadas de la función hash (NIST, 2024c).

| Estándar | Parámetro | Categoría NIST | Clave pública (B) | Clave privada (B) | Ciphertext o firma (B) | Fuente |
|---|---|---|---:|---:|---:|---|
| ML-KEM | ML-KEM-512 | 1 | 800 | 1 632 | 768 | NIST (2024a) |
| ML-KEM | ML-KEM-768 | 3 | 1 184 | 2 400 | 1 088 | NIST (2024a) |
| ML-KEM | ML-KEM-1024 | 5 | 1 568 | 3 168 | 1 568 | NIST (2024a) |
| ML-DSA | ML-DSA-44 | 2 | 1 312 | 2 560 | 2 420 | NIST (2024b) |
| ML-DSA | ML-DSA-65 | 3 | 1 952 | 4 032 | 3 309 | NIST (2024b) |
| ML-DSA | ML-DSA-87 | 5 | 2 592 | 4 896 | 4 627 | NIST (2024b) |
| SLH-DSA | 128s / 128f | 1 | 32 | 64 | 7 856 / 17 088 | NIST (2024c) |
| SLH-DSA | 192s / 192f | 3 | 48 | 96 | 16 224 / 35 664 | NIST (2024c) |
| SLH-DSA | 256s / 256f | 5 | 64 | 128 | 29 792 / 49 856 | NIST (2024c) |

| Esquema de firma | Firma (B) | Tiempo de firma | Tiempo de verificación |
|---|---:|---:|---:|
| Ed25519 (referencia clásica) | 64 | 1 | 1 |
| RSA-2048 | 256 | 70 | 0.3 |
| ML-DSA-44 | 2 420 | 4.8 | 0.5 |
| SLH-DSA-128s | 7 856 | 8 000 | 2.8 |
| SLH-DSA-128f | 17 088 | 550 | 7 |

Tiempos de CPU relativos a Ed25519 según Westerbaan (2024); varían según la plataforma.

ML-KEM reemplaza a ECDH, X25519 y al transporte de clave con RSA. ML-DSA y SLH-DSA reemplazan a ECDSA y a la firma RSA. ML-DSA es la firma de uso general: verifica más rápido que Ed25519 y firma solo 4.8 veces más lento. SLH-DSA es el respaldo conservador: no depende de ningún problema algebraico estructurado; si un avance criptoanalítico rompiera los retículos, SLH-DSA seguiría en pie. Su precio es una firma de 7 856 bytes que tarda 8 000 veces más en generarse que una de Ed25519.

## Referencias

Chu, J., Dukkipati, N., Cheng, Y., & Mathis, M. (2013). *Increasing TCP's initial window* (RFC 6928). RFC Editor. https://www.rfc-editor.org/rfc/rfc6928

CISA, NSA, & NIST. (2023). *Quantum-readiness: Migration to post-quantum cryptography*. Cybersecurity and Infrastructure Security Agency. https://www.cisa.gov/resources-tools/resources/quantum-readiness-migration-post-quantum-cryptography

Elevate Consult. (2026, 13 de noviembre). *CNSA 2.0: What the NSA quantum-resistant suite means for defense contractors*. https://elevateconsult.com/?p=259389

National Institute of Standards and Technology. (2024a). *Module-lattice-based key-encapsulation mechanism standard* (FIPS 203). https://doi.org/10.6028/NIST.FIPS.203

National Institute of Standards and Technology. (2024b). *Module-lattice-based digital signature standard* (FIPS 204). https://doi.org/10.6028/NIST.FIPS.204

National Institute of Standards and Technology. (2024c). *Stateless hash-based digital signature standard* (FIPS 205). https://doi.org/10.6028/NIST.FIPS.205

O'Brien, D. (2023, 10 de agosto). *Protecting Chrome traffic with hybrid Kyber KEM*. Chromium Blog. https://blog.chromium.org/2023/08/protecting-chrome-traffic-with-hybrid.html

Westerbaan, B. (2024, 5 de marzo). *The state of the post-quantum Internet*. The Cloudflare Blog. https://blog.cloudflare.com/pq-2024/
