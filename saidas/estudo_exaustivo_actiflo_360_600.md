# Estudo Exaustivo e Reproduzível de Fundações — ACTIFLO 360 L/s e 600 L/s

> **Gerado 100% deterministicamente por `src/fundacao/relatorios/estudo_exaustivo.py`** a partir dos 9 furos SPT reais (`SP-01`..`SP-10`), ensaios de laboratório (`AI-01`..`AI-06`) e pranchas PBES/PBGE da ETA Vila C (SANEPAR — Foz do Iguaçu/PR).

## 1. Verificação Multi-Método (5 Métodos Brasileiros — Velloso & Lopes) por Diâmetro

Métodos avaliados até o topo da rocha impenetrável (`FS = 2,0`): **Aoki-Velloso (1975/97)**, **Décourt-Quaresma (1978/96)**, **Antunes-Cabral (1996)**, **Teixeira (1996)** e **Alonso (1996)**.

### 1.1 ACTIFLO 360 L/s (`SP-01` a `SP-04`, arrasamento `237,65 m`, rocha `225,1–227,6 m`)

| Diâmetro | $P_{\text{adm}}$ Média 5 Métodos (tf) | Pior Furo (tf) | Aoki | Décourt | Antunes | Teixeira | Alonso |
| :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Ø 40 cm** | **33.6** | 30.9 | 27.5 | 39.0 | 23.4 | 41.7 | 36.3 |
| **Ø 50 cm** | **44.3** | 41.1 | 37.7 | 50.4 | 29.7 | 54.6 | 49.2 |
| **Ø 60 cm** | **56.1** | 52.4 | 49.3 | 62.4 | 36.2 | 69.1 | 63.6 |
| **Ø 70 cm** | **68.9** | 64.8 | 62.3 | 75.1 | 42.9 | 84.7 | 79.6 |
| **Ø 80 cm** | **82.5** | 78.0 | 76.7 | 88.5 | 49.7 | 100.6 | 97.1 |

### 1.2 ACTIFLO 600 L/s (`SP-05` a `SP-10`, arrasamento `237,66 m`, rocha `223,1–224,3 m`)

| Diâmetro | $P_{\text{adm}}$ Média 5 Métodos (tf) | Pior Furo (tf) | Aoki | Décourt | Antunes | Teixeira | Alonso |
| :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Ø 40 cm** | **59.3** | 49.6 | 48.6 | 67.4 | 44.4 | 77.0 | 59.0 |
| **Ø 50 cm** | **78.2** | 65.8 | 66.8 | 87.5 | 56.3 | 102.3 | 78.1 |
| **Ø 60 cm** | **98.8** | 83.4 | 87.5 | 108.8 | 68.5 | 129.9 | 99.0 |
| **Ø 70 cm** | **120.9** | 102.5 | 110.6 | 131.4 | 81.0 | 159.9 | 121.7 |
| **Ø 80 cm** | **144.3** | 122.6 | 136.1 | 155.3 | 93.9 | 190.1 | 146.2 |

## 2. Análise de Confiabilidade Geotécnica (FORM Lognormal — ISO 2394 / JRC Eurocode 7)

Alvos da literatura (`Reliability Targets for Geotechnical Structures`): $\beta_T \ge 3{,}1$ (sistema redundante, $P_f \le 10^{-3}$) e $\beta_T \ge 3{,}8$ (CC2 / 50 anos, $P_f \le 7{,}2\times 10^{-5}$).

