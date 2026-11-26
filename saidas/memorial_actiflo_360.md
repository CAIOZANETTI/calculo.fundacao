# Memorial de Verificação de Fundações — ACTIFLO 360 L/s (Filtro de Areia)

- **Empreendimento:** SANEPAR — SAA Foz do Iguaçu (PR) — ETA Vila C
- **Referência PBES:** `001-SAA-0017-8820-PBES-DE-0000ACT02FORMA-R0`
- **Concreto / Durabilidade:** C40 (`fck = 40 MPa`, CAA IV, cobrimento `4.5 cm`)
- **Estacas:** Hélice Contínua Ø `40 cm` (embutimento `5 cm`), $P_{\text{adm}}$ adotada = **55.0 tf**

## 1. Resumo Geral do Carregamento e Alocação

| Indicador | Valor |
| :--- | ---: |
| Total de pontos de carga | 30 |
| Carga vertical característica total ($\sum N_k$) | 1,270.0 tf |
| Blocos de 1 estaca (PBES) | 21 |
| Blocos de 2 estacas (PBES) | 9 |
| Total de estacas (PBES) | 39 |
| Total de estacas recalculado ($P_{\text{adm}} = 55.0$ tf) | 39 |
| Ponto mais carregado (1 estaca) | PC11 (55 tf) |
| Ponto mais carregado (2 estacas) | PC22 (71 tf) |
| Máxima carga atuante por estaca (PBES) | 55.0 tf |
| Pontos que excedem $P_{\text{adm}}$ no PBES | **0** |

## 2. Verificação Estrutural da Estaca (Fuste)

- **Seção:** Ø `40 cm` ($A_c = 1256.6\text{ cm}^2$)
- **Tensão média atuante máxima:** `4.29 MPa` (para `55.0 tf`) vs. limite adotado `6.00 MPa` (`76.9 tf`)
- **Taxa de utilização à compressão:** `71.5%` — **APROVADO**
- **Armadura longitudinal mínima (0,4%):** `5.03 cm²` → Sugestão: `7 Ø 10 mm (As = 5.50 cm²)` (mín. `4.0 m`)

## 3. Verificação Estrutural dos Blocos sobre Estacas

### 3.1 Bloco de 1 Estaca (`70×70×70 cm`) — Caso Crítico ($N_k = 55.0$ tf)

- **Folga à borda:** `15.0 cm` (mín. 15,0 cm) — OK
- **Tensão de contato pilar / estaca:** `8.39 MPa` / `6.01 MPa` (limite $f_{cd1} = 20.40$ MPa) — OK
- **Fendimento transversal:** $F_{td} = 107.9$ kN → $A_{s,\text{req}} = 2.48\text{ cm}^2$ vs. adotado `3.74 cm²` — **APROVADO**

### 3.2 Bloco de 2 Estacas (`70×190×70 cm`, $e = 120$ cm) — Bielas e Tirantes

| Verificação | Caso Crítico PBES | Capacidade Cheia ($2\cdot P_{\text{adm}}$) | Limite / Adotado |
| :--- | ---: | ---: | ---: |
| Carga característica $N_k$ (tf) | 71.0 | 110.0 | — |
| Altura útil $d$ (cm) / Ângulo $\theta$ | 63.4 cm / 50.4° | 63.4 cm / 50.4° | 45°–55° (Blévot) |
| Tração no tirante $R_{sd,\text{Blévot}}$ (kN) | 464.1 | 719.1 | — |
| Armadura requerida $A_{s,\text{Blévot}}$ (cm²) | 10.68 | 16.54 | **24.13 cm²** (12 Ø 16) |
| Tensão nó pilar CCC $\sigma_{cd,p}$ (MPa) | 7.82 | 12.12 | $f_{cd1} = 20.40$ MPa |
| Tensão nó estaca CCT $\sigma_{cd,e}$ (MPa) | 6.54 | 10.13 | $f_{cd2} = 14.40$ MPa |
| Ancoragem $l_{b,\text{nec}}$ com gancho (cm) | 16.0 | 21.1 | disp. `90.5 cm` |
| Status | **APROVADO** | **APROVADO** | — |

## 4. Pré-Dimensionamento Geotécnico por Cota de Arrasamento

> ⚠️ **ATENÇÃO:** Calculado com perfil de sondagem **HIPOTÉTICO** (substituir pelos laudos SPT reais do `2. PBGE`).

| Cota Arrasamento (m) | Compr. Recomendado $L$ (m) | Cota Ponta (m) | $P_{\text{adm,mín}}$ (tf) | $P_{\text{adm,média}}$ (tf) | Tração Adm. (tf) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 237.150 | 11.0 | 226.150 | 42.3 | 68.7 | 20.9 |
| 237.450 | 11.0 | 226.450 | 40.7 | 66.9 | 19.7 |
| 237.650 | 11.0 | 226.650 | 39.6 | 65.7 | 18.8 |
| 239.150 | 13.0 | 226.150 | 44.0 | 71.0 | 22.0 |

## 5. Quantitativos dos Blocos (Calculado vs. Resumo PBES)

| Item | Calculado (Geometria Blocos) | Resumo PBES (Pranchas) |
| :--- | ---: | ---: |
| Volume de concreto dos blocos (m³) | 15.58 | 15.60 |
| Área lateral de fôrmas dos blocos (m²) | 73.92 | 73.95 |
| Aço CA-50 nos blocos — total (kg) | 1092.6 | — |
| Taxa média de aço nos blocos (kg/m³) | 70.1 | — |

*Detalhamento do aço nos blocos por bitola:* Ø6,3 = `273.2 kg` | Ø8,0 = `309.7 kg` | Ø16,0 = `509.7 kg`.

## 6. Estudo de Sensibilidade ($P_{\text{adm}}$ vs. Quantidade de Estacas)

| $P_{\text{adm}}$ (tf/estaca) | Blocos 1 Est. | Blocos 2 Est. | Blocos 3+ Est. | Total Estacas | Carga Média/Estaca (tf) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 45 | 16 | 14 | 0 | **44** | 28.9 |
| 50 | 17 | 13 | 0 | **43** | 29.5 |
| 55 | 21 | 9 | 0 | **39** | 32.6 |
| 60 | 23 | 7 | 0 | **37** | 34.3 |
| 65 | 25 | 5 | 0 | **35** | 36.3 |
| 70 | 28 | 2 | 0 | **32** | 39.7 |
| 75 | 30 | 0 | 0 | **30** | 42.3 |
