# Comparativo Técnico-Econômico e Contratual Determinístico — ACTIFLO 360 e 600

> **Base paramétrica:** `SINAPI/PR + Mercado Fundações PR (referencial paramétrico sem BDI)` (sobreconsumo Hélice = **`20%`**). Todos os valores de $\beta$ (FORM), comprimento armado ($2{,}5\cdot T$) e reforço de flexão na laje de 30 cm (NBR 6118 contra malha PBES) são **100% calculados deterministicamente em Python — zero constante arbitrada**.

## 1. ACTIFLO 360 L/s — Original PBGE vs. Alternativas

| Cód. | Solução | Estacas (m) | Gaiola (m) | Concreto Total (m³) | Aço Total (kg) | **Custo Est. (R$)** | **Δ vs. Original** | **$\beta$ FORM** | Seguro? |
| :--- | :--- | :---: | :---: | ---: | ---: | ---: | ---: | ---: | :---: |
| `360-S0` | Original PBGE/PBES (como licitado: 33×Ø40 + 6×Ø50, C30) | 39 (523 m) | 6.0 | **102.1** | 2,808 | **R$ 185,425** | **BASE** | `2.07` | **NÃO** |
| `360-S1` | PBGE Corrigido c/ PCE (33×Ø40 + 6×Ø50 até rocha, blocos 80×80, C40) | 39 (432 m) | 6.0 | **87.2** | 2,838 | **R$ 213,341** | **+15.1%** | `3.16` | SIM |
| `360-S2` | Reforço Tradicional (42×Ø50 cm até rocha, blocos 80×80/80×210, C40 + 1 PCE) | 42 (483 m) | 6.0 | **133.0** | 3,978 | **R$ 273,481** | **+47.5%** | `5.38` | SIM |
| `360-S3` | Otimizado Capitéis: 22×Ø60 cm (L=11,5 m) + Capitéis 90×90 (h=45) + 1 PCE | 22 (253 m) | 6.0 | **88.5** | 2,744 | **R$ 216,159** | **+16.6%** | `4.32` | SIM |
| `360-S4` | Otimizado Capitéis: 18×Ø70 cm (L=11,5 m) + Capitéis 100×100 (h=45) + 1 PCE | 18 (207 m) | 6.5 | **98.3** | 2,954 | **R$ 225,981** | **+21.9%** | `4.38` | SIM |
| `360-S5` | Radier Direto + Troca Total Solo-Cimento (3,3 m) | 0 (0 m) | 0.0 | **0.0** | 1,740 | **R$ 239,809** | **+29.3%** | `6.01` | SIM |

### Detalhamento de Custos e Enquadramento Contratual