| Cenário | $R_{\text{ult}}$ médio (tf) | $S$ médio (tf) | $FS_{\text{méd}}$ | $COV_R$ | **$\beta$ (FORM)** | **$P_f$** | Diagnóstico |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |
| 360 PBGE atual — Ø40 em PC15/PC24 (42 tf), sem PCE | 67.1 | 39.9 | 1.68 | 0.23 | **2.02** | `2.19e-02` | INSUFICIENTE (β = 2.02 < 3.1 — revisar fundação ou comprovar ponta com PCE) |
| 360 PBGE atual — Ø50 em PC11 (55 tf), sem PCE | 88.7 | 52.2 | 1.70 | 0.23 | **2.07** | `1.93e-02` | INSUFICIENTE (β = 2.07 < 3.1 — revisar fundação ou comprovar ponta com PCE) |
| 360 Alternativa — Ø70 p/ 55 tf, sem PCE | 137.8 | 52.2 | 2.64 | 0.23 | **3.90** | `4.75e-05` | SEGURO (atende CC2/50a β ≥ 3.8) |
| 360 Alternativa — Ø70 p/ 55 tf, COM PCE (COV=0,12) | 137.8 | 52.2 | 2.64 | 0.13 | **5.95** | `1.32e-09` | SEGURO (atende CC2/50a β ≥ 3.8) |
| 360 Alternativa — Ø80 p/ 60 tf, COM PCE (COV=0,12) | 165.0 | 57.0 | 2.89 | 0.13 | **6.59** | `2.24e-11` | SEGURO (atende CC2/50a β ≥ 3.8) |
| 600 PBGE atual — Ø40 em P4/PC5 (49 tf), sem PCE | 118.5 | 46.5 | 2.55 | 0.25 | **3.42** | `3.08e-04` | ACEITÁVEL P/ SISTEMA REDUNDANTE (3.1 ≤ β < 3.8 — recomenda-se PCE) |
| 600 PBGE atual — Ø50 em PC59 (61 tf), sem PCE | 156.4 | 57.9 | 2.70 | 0.25 | **3.68** | `1.17e-04` | ACEITÁVEL P/ SISTEMA REDUNDANTE (3.1 ≤ β < 3.8 — recomenda-se PCE) |
| 600 PBGE atual — Ø50 em PC59 (61 tf), COM PCE (COV=0,12) | 156.4 | 57.9 | 2.70 | 0.17 | **5.14** | `1.37e-07` | SEGURO (atende CC2/50a β ≥ 3.8) |
| 600 Alternativa — Ø70 p/ 85 tf, COM PCE (COV=0,12) | 241.9 | 80.8 | 3.00 | 0.16 | **5.81** | `3.03e-09` | SEGURO (atende CC2/50a β ≥ 3.8) |

## 3. Avaliação Quantitativa de Vibração em Estacas Cravadas (Wiss / Woods-Jedele / DIN 4150-3 / NBR 9653)

| Estrutura Existente Vizinha | Distância (m) | Martelo (kJ) | **PPV est. (mm/s)** | Dist. Segura DIN (`5 mm/s`) | Dist. Segura NBR (`15 mm/s`) | Risco |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| Filtro Velho (Mód. 1) — ao sul do ACTIFLO 360 | 4.0 | 45 | **36.7** | 15.1 m | 7.3 m | ALTO — Excede DIN 4150-3 e NBR 9653 (alto risco de fissuração em tanques existentes) |
| Floculador Existente — a leste do ACTIFLO 360 | 6.0 | 45 | **20.0** | 15.1 m | 7.3 m | ALTO — Excede DIN 4150-3 e NBR 9653 (alto risco de fissuração em tanques existentes) |
| EE Lodo Existente — a oeste do ACTIFLO 360 | 12.0 | 45 | **7.1** | 15.1 m | 7.3 m | MODERADO/ALTO — Excede DIN 4150-3 para estruturas hidráulicas estanques |
| Tanque de Lodo / Filtros Adjacentes — colados ao ACTIFLO 600 | 3.5 | 45 | **44.8** | 15.1 m | 7.3 m | ALTO — Excede DIN 4150-3 e NBR 9653 (alto risco de fissuração em tanques existentes) |
| Filtro Velho (nega em basalto — transmissão Classe IV) | 4.0 | 45 | **85.0** | 26.4 m | 12.7 m | ALTO — Excede DIN 4150-3 e NBR 9653 (alto risco de fissuração em tanques existentes) |

## 4. Alternativa: Estacas de Maior Diâmetro (`Ø60–80 cm`) + Capitéis na Laje de Fundo (`h = 30 cm`, NBR 6118:2023)

