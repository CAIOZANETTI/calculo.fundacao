# Memorial de Verificação de Fundações — ACTIFLO 600 L/s (Filtro de Areia)

- **Empreendimento:** SANEPAR — SAA Foz do Iguaçu (PR) — ETA Vila C
- **Referência PBES:** `001-SAA-0017-8820-PBES-DE-0000ACT01FORMA-R0`
- **Concreto / Durabilidade:** C40 (`fck = 40 MPa`, CAA IV, cobrimento `4.5 cm`)
- **Estacas:** Hélice Contínua Ø `40 cm` (embutimento `5 cm`), $P_{\text{adm}}$ adotada = **55.0 tf**

## 1. Resumo Geral do Carregamento e Alocação

| Indicador | Valor |
| :--- | ---: |
| Total de pontos de carga | 85 |
| Carga vertical característica total ($\sum N_k$) | 3,023.0 tf |
| Blocos de 1 estaca (PBES) | 83 |
| Blocos de 2 estacas (PBES) | 2 |
| Total de estacas (PBES) | 87 |
| Total de estacas recalculado ($P_{\text{adm}} = 55.0$ tf) | 88 |
| Ponto mais carregado (1 estaca) | PC59 (61 tf) |
| Ponto mais carregado (2 estacas) | PC8 (68 tf) |
| Máxima carga atuante por estaca (PBES) | 61.0 tf |
| Pontos que excedem $P_{\text{adm}}$ no PBES | **1** |

### ⚠️ Pontos de Carga Acima da Capacidade Admissível Adotada

| Ponto | $N_k$ (tf) | Estacas PBES | Carga/Estaca (tf) | Estacas Necessárias | Observação |
| :--- | ---: | :---: | ---: | :---: | :--- |
| `PC59` | 61.0 | 1 | 61.0 | 2 | Carga/estaca (61.0 tf) > P_adm (55.0 tf); requer 2 estaca(s) em vez de 1. |

## 2. Verificação Estrutural da Estaca (Fuste)

- **Seção:** Ø `40 cm` ($A_c = 1256.6\text{ cm}^2$)
- **Tensão média atuante máxima:** `4.76 MPa` (para `61.0 tf`) vs. limite adotado `6.00 MPa` (`76.9 tf`)
- **Taxa de utilização à compressão:** `79.3%` — **APROVADO**
- **Armadura longitudinal mínima (0,4%):** `5.03 cm²` → Sugestão: `7 Ø 10 mm (As = 5.50 cm²)` (mín. `4.0 m`)

## 3. Verificação Estrutural dos Blocos sobre Estacas

### 3.1 Bloco de 1 Estaca (`70×70×70 cm`) — Caso Crítico ($N_k = 61.0$ tf)

- **Folga à borda:** `15.0 cm` (mín. 15,0 cm) — OK
- **Tensão de contato pilar / estaca:** `9.31 MPa` / `6.66 MPa` (limite $f_{cd1} = 20.40$ MPa) — OK
- **Fendimento transversal:** $F_{td} = 119.6$ kN → $A_{s,\text{req}} = 2.75\text{ cm}^2$ vs. adotado `3.74 cm²` — **APROVADO**

### 3.2 Bloco de 2 Estacas (`70×190×70 cm`, $e = 120$ cm) — Bielas e Tirantes

| Verificação | Caso Crítico PBES | Capacidade Cheia ($2\cdot P_{\text{adm}}$) | Limite / Adotado |
| :--- | ---: | ---: | ---: |
| Carga característica $N_k$ (tf) | 68.0 | 110.0 | — |
| Altura útil $d$ (cm) / Ângulo $\theta$ | 63.4 cm / 50.4° | 63.4 cm / 50.4° | 45°–55° (Blévot) |
| Tração no tirante $R_{sd,\text{Blévot}}$ (kN) | 444.5 | 719.1 | — |
| Armadura requerida $A_{s,\text{Blévot}}$ (cm²) | 10.22 | 16.54 | **24.13 cm²** (12 Ø 16) |
| Tensão nó pilar CCC $\sigma_{cd,p}$ (MPa) | 7.49 | 12.12 | $f_{cd1} = 20.40$ MPa |
| Tensão nó estaca CCT $\sigma_{cd,e}$ (MPa) | 6.26 | 10.13 | $f_{cd2} = 14.40$ MPa |
| Ancoragem $l_{b,\text{nec}}$ com gancho (cm) | 16.0 | 21.1 | disp. `90.5 cm` |
| Status | **APROVADO** | **APROVADO** | — |

## 4. Pré-Dimensionamento Geotécnico por Cota de Arrasamento

| Cota Arrasamento (m) | Compr. Recomendado $L$ (m) | Cota Ponta (m) | $P_{\text{adm,mín}}$ (tf) | $P_{\text{adm,média}}$ (tf) | Tração Adm. (tf) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 235.562 | *Não atingiu na sondagem* | — | — | — | — |
| 235.812 | *Não atingiu na sondagem* | — | — | — | — |
| 236.662 | *Não atingiu na sondagem* | — | — | — | — |
| 237.472 | *Não atingiu na sondagem* | — | — | — | — |
| 237.662 | *Não atingiu na sondagem* | — | — | — | — |

## 5. Quantitativos dos Blocos (Calculado vs. Resumo PBES)

| Item | Calculado (Geometria Blocos) | Resumo PBES (Pranchas) |
| :--- | ---: | ---: |
| Volume de concreto dos blocos (m³) | 30.33 | 30.35 |
| Área lateral de fôrmas dos blocos (m²) | 169.96 | 170.00 |
| Aço CA-50 nos blocos — total (kg) | 1240.6 | — |
| Taxa média de aço nos blocos (kg/m³) | 40.9 | — |

*Detalhamento do aço nos blocos por bitola:* Ø6,3 = `1058.5 kg` | Ø8,0 = `68.8 kg` | Ø16,0 = `113.3 kg`.

## 6. Estudo de Sensibilidade ($P_{\text{adm}}$ vs. Quantidade de Estacas)

| $P_{\text{adm}}$ (tf/estaca) | Blocos 1 Est. | Blocos 2 Est. | Blocos 3+ Est. | Total Estacas | Carga Média/Estaca (tf) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 45 | 72 | 13 | 0 | **98** | 30.9 |
| 50 | 79 | 6 | 0 | **91** | 33.2 |
| 55 | 82 | 3 | 0 | **88** | 34.4 |
| 60 | 82 | 3 | 0 | **88** | 34.4 |
| 65 | 83 | 2 | 0 | **87** | 34.8 |
| 70 | 85 | 0 | 0 | **85** | 35.6 |
| 75 | 85 | 0 | 0 | **85** | 35.6 |
