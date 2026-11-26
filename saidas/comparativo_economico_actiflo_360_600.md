# Comparativo Técnico-Econômico e Contratual das Soluções — ACTIFLO 360 e 600

> **Base paramétrica:** `SINAPI/PR + Mercado Fundações PR (referencial paramétrico sem BDI)` (sobreconsumo de concreto na Hélice Contínua = **`20%`**). Os valores absolutos em `R$` servem para comparação relativa entre soluções; basta editar `projetos/precos_unitarios_sinapi_pr.yaml` com os preços exatos do contrato SANEPAR para gerar o orçamento executivo e o pleito formal.

## 1. ACTIFLO 360 L/s — Original PBGE vs. Alternativas

| Cód. | Solução | Estacas / Metragem | Concreto Estacas (m³) | Concreto Blocos/Cap. (m³) | **Concreto Total (m³)** | **Aço Total (kg)** | **Custo Est. (R$)** | **Δ vs. Original** | $\beta$ | Seguro? |
| :--- | :--- | :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| `360-S0` | Original PBGE/PBES (como licitado: 33×Ø40 + 6×Ø50, C30) | 39 (523 m) | 86.5 | 15.6 | **102.1** | 2,808 | **R$ 185,425** | **BASE** | 2.02 | **NÃO** |
| `360-S1` | PBGE Corrigido c/ PCE (33×Ø40 + 6×Ø50 até rocha, blocos 80×80, C40) | 39 (432 m) | 71.0 | 16.2 | **87.2** | 2,838 | **R$ 213,341** | **+15.1%** | 2.65 | **NÃO** |
| `360-S2` | Reforço Tradicional (42×Ø50 cm até rocha, blocos 80×80/80×210, C40 + 1 PCE) | 42 (483 m) | 113.8 | 19.2 | **133.0** | 3,978 | **R$ 273,481** | **+47.5%** | 3.95 | SIM |
| `360-S3` | Otimizado Capitéis: 22×Ø60 cm (L=11,5 m) + Capitéis 90×90 (h=45) + 1 PCE | 22 (253 m) | 85.8 | 2.7 | **88.5** | 3,288 | **R$ 222,962** | **+20.2%** | 4.35 | SIM |
| `360-S4` | Otimizado Capitéis: 18×Ø70 cm (L=11,5 m) + Capitéis 100×100 (h=45) + 1 PCE | 18 (207 m) | 95.6 | 2.7 | **98.3** | 3,886 | **R$ 237,631** | **+28.2%** | 5.95 | SIM |
| `360-S5` | Radier Direto + Troca Total Solo-Cimento (3,3 m) | 0 (0 m) | 0.0 | 0.0 | **0.0** | 1,740 | **R$ 239,809** | **+29.3%** | 3.80 | SIM |

### Detalhamento de Custos e Enquadramento Contratual

