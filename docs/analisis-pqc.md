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

## 3. Plan de migración por perfil

Las tres organizaciones siguen el mismo método recomendado por CISA, NSA y NIST: una hoja de ruta de preparación cuántica; un inventario criptográfico; la revisión de la cadena de suministro; el diálogo con los proveedores (CISA, NSA, & NIST, 2023). Lo que cambia es el horizonte de sensibilidad de los datos y, con él, la urgencia.

### Perfil A — Hospital universitario (sensibilidad de 50 a 75 años)

1. Inventario. Portal de pacientes con TLS 1.3 (X25519 + certificados ECDSA); firma ECDSA de prescripciones; respaldos cifrados de historias clínicas; VPN con sedes; integración HL7 con laboratorios.
2. Clasificación. Historia clínica: confidencialidad de 50 a 75 años; prioridad máxima por HNDL. Prescripción firmada: autenticidad durante la vigencia legal del documento. Datos operativos: menos de 5 años.
3. Estrategia híbrida. X25519MLKEM768 en el portal y en la VPN de inmediato; los respaldos se recifran con AES-256 y claves envueltas con ML-KEM-1024. Firma de prescripciones con ML-DSA-65 en paralelo con ECDSA hasta que los verificadores externos acepten la nueva firma.
4. Cronograma. Hito 1 (primer trimestre de 2027): inventario completo y TLS híbrido en el portal. Hito 2 (2027): firma dual ECDSA + ML-DSA-65 en prescripciones. Hito 3 (2028): respaldos recifrados con claves envueltas por ML-KEM-1024. Hito 4 (2030): retiro de RSA y ECDSA en sistemas internos.
5. Riesgos y mitigación. Equipos médicos con firmware antiguo que no aceptan certificados grandes: segmentarlos detrás de un proxy TLS. Interoperabilidad con farmacias: firma dual durante la transición.

La prioridad del Perfil A es la confidencialidad: cada mes sin intercambio de clave post-cuántico agrega historias clínicas al archivo de un posible atacante HNDL.

### Perfil B — Startup de comercio electrónico (sensibilidad de 5 a 7 años)