| Cenário | Carga Projeto Capitel (tf) | Sem Capitel (`τ_sd / τ_Rd1` MPa) | **Capitel Mínimo (`L × L`, `h_total`)** | Rebaixo abaixo laje | `τ_sd (C'')` na laje 30 cm | Dispensa armadura punção? |
| :--- | ---: | :---: | :---: | ---: | ---: | :---: |
| ACTIFLO 360 — 22 estacas Ø60 cm (~58 tf/est) | 65 | `0.80 / 0.68` (PUNÇÃO) | **`90×90 cm`, `h = 45 cm`** | `+15 cm` | `0.59 MPa` | **SIM** |
| ACTIFLO 360 — 18 estacas Ø70 cm (~71 tf/est) | 75 | `0.86 / 0.68` (PUNÇÃO) | **`100×100 cm`, `h = 45 cm`** | `+15 cm` | `0.64 MPa` | **SIM** |
| ACTIFLO 360 — 15 estacas Ø80 cm (~85 tf/est) | 90 | `0.98 / 0.68` (PUNÇÃO) | **`130×130 cm`, `h = 45 cm`** | `+15 cm` | `0.66 MPa` | **SIM** |
| ACTIFLO 600 — 42 estacas Ø60 cm (~72 tf/est) | 80 | `0.98 / 0.68` (PUNÇÃO) | **`110×110 cm`, `h = 45 cm`** | `+15 cm` | `0.65 MPa` | **SIM** |
| ACTIFLO 600 — 34 estacas Ø70 cm (~89 tf/est) | 95 | `1.09 / 0.68` (PUNÇÃO) | **`140×140 cm`, `h = 45 cm`** | `+15 cm` | `0.66 MPa` | **SIM** |
| ACTIFLO 600 — 28 estacas Ø80 cm (~108 tf/est) | 115 | `1.25 / 0.68` (PUNÇÃO) | **`190×190 cm`, `h = 45 cm`** | `+15 cm` | `0.65 MPa` | **SIM** |

## 5. Interação Solo–Laje–Estaca: Radier Estaqueado (Método PDR — Poulos, Davis & Randolph)

| Cenário | Estacas / Ø | Carga Radier (%) | Carga Estacas (%) | Média/Estaca (tf) | Recalque Radier Isolado (mm) | **Recalque PDR (mm)** | Redução | ELS ≤ 25 mm |
| :--- | :---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| ACTIFLO 360 — PBGE atual (39 est Ø40, L=11,5m) | 39× Ø40 | 2.3% | 97.7% | 31.8 | 163.3 | **9.4** | 94.2% | **SIM** |
| ACTIFLO 360 — Otimizado Capitéis (18 est Ø70, L=11,5m) | 18× Ø70 | 2.9% | 97.1% | 68.5 | 163.3 | **11.6** | 92.9% | **SIM** |
| ACTIFLO 360 — Otimizado Capitéis (15 est Ø80, L=11,5m) | 15× Ø80 | 3.1% | 96.9% | 82.0 | 163.3 | **12.2** | 92.5% | **SIM** |
| ACTIFLO 600 — PBGE atual (87 est Ø40, L=13,5m) | 87× Ø40 | 1.2% | 98.8% | 34.3 | 286.0 | **9.1** | 96.8% | **SIM** |
| ACTIFLO 600 — Otimizado Capitéis (42 est Ø60, L=13,5m) | 42× Ø60 | 1.6% | 98.4% | 70.8 | 286.0 | **10.8** | 96.2% | **SIM** |
| ACTIFLO 600 — Otimizado Capitéis (34 est Ø70, L=13,5m) | 34× Ø70 | 1.7% | 98.3% | 87.4 | 286.0 | **11.3** | 96.0% | **SIM** |
| ACTIFLO 600 — Otimizado Capitéis (28 est Ø80, L=13,5m) | 28× Ø80 | 1.8% | 98.2% | 106.1 | 286.0 | **11.9** | 95.8% | **SIM** |

## 6. Eficiência e Recalque de Grupo (Converse-Labarre & Sapata Equivalente a 2L/3)

- **ACTIFLO 360 (grupo PBGE ~4×10 Ø40):** $\eta_{CL} = 0.793$, recalque elástico fuste `0.6 mm` + solo abaixo de $2L/3$ `10.0 mm` = **`10.7 mm`**.
- **ACTIFLO 600 (grupo PBGE ~8×11 Ø40):** $\eta_{CL} = 0.786$, recalque elástico fuste `0.8 mm` + solo abaixo de $2L/3$ `7.2 mm` = **`8.0 mm`**.