- **`360-S0` — Original PBGE/PBES (como licitado: 33×Ø40 + 6×Ø50, C30):** Perfuração `R$ 51,935` · Concreto est. `R$ 46,710` · Aço est. `R$ 21,439` · Blocos/Cap./ΔLaje `R$ 34,541` (ΔAço laje `0 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 30,800`.
  - *Enquadramento:* Base contratual (NÃO executável sem revisão: 6 blocos Ø50 fora da NBR 6122, ponta na rocha e β=2,02).
  - *Síntese:* 523 m teóricos (trava na rocha em ~430 m); β=2,02–2,07 insuficiente em solo sem PCE.
- **`360-S1` — PBGE Corrigido c/ PCE (33×Ø40 + 6×Ø50 até rocha, blocos 80×80, C40):** Perfuração `R$ 42,765` · Concreto est. `R$ 44,728` · Aço est. `R$ 21,439` · Blocos/Cap./ΔLaje `R$ 35,609` (ΔAço laje `0 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 68,800`.
  - *Enquadramento:* Comunicação técnica + PCE prévia (SE PCE falhar na ponta em rocha, exige aditivo p/ S2 ou S3/S4).
  - *Síntese:* Menor alteração geométrica; depende 100% de a PCE comprovar ponta de ~55 tf no topo do basalto.
- **`360-S2` — Reforço Tradicional (42×Ø50 cm até rocha, blocos 80×80/80×210, C40 + 1 PCE):** Perfuração `R$ 57,960` · Concreto est. `R$ 71,697` · Aço est. `R$ 31,972` · Blocos/Cap./ΔLaje `R$ 42,702` (ΔAço laje `0 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 69,150`.
  - *Enquadramento:* Pleito/Aditivo de escopo justificável (reforço exigido pela baixa NSPT + rocha rasa em SP-01..04).
  - *Síntese:* Atende com folga sem depender de ponta duvidosa, mas aumenta volume de concreto e blocos.
- **`360-S3` — Otimizado Capitéis: 22×Ø60 cm (L=11,5 m) + Capitéis 90×90 (h=45) + 1 PCE:** Perfuração `R$ 39,215` · Concreto est. `R$ 54,080` · Aço est. `R$ 25,685` · Blocos/Cap./ΔLaje `R$ 18,882` (ΔAço laje `979 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 85,100`.
  - *Enquadramento:* Alternativa de Engenharia de Valor / Aditivo otimizado (requer revisão estrutural da laje de fundo).
  - *Síntese:* Menos perfurações (-44%) e sem blocos de 70 cm; atende β > 4,3 com PCE.
- **`360-S4` — Otimizado Capitéis: 18×Ø70 cm (L=11,5 m) + Capitéis 100×100 (h=45) + 1 PCE:** Perfuração `R$ 40,365` · Concreto est. `R$ 60,225` · Aço est. `R$ 26,032` · Blocos/Cap./ΔLaje `R$ 25,909` (ΔAço laje `1547 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 85,100`.
  - *Enquadramento:* Alternativa de Engenharia de Valor / Aditivo otimizado (altíssima segurança β=5,95).
  - *Síntese:* Corta perfurações em 54%, mas Ø70 exige perfuratriz pesada + mais concreto/estaca.
- **`360-S5` — Radier Direto + Troca Total Solo-Cimento (3,3 m):** Perfuração `R$ 0` · Concreto est. `R$ 0` · Aço est. `R$ 0` · Blocos/Cap./ΔLaje `R$ 21,750` (ΔAço laje `1740 kg`) · Terra/Solo-cim. `R$ 200,059` · Mob.+Ensaios `R$ 18,000`.
  - *Enquadramento:* Alteração de concepção (requer aprovação SANEPAR/fornecedor ACTIFLO + revalidação radier).
  - *Síntese:* Elimina 39 estacas e 30 blocos; escava e substitui 610 m³ até o silte rijo (recalque ~0,9 cm, acima do N.A.).

## 2. ACTIFLO 600 L/s — Original PBGE vs. Alternativas

| Cód. | Solução | Estacas / Metragem | Concreto Estacas (m³) | Concreto Blocos/Cap. (m³) | **Concreto Total (m³)** | **Aço Total (kg)** | **Custo Est. (R$)** | **Δ vs. Original** | $\beta$ | Seguro? |
| :--- | :--- | :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: |
| `600-S0` | Original PBGE/PBES (como licitado: 83×Ø40 + 4×Ø50, C30) | 87 (1111 m) | 172.3 | 30.3 | **202.6** | 4,879 | **R$ 338,915** | **BASE** | 3.42 | SIM |
| `600-S1a` | PBGE Corrigido C30 + 1 PCE (83×Ø40 + 4×Ø50 até rocha, 4 blocos 80×80) | 87 (1092 m) | 169.2 | 30.8 | **199.9** | 4,899 | **R$ 374,046** | **+10.4%** | 5.14 | SIM |
| `600-S1b` | PBGE Corrigido C40 + 1 PCE (se SANEPAR exigir C40 CAA IV nas estacas) | 87 (1092 m) | 169.2 | 30.8 | **199.9** | 4,899 | **R$ 389,272** | **+14.9%** | 5.14 | SIM |
| `600-S2` | Otimizado Perfuratriz Leve: 52×Ø50 cm (L=13 m) + Capitéis 95×95 (h=45) + 1 PCE | 52 (676 m) | 159.3 | 7.0 | **166.3** | 6,426 | **R$ 326,248** | **-3.7%** | 5.20 | SIM |
| `600-S3` | Otimizado Capitéis: 42×Ø60 cm (L=13,5 m) + Capitéis 110×110 (h=45) + 1 PCE | 42 (567 m) | 192.4 | 7.6 | **200.0** | 8,903 | **R$ 398,391** | **+17.5%** | 5.55 | SIM |
| `600-S4` | Otimizado Capitéis: 34×Ø70 cm (L=13,5 m) + Capitéis 140×140 (h=45) + 1 PCE | 34 (459 m) | 212.0 | 10.0 | **222.0** | 11,178 | **R$ 440,291** | **+29.9%** | 5.81 | SIM |

### Detalhamento de Custos e Enquadramento Contratual

- **`600-S0` — Original PBGE/PBES (como licitado: 83×Ø40 + 4×Ø50, C30):** Perfuração `R$ 106,945` · Concreto est. `R$ 93,034` · Aço est. `R$ 45,479` · Blocos/Cap./ΔLaje `R$ 59,158` (ΔAço laje `0 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 34,300`.
  - *Enquadramento:* Base contratual (geotecnicamente viável, mas exige corrigir 4 blocos Ø50 e cota de 7 estacas de 16 m).
  - *Síntese:* 1.111 m previstos; 85 blocos de 70 cm (170 m² de fôrma); atende β=3,42–3,68 sem PCE.
- **`600-S1a` — PBGE Corrigido C30 + 1 PCE (83×Ø40 + 4×Ø50 até rocha, 4 blocos 80×80):** Perfuração `R$ 105,042` · Concreto est. `R$ 91,354` · Aço est. `R$ 45,479` · Blocos/Cap./ΔLaje `R$ 59,870` (ΔAço laje `0 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 72,300`.
  - *Enquadramento:* Menor atrito contratual (correção pontual de compatibilização + PCE).
  - *Síntese:* Mantém C30 nas estacas (se CAA solo ≤ III), ajusta 4 blocos p/ 80×80 e valida β=5,14 c/ PCE.
- **`600-S1b` — PBGE Corrigido C40 + 1 PCE (se SANEPAR exigir C40 CAA IV nas estacas):** Perfuração `R$ 105,042` · Concreto est. `R$ 106,580` · Aço est. `R$ 45,479` · Blocos/Cap./ΔLaje `R$ 59,870` (ΔAço laje `0 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 72,300`.
  - *Enquadramento:* Aditivo justificável pela divergência de edital (PBGE C30 vs. PBES C40/CAA IV).
  - *Síntese:* Mesma geometria de S1a, mas quantificando o impacto financeiro do upgrade C30→C40 nas estacas.
- **`600-S2` — Otimizado Perfuratriz Leve: 52×Ø50 cm (L=13 m) + Capitéis 95×95 (h=45) + 1 PCE:** Perfuração `R$ 81,120` · Concreto est. `R$ 86,011` · Aço est. `R$ 39,585` · Blocos/Cap./ΔLaje `R$ 49,683` (ΔAço laje `2590 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 69,850`.
  - *Enquadramento:* Engenharia de Valor — REDUZ CUSTO mantendo equipamento leve (Ø50) e eliminando 85 blocos!.
  - *Síntese:* 52 estacas (~58 tf/est vs. 78 tf adm.), 676 m (-39% perfuração), menos fôrma e escavação.
- **`600-S3` — Otimizado Capitéis: 42×Ø60 cm (L=13,5 m) + Capitéis 110×110 (h=45) + 1 PCE:** Perfuração `R$ 87,885` · Concreto est. `R$ 103,884` · Aço est. `R$ 49,035` · Blocos/Cap./ΔLaje `R$ 71,436` (ΔAço laje `4256 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 86,150`.
  - *Enquadramento:* Engenharia de Valor — avalia ganho de produtividade (42 vs 87 estacas) vs. concreto Ø60.
  - *Síntese:* 567 m (-49% perfuração), volume total de concreto similar ao PBGE, exige checar flexão da laje.
- **`600-S4` — Otimizado Capitéis: 34×Ø70 cm (L=13,5 m) + Capitéis 140×140 (h=45) + 1 PCE:** Perfuração `R$ 89,505` · Concreto est. `R$ 114,465` · Aço est. `R$ 49,172` · Blocos/Cap./ΔLaje `R$ 101,698` (ΔAço laje `6295 kg`) · Terra/Solo-cim. `R$ 0` · Mob.+Ensaios `R$ 85,450`.
  - *Enquadramento:* Alternativa de mínimo nº de furos (34 estacas), porém com maior volume de concreto e aço na laje.
  - *Síntese:* 459 m (-59% perfuração), porém +25% concreto em estacas e maior reforço de flexão na laje.