1. Inventario. TLS 1.3 con X25519 y ECDSA en el CDN y en el origen; tokens de pago bajo PCI-DSS; API con clientes móviles; JWT firmados con ES256.
2. Clasificación. Datos de tarjeta: 5 a 7 años; datos de sesión: horas.
3. Estrategia híbrida. Activar X25519MLKEM768 en el CDN y en el origen; Chrome lo soporta desde la versión 116 (O'Brien, 2023). Los certificados siguen en ECDSA hasta que la Web PKI ofrezca certificados ML-DSA.
4. Cronograma. Hito 1 (2026): TLS híbrido en CDN y origen. Hito 2 (2027): librerías móviles con soporte híbrido. Hito 3 (2028 a 2029): certificados ML-DSA cuando los acepten navegadores y autoridades. Hito 4 (2033): evaluación de PQC puro.
5. Riesgos y mitigación. Middleboxes que fallan con ClientHello de más de un paquete: monitoreo de errores de handshake y opción de desactivar el grupo híbrido.

### Perfil C — Entidad gubernamental de defensa (sensibilidad de 25 a 50 años)

1. Inventario. PKI nacional; firma de documentos oficiales; VPN entre agencias; firma de software y firmware; equipos de red.
2. Clasificación. Comunicaciones clasificadas: 25 a 50 años; firmas de firmware: vida útil del equipo.
3. Estrategia híbrida. Algoritmos CNSA 2.0: ML-KEM-1024, ML-DSA-87, LMS o XMSS para firmware, AES-256 y SHA-384 (Elevate Consult, 2026). El modo híbrido solo durante la transición de cada categoría.
4. Cronograma CNSA 2.0. Firma de software y firmware: preferir desde 2025 y uso exclusivo en 2030. Equipos de red y VPN: preferir desde 2026 y exclusivo en 2030. Navegadores, servidores y nube: preferir desde 2025 y exclusivo en 2033. Sistemas operativos: preferir desde 2027 y exclusivo en 2033 (Elevate Consult, 2026).
5. Riesgos y mitigación. Ciclos de compra largos: exigir CNSA 2.0 en cada contrato nuevo. PKI nacional con raíces de larga vida: emitir raíces nuevas con ML-DSA-87 y SLH-DSA como raíz de respaldo.

## 4. Tamaños de clave y firma frente a la criptografía clásica; impacto en TLS 1.3 híbrido

| Algoritmo | Tipo | Clave pública (B) | Clave privada (B) | Firma o ciphertext (B) | Nivel de seguridad | Fuente |
|---|---|---:|---:|---:|---|---|
| RSA-3072 | Cifrado y firma clásicos | 384 (módulo) | Unos 1 700 en formato CRT | 384 (firma) | 128 bits clásicos; no post-cuántico | Calculado del tamaño de módulo |
| ECDSA P-256 | Firma clásica | 64 (65 sin comprimir) | 32 | 64 en bruto; 70 a 72 en DER | 128 bits clásicos; no post-cuántico | Calculado del tamaño de curva |
| X25519 | Intercambio de clave clásico | 32 | 32 | No aplica | 128 bits clásicos; no post-cuántico | Westerbaan (2024) |
| ML-KEM-768 | KEM post-cuántico | 1 184 | 2 400 | 1 088 (ciphertext) | Categoría 3 (≈ AES-192) | NIST (2024a) |
| ML-DSA-65 | Firma post-cuántica | 1 952 | 4 032 | 3 309 | Categoría 3 (≈ AES-192) | NIST (2024b) |
| SLH-DSA-128s | Firma post-cuántica basada en hash | 32 | 64 | 7 856 | Categoría 1 (≈ AES-128) | NIST (2024c) |

El crecimiento es grande. La clave pública de ML-KEM-768 mide 37 veces la de X25519 (1 184 frente a 32 bytes). La firma de ML-DSA-65 mide 46 veces la de ECDSA P-256 en DER (3 309 frente a 72 bytes).

En el handshake híbrido X25519MLKEM768 el key_share del cliente concatena las dos claves públicas.

$$32 + 1\,184 = 1\,216\ \text{bytes}$$

El servidor responde con su clave X25519 y el ciphertext de ML-KEM.

$$32 + 1\,088 = 1\,120\ \text{bytes}$$

El ClientHello crece algo más de un kilobyte, como reporta Chrome (O'Brien, 2023). La ventana inicial de TCP admite hasta 10 segmentos; unos 14 600 bytes (Chu et al., 2013). Un ClientHello de unos 1.7 KB y un ServerHello de unos 1.2 KB caben en esa ventana; el handshake no gana rondas. El único efecto común es que el ClientHello ya no cabe en un solo paquete de 1 500 bytes y algunos middleboxes mal implementados fallan con él.

La situación cambia al firmar la cadena con ML-DSA-65. Una cadena típica lleva dos claves públicas y dos firmas de certificado, más la firma del handshake.

$$2 \times 3\,309 + 2 \times 1\,952 + 3\,309 = 13\,831\ \text{bytes}$$

La misma estructura con ECDSA ocupa unos 346 bytes. Los 13.8 KB de autenticación, más el resto del flight del servidor y los sellos de transparencia de certificados, se acercan o superan los 14 600 bytes de la ventana inicial. En redes con pérdida de paquetes o alta latencia aparece una ronda adicional. Por eso la industria desplegó primero el intercambio de clave híbrido y dejó las firmas para después.

## 5. Decisión técnica — ¿Qué algoritmo NIST firma las prescripciones del Perfil A?

El análisis recomienda ML-DSA-65 como firma principal de las prescripciones. ML-KEM queda descartado de entrada: es un mecanismo de encapsulamiento de clave y no produce firmas (NIST, 2024a). La elección real está entre ML-DSA-65 y SLH-DSA-128s.

El volumen decide. Un hospital emite miles de prescripciones por día y el portal exige baja latencia. ML-DSA-65 firma con 3 309 bytes; SLH-DSA-128s con 7 856 bytes, 2.4 veces más. En tiempo de CPU la diferencia es mayor: con los datos de Westerbaan (2024), SLH-DSA-128s firma unas 1 700 veces más lento que ML-DSA-44 (8 000 frente a 4.8) y verifica 5.6 veces más lento (2.8 frente a 0.5).

El horizonte de 50 a 75 años no obliga a usar el esquema más conservador. La amenaza HNDL afecta la confidencialidad: un dato cifrado hoy puede leerse mañana. Una firma autentica quién emitió la prescripción y cuándo. Si algún día ML-DSA se debilita, el hospital vuelve a firmar o sella con marca de tiempo los documentos que deban seguir vigentes; nada del pasado queda expuesto.

El estudiante decide ML-DSA-65 para las prescripciones y SLH-DSA para la raíz de la PKI del hospital y los certificados de larga vida. Allí se firma poco y la diversidad criptográfica protege contra una falla de los retículos. La regla es usar la firma rápida para el volumen y la conservadora para la raíz.

## 6. Decisión técnica — ¿Modo híbrido permanente o etapa de transición para el Perfil B?

El análisis concluye que el Perfil B debe adoptar X25519MLKEM768 desde ahora y tratarlo como etapa de transición. El costo es bajo: 1 184 bytes más en el ClientHello y 1 088 en la respuesta, dentro de la ventana inicial de 14 600 bytes; el handshake no agrega rondas en el caso común. Chrome lo soporta desde la versión 116 (O'Brien, 2023). Activarlo en el CDN es un cambio de configuración, no un proyecto.

El beneficio es doble y los dos riesgos que cubre no están correlacionados. Si una computadora cuántica rompe X25519, ML-KEM protege la sesión. Si ML-KEM resulta tener una debilidad clásica, X25519 sigue protegiendo; Cloudflare cita el ataque de tiempo KyberSlash como ejemplo de esa clase de riesgo de implementación (Westerbaan, 2024). Varios candidatos post-cuánticos se rompieron en 2022 y 2023 con hardware barato (O'Brien, 2023). ML-KEM tiene pocos años de escrutinio frente a las décadas de las curvas elípticas.

El híbrido no debe ser permanente. Duplica código, superficie de ataque y bytes. Con datos de 5 a 7 años de sensibilidad, el Perfil B no tiene la urgencia del Perfil C. El estudiante decide mantener el híbrido hasta que ML-KEM acumule confianza y migrar a ML-KEM puro alrededor de 2033, la fecha que CNSA 2.0 fija para navegadores, servidores y nube (Elevate Consult, 2026). La regla es entrar temprano con el híbrido y salir tarde de él.

## Conclusiones

La computación cuántica no amenaza por igual a toda la criptografía. Shor elimina RSA, Diffie-Hellman y las curvas elípticas; Grover solo recorta el margen de AES y de SHA-2. La migración empieza por el intercambio de clave porque el ataque HNDL ya está en curso. Las firmas pueden esperar un poco más porque su riesgo empieza el día en que exista la máquina.

Los estándares NIST cubren las dos necesidades: ML-KEM para establecer claves; ML-DSA y SLH-DSA para firmar. El costo de la migración se mide en bytes: un kilobyte por handshake con ML-KEM y más de 13 KB por cadena de certificados con ML-DSA. El primero ya es invisible para el usuario; el segundo todavía exige ingeniería.

## Referencias

Chu, J., Dukkipati, N., Cheng, Y., & Mathis, M. (2013). *Increasing TCP's initial window* (RFC 6928). RFC Editor. https://www.rfc-editor.org/rfc/rfc6928

CISA, NSA, & NIST. (2023). *Quantum-readiness: Migration to post-quantum cryptography*. Cybersecurity and Infrastructure Security Agency. https://www.cisa.gov/resources-tools/resources/quantum-readiness-migration-post-quantum-cryptography

Elevate Consult. (2026, 13 de noviembre). *CNSA 2.0: What the NSA quantum-resistant suite means for defense contractors*. https://elevateconsult.com/?p=259389

National Institute of Standards and Technology. (2024a). *Module-lattice-based key-encapsulation mechanism standard* (FIPS 203). https://doi.org/10.6028/NIST.FIPS.203

National Institute of Standards and Technology. (2024b). *Module-lattice-based digital signature standard* (FIPS 204). https://doi.org/10.6028/NIST.FIPS.204

National Institute of Standards and Technology. (2024c). *Stateless hash-based digital signature standard* (FIPS 205). https://doi.org/10.6028/NIST.FIPS.205

O'Brien, D. (2023, 10 de agosto). *Protecting Chrome traffic with hybrid Kyber KEM*. Chromium Blog. https://blog.chromium.org/2023/08/protecting-chrome-traffic-with-hybrid.html

Westerbaan, B. (2024, 5 de marzo). *The state of the post-quantum Internet*. The Cloudflare Blog. https://blog.cloudflare.com/pq-2024/