- **`360-S0` — Original PBGE/PBES (como licitado: 33×Ø40 + 6×Ø50, C30):** Perfuração `R$ 51,935` · Concreto est. `R$ 46,710` · Aço est. `R$ 21,439` · Blocos/Cap./ΔLaje `R$ 34,541` (ΔAço laje `0 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 30,800` · $P_f = 1.94e-02$.
  - *Enquadramento:* Base contratual (NÃO executável sem revisão: 6 blocos Ø50 fora da NBR 6122, ponta na rocha e β insuficiente).
  - *Síntese:* 523 m teóricos (trava na rocha em ~430 m); β calculado em solo sem PCE abaixo de 3,1.
- **`360-S1` — PBGE Corrigido c/ PCE (33×Ø40 + 6×Ø50 até rocha, blocos 80×80, C40):** Perfuração `R$ 42,765` · Concreto est. `R$ 44,728` · Aço est. `R$ 21,439` · Blocos/Cap./ΔLaje `R$ 35,609` (ΔAço laje `0 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 68,800` · $P_f = 7.92e-04$.
  - *Enquadramento:* Comunicação técnica + PCE prévia (SE PCE falhar na ponta em rocha, exige aditivo p/ S2 ou S3/S4).
  - *Síntese:* Mesmo com PCE (COV=0,12), em solo puro sem ganho de ponta rochosa β permanece próximo ao limite.
- **`360-S2` — Reforço Tradicional (42×Ø50 cm até rocha, blocos 80×80/80×210, C40 + 1 PCE):** Perfuração `R$ 57,960` · Concreto est. `R$ 71,697` · Aço est. `R$ 31,972` · Blocos/Cap./ΔLaje `R$ 42,702` (ΔAço laje `0 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 69,150` · $P_f = 3.63e-08$.
  - *Enquadramento:* Pleito/Aditivo de escopo justificável (reforço exigido pela baixa NSPT + rocha rasa em SP-01..04).
  - *Síntese:* Atende com folga sem depender de ponta em rocha, mas eleva concreto e blocos (+47%).
- **`360-S3` — Otimizado Capitéis: 22×Ø60 cm (L=11,5 m) + Capitéis 90×90 (h=45) + 1 PCE:** Perfuração `R$ 39,215` · Concreto est. `R$ 54,080` · Aço est. `R$ 25,685` · Blocos/Cap./ΔLaje `R$ 12,080` (ΔAço laje `435 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 85,100` · $P_f = 7.84e-06$.
  - *Enquadramento:* Alternativa de Engenharia de Valor / Aditivo otimizado (malha PBES Ø10 c/12 já absorve flexão no vão!).
  - *Síntese:* Menos concreto total que PBGE, metade das perfurações e alta confiabilidade com PCE.
- **`360-S4` — Otimizado Capitéis: 18×Ø70 cm (L=11,5 m) + Capitéis 100×100 (h=45) + 1 PCE:** Perfuração `R$ 40,365` · Concreto est. `R$ 60,225` · Aço est. `R$ 28,282` · Blocos/Cap./ΔLaje `R$ 12,009` (ΔAço laje `435 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 85,100` · $P_f = 5.89e-06$.
  - *Enquadramento:* Alternativa de Engenharia de Valor / Aditivo otimizado.
  - *Síntese:* Corta perfurações em 54%, mas Ø70 exige mais concreto/estaca e gaiola mais longa (T maior).
- **`360-S5` — Radier Direto + Troca Total Solo-Cimento (3,3 m):** Perfuração `R$ 0` · Concreto est. `R$ 0` · Aço est. `R$ 0` · Blocos/Cap./ΔLaje `R$ 21,750` (ΔAço laje `1740 kg`) · Terra/Solo-cim. `R$ 200,059` · Mob.+Ensaios `R$ 18,000` · $P_f = 9.14e-10$.
  - *Enquadramento:* Alteração de concepção (requer aprovação SANEPAR/fornecedor ACTIFLO + revalidação radier).
  - *Síntese:* Elimina 39 estacas e 30 blocos; escava e substitui 610 m³ até o silte rijo (recalque ~0,9 cm, acima do N.A.).

## 2. ACTIFLO 600 L/s — Original PBGE vs. Alternativas

| Cód. | Solução | Estacas (m) | Gaiola (m) | Concreto Total (m³) | Aço Total (kg) | **Custo Est. (R$)** | **Δ vs. Original** | **$\beta$ FORM** | Seguro? |
| :--- | :--- | :---: | :---: | ---: | ---: | ---: | ---: | ---: | :---: |
| `600-S0` | Original PBGE/PBES (como licitado: 83×Ø40 + 4×Ø50, C30) | 87 (1111 m) | 6.0 | **202.6** | 4,879 | **R$ 338,915** | **BASE** | `3.42` | SIM |
| `600-S1a` | PBGE Corrigido C30 + 1 PCE (83×Ø40 + 4×Ø50 até rocha, 4 blocos 80×80) | 87 (1092 m) | 6.0 | **199.9** | 4,899 | **R$ 374,046** | **+10.4%** | `4.75` | SIM |
| `600-S1b` | PBGE Corrigido C40 + 1 PCE (se SANEPAR exigir C40 CAA IV nas estacas) | 87 (1092 m) | 6.0 | **199.9** | 4,899 | **R$ 389,272** | **+14.9%** | `4.75` | SIM |
| `600-S2` | Otimizado Perfuratriz Leve: 52×Ø50 cm (L=13 m) + Capitéis 95×95 (h=45) + 1 PCE | 52 (676 m) | 6.0 | **166.3** | 4,931 | **R$ 307,556** | **-9.3%** | `5.05` | SIM |
| `600-S3` | Otimizado Capitéis: 42×Ø60 cm (L=13,5 m) + Capitéis 110×110 (h=45) + 1 PCE | 42 (567 m) | 6.0 | **200.0** | 6,070 | **R$ 362,976** | **+7.1%** | `5.14` | SIM |
| `600-S4` | Otimizado Capitéis: 34×Ø70 cm (L=13,5 m) + Capitéis 140×140 (h=45) + 1 PCE | 34 (459 m) | 6.0 | **222.0** | 7,562 | **R$ 395,086** | **+16.6%** | `5.22` | SIM |

### Detalhamento de Custos e Enquadramento Contratual

- **`600-S0` — Original PBGE/PBES (como licitado: 83×Ø40 + 4×Ø50, C30):** Perfuração `R$ 106,945` · Concreto est. `R$ 93,034` · Aço est. `R$ 45,479` · Blocos/Cap./ΔLaje `R$ 59,158` (ΔAço laje `0 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 34,300` · $P_f = 3.09e-04$.
  - *Enquadramento:* Base contratual (geotecnicamente viável, mas exige corrigir 4 blocos Ø50 e cota de 7 estacas de 16 m).
  - *Síntese:* 1.111 m previstos; 85 blocos de 70 cm (170 m² de fôrma); confiabilidade aceitável sem PCE.
- **`600-S1a` — PBGE Corrigido C30 + 1 PCE (83×Ø40 + 4×Ø50 até rocha, 4 blocos 80×80):** Perfuração `R$ 105,042` · Concreto est. `R$ 91,354` · Aço est. `R$ 45,479` · Blocos/Cap./ΔLaje `R$ 59,870` (ΔAço laje `0 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 72,300` · $P_f = 1.03e-06$.
  - *Enquadramento:* Menor atrito contratual (correção pontual de compatibilização + PCE).
  - *Síntese:* Mantém C30 nas estacas (se CAA solo ≤ III), ajusta 4 blocos p/ 80×80 e valida com PCE.
- **`600-S1b` — PBGE Corrigido C40 + 1 PCE (se SANEPAR exigir C40 CAA IV nas estacas):** Perfuração `R$ 105,042` · Concreto est. `R$ 106,580` · Aço est. `R$ 45,479` · Blocos/Cap./ΔLaje `R$ 59,870` (ΔAço laje `0 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 72,300` · $P_f = 1.03e-06$.
  - *Enquadramento:* Aditivo justificável pela divergência de edital (PBGE C30 vs. PBES C40/CAA IV).
  - *Síntese:* Quantifica exatamente o impacto do upgrade C30→C40 nas 87 estacas.
- **`600-S2` — Otimizado Perfuratriz Leve: 52×Ø50 cm (L=13 m) + Capitéis 95×95 (h=45) + 1 PCE:** Perfuração `R$ 81,120` · Concreto est. `R$ 86,011` · Aço est. `R$ 39,585` · Blocos/Cap./ΔLaje `R$ 30,990` (ΔAço laje `1095 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 69,850` · $P_f = 2.18e-07$.
  - *Enquadramento:* Engenharia de Valor — REDUZ CUSTO mantendo equipamento leve (Ø50) e eliminando 85 blocos!.
  - *Síntese:* 52 estacas (676 m, -39% perfuração), -36 m³ de concreto total e malha PBES Ø10 c/14 quase sem reforço!
- **`600-S3` — Otimizado Capitéis: 42×Ø60 cm (L=13,5 m) + Capitéis 110×110 (h=45) + 1 PCE:** Perfuração `R$ 87,885` · Concreto est. `R$ 103,884` · Aço est. `R$ 49,035` · Blocos/Cap./ΔLaje `R$ 36,021` (ΔAço laje `1423 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 86,150` · $P_f = 1.41e-07$.
  - *Enquadramento:* Engenharia de Valor — avalia 42 estacas Ø60 vs. perfuratriz pesada e concreto.
  - *Síntese:* 567 m (-49% perfuração), volume de concreto similar ao PBGE, porém exige equipamento pesado.
- **`600-S4` — Otimizado Capitéis: 34×Ø70 cm (L=13,5 m) + Capitéis 140×140 (h=45) + 1 PCE:** Perfuração `R$ 89,505` · Concreto est. `R$ 114,465` · Aço est. `R$ 49,172` · Blocos/Cap./ΔLaje `R$ 56,493` (ΔAço laje `2678 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 85,450` · $P_f = 8.88e-08$.
  - *Enquadramento:* Alternativa de mínimo nº de furos (34 estacas), porém com maior volume de concreto e equipamento pesado.
  - *Síntese:* 459 m (-59% perfuração), mas maior volume de concreto e maior reforço de flexão na laje.
