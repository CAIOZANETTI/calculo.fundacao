# Parecer Geotécnico e Estrutural — Filtros de Areia ACTIFLO 360 L/s e 600 L/s

**Obra:** SANEPAR — SAA Foz do Iguaçu (PR) — ETA Vila C  
**Fontes reais analisadas (Google Drive — pasta `2. PBGE` completa + `Filtro_areia_360_600.zip`):**
- Sondagens SPT reais (`SP-01` a `SP-16`, 318,18 m): `001-SAA-0017-7471-SOND-RT-0000ETAVILACLOC-001-R0.pdf` (Geoazimute, 03/2022)
- Ensaios de laboratório reais (`AI-01` a `AI-06` — Cisalhamento Direto e Adensamento Unidimensional; `AMDEF-01` a `14` — Granulometria/CBR; Permeabilidade in situ): `001-SAA-0017-7471-ENSA-RT-0000ETAVILACLOC-001-R0.pdf` (Paraná Solos, 04/2022)
- Projeto Básico Geotécnico (PBGE): `001-GEOPLANTA1-R1`, `002-GEOSECAO2-R1`, `003-FUNDACAO1-R2` (ACTIFLO 360) e `005-FUNDACAO3-R2` (ACTIFLO 600)
- Projeto Básico Estrutural (PBES): 12 pranchas do `ACTIFLO 360` e 21 pranchas do `ACTIFLO 600`

> [!NOTE]
> O arquivo `2. PBGE.zip` dentro da pasta inicial estava vazio (apenas diretórios), mas localizamos a pasta original completa `2. PBGE` no Google Drive contendo todos os laudos SPT, ensaios geotécnicos e pranchas de fundação (`R2`). Todos os cálculos abaixo usam **dados reais da obra**.

---

## 1. Perfil Real do Subsolo e Ensaios de Laboratório

As 16 sondagens (`SP-01` a `SP-16`) e as seções geológicas (`002-GEOSECAO2-R1`) caracterizam três horizontes bem definidos na ETA Vila C:

| Horizonte | Profundidade típica | NSPT | Características dos Ensaios (`AI-01` a `AI-06`, 3 m) |
| :--- | :---: | :---: | :--- |
| **1. Argila siltosa vermelha porosa** (HRB A-7-5) | `0,0` a `4,8 m` (zona 360)<br>`0,0` a `7,8 m` (zona 600) | **4 a 7** | $\gamma_{\text{nat}} = 16{,}2\text{–}18{,}2\text{ kN/m}^3$, $w = 24{,}9\text{–}30{,}0\%$<br>$c' = 0{,}9\text{–}16{,}3\text{ kPa}$, $\phi' = 14{,}1^\circ\text{–}26{,}3^\circ$<br>**Adensamento (`AI-01` / `AI-02`):** $e_0 = 1{,}33\text{–}1{,}63$, $\sigma'_{vm} = \mathbf{65\text{–}110\text{ kPa}}$, **$C_c = 0{,}43\text{–}0{,}54$** (muito compressível!) |
| **2. Argila siltosa / Silte argiloso variegado** | `4,8` a `13–14,5 m` (zona 360)<br>`7,8` a `14,5–15,8 m` (zona 600) | **10 a 16** (zona 360)<br>**14 a 30+** (zona 600) | Médio a rijo na zona do 360; rijo a muito rijo/duro na zona do 600 (chega a `NSPT = 26–37` em `SP-08/09`) |
| **3. Impenetrável ao trépano de lavagem (Basalto)** | `12,5–14,5 m` (zona 360)<br>`14,5–15,8 m` (zona 600) | Impenetrável | Cotas do topo rochoso: **`225,10` a `227,56 m`** (360) e **`222,60` a `224,60 m`** (600) |
| **Nível d'água (N.A. — leitura 24h)** | **`7,50` a `9,00 m`** | — | Cotas **`230,57` a `232,06 m`** (`5,5` a `7,0 m` abaixo do fundo dos tanques) |

---

## 2. Balanço de Cargas: Tanque Vazio vs. Cheio Estático vs. Operando (Microareia e Agitadores)

A partir dos cortes longitudinais (`Corte F.F.` do 360 L/s e `Corte A.A.` do 600 L/s), o nível d'água interno de operação é `243,60 m` (360) e `243,61 m` (600), sobre fundo principal em `238,60 m` / `238,61 m` — resultando em lâmina útil de **$H_w \approx 4{,}85\text{ a }5{,}00\text{ m}$**.

| Parcela de Carga | ACTIFLO 360 L/s | ACTIFLO 600 L/s | Participação |
| :--- | ---: | ---: | :---: |
| Concreto armado + lastro + enchimento (**Vazio**) | **536 tf** (`202,2 m³`) | **1.294 tf** (`478,1 m³`) | ~42–43% |
| Volume de água em operação ($H_w \approx 4{,}85\text{–}5{,}0\text{ m}$) | **~543 m³ → 543 tf** | **~1.431 m³ → 1.431 tf** | ~43–47% |
| Microareia em suspensão + lodo de fundo (~`8 kg/m³`) | ~4–5 tf | ~11–12 tf | < 0,5% |
| Equipamentos, passarelas, sobrecargas e folgas do PBES | ~186 tf | ~287 tf | ~10–15% |
| **Total Característico nas Pranchas PBES ($\sum N_k$)** | **1.270 tf** | **3.023 tf** | **100%** |
| Tensão média em planta (Vazio → Cheio em Operação) | `36,3 → 85,9 kPa` | `34,8 → 81,2 kPa` | — |
| Acréscimo dinâmico típico dos agitadores (~2–3% sobre água) | `+16 tf` (+1,3%) | `+43 tf` (+1,4%) | Marginal |

### Conclusão sobre Estático vs. Operação com Agitadores
1. **As cargas do PBES (`1.270 tf` e `3.023 tf`) já representam o tanque cheio em operação.**
2. **A vibração dos agitadores não altera de forma significativa o dimensionamento axial das fundações:** misturadores/agitadores de coagulação e maturação ACTIFLO operam em baixa/média rotação; o esforço dinâmico vertical soma < 2% da carga total (coberto pelas sobrecargas e fatores de segurança `FS = 2,0` / `γf = 1,4`).
3. **Efeito relevante da operação:** o ciclo de **enchimento e esvaziamento** (`35 → 86 kPa`) exige controle rígido de recalque diferencial para não comprometer o nivelamento dos vertedores/lamelas nem abrir juntas hidroexpansivas de estanqueidade (CAA IV).

---

## 3. Verificação das Estacas Projetadas (PBGE + PBES) Frente às Sondagens Reais

O PBGE (`003-FUNDACAO1-R2` e `005-FUNDACAO3-R2`) projetou **Estacas Hélice Contínua Monitoradas Ø 40 cm e Ø 50 cm** com comprimentos de `6 m` a `16 m`. Cruzando o projeto com as sondagens reais vizinhas (`SP-01`..`SP-04` para o 360; `SP-05`..`SP-10` para o 600), obtemos:

### 3.1 Capacidade Geotécnica Real até o Limite das Sondagens / Topo Rochoso (`FS = 2,0`)

| Unidade / Furo | Topo Rocha (cota) | Arrasamento | Compr. PBGE | $L_{\text{ef}}$ até rocha | Diâm. | Aoki-Velloso | Décourt-Quaresma | Antunes-Cabral | **Média (tf)** | Carga PBES máx/est. |
| :--- | :---: | :---: | :---: | :---: | :---: | ---: | ---: | ---: | ---: | ---: |
| **360** — `SP-01` | `226,18 m` | `237,65 m` | `14–15 m` | `11,5 m` | Ø40 | 27,0 | 39,1 | 24,3 | **30,1** | 47–53 tf *(insuf. solo)* |
| **360** — `SP-01` | `226,18 m` | `237,65 m` | `15 m` | `11,5 m` | Ø50 | 37,2 | 50,4 | 30,8 | **39,5** | 53–55 tf *(insuf. solo)* |
| **360** — `SP-02` | `225,10 m` | `237,65 m` | `14–15 m` | `12,6 m` | Ø40 | 28,1 | 43,2 | 27,3 | **32,9** | 47–53 tf *(insuf. solo)* |
| **360** — `SP-02` | `225,10 m` | `237,65 m` | `15 m` | `12,6 m` | Ø50 | 38,1 | 55,4 | 34,5 | **42,6** | 53–55 tf *(insuf. solo)* |
| **360** — `SP-03/04` | `227,07–227,56 m` | `237,65 m` | `14–15 m` | **`9,5–10,6 m`** | Ø40 | 26,3–28,4 | 35,6–38,1 | 20,2–21,9 | **27,4–29,5** | 47–53 tf *(crítico!)* |
| **360** — `SP-03/04` | `227,07–227,56 m` | `237,65 m` | `15 m` | **`9,5–10,6 m`** | Ø50 | 36,4–39,2 | 46,2–49,5 | 25,7–27,9 | **36,1–38,9** | 53–55 tf *(crítico!)* |
| **600** — `SP-05` | `> 223,55 m` | `237,66 m` | `12–16 m` | `13,6 m` | Ø40 | 40,9 | 57,0 | 36,0 | **44,6** | 48–49 tf *(limite)* |
| **600** — `SP-05` | `> 223,55 m` | `235,81 m` | `14 m` | `11,8 m` | Ø50 | 55,1 | 70,5 | 44,2 | **56,6** | 61 tf (`PC59`, *limite*) |
| **600** — `SP-06/08` | `223,11–223,77 m` | `237,66 m` | `12–16 m` | `13,8–14,0 m` | Ø40 | 49,5–49,9 | 67,6–68,5 | 44,3–44,9 | **54,1** | 48–49 tf *(OK)* |
| **600** — `SP-06/08` | `223,11–223,77 m` | `235,81 m` | `14 m` | `12,0–12,2 m` | Ø50 | 66,8–67,4 | 84,1–85,8 | 54,9–55,5 | **69,0–69,2** | 61 tf (`PC59`, *OK*) |
| **600** — `SP-09` | `224,30 m` | `237,66 m` | `12–16 m` | `12,5 m` | Ø40 | 54,7 | 78,1 | 54,2 | **62,4** | 48–49 tf *(OK)* |
| **600** — `SP-09` | `224,30 m` | `235,81 m` | `14 m` | `10,7 m` | Ø50 | 72,8 | 97,2 | 66,9 | **79,0** | 61 tf (`PC59`, *OK*) |

### 3.2 Diagnóstico: As Estacas Projetadas Estão Adequadas?

> [!CAUTION]
> **Veredito:** O projeto atual **NÃO deve ir para execução sem revisão prévia**, devido a **4 problemas objetivos** identificados:

1. **Ponta teórica dentro da rocha impenetrável (especialmente no ACTIFLO 360):**
   - No **ACTIFLO 360**, o PBGE especifica estacas de **`14–15 m`** (`cota ponta 222,65–223,65 m`), mas o basalto impenetrável aparece em **`225,10–227,56 m`** — **2,5 a 4,9 m acima**! A hélice contínua irá travar com `9,5–12,6 m` de comprimento efetivo, onde a capacidade geotécnica em solo (`27–33 tf` para Ø40 e `36–43 tf` para Ø50) **não atende** às cargas de `44–55 tf` sem comprovar, via prova de carga, contribuição efetiva de ponta apoiada no topo rochoso limpo.
   - No **ACTIFLO 600**, o solo profundo é muito melhor (`NSPT = 19–30`), atendendo bem na maior parte dos furos (`SP-06/08/09/10`), mas 7 estacas de `L = 16 m` (`P4, PC5, PC28, PC38, PC53, PC68, PC82`) também projetam a ponta para `221,5–221,7 m`, **1 a 2,8 m dentro da rocha**.
2. **Incompatibilidade geométrica PBGE × PBES (estacas Ø 50 cm em blocos de `70×70 cm`):**
   - O PBGE adotou **Ø 50 cm** em **6 pontos do 360** (`PC9, PC11, PC12, PC17, PC18, PC21`) e **4 pontos do 600** (`PC41, PC44, PC47, PC59`), mas o PBES detalhou todos os blocos de 1 estaca com `70×70 cm` (folga lateral de `10 cm < 15 cm` mínimo da NBR 6122). Esses 10 blocos devem passar para **`80×80 cm`**.
3. **Divergência de classe de concreto:** PBGE especifica **C30** nas estacas vs. **CAA IV / C40** no PBES (precisa justificar/compatibilizar segundo NBR 6122:2022 Tabela 4).
4. **Erro de etiqueta na prancha PBGE `003-FUNDACAO1-R2`:** `PC17` aparece duplicado no lugar de `PC18`.

---

## 4. Nível d'Água (~8 m) e Uso de "Estaca Escavada" até 16 m

- **Estaca escavada convencional (trado mecânico a seco, sem fluido estabilizante):** **INADEQUADA e PROIBIDA pela NBR 6122:2022** abaixo do N.A. (`7,5–9,0 m`), por risco crítico de desmoronamento das paredes do furo, lavagem do concreto e seccionamento do fuste.
- **Estaca Hélice Contínua Monitorada (efetivamente especificada no PBGE e PBES):** **TECNICAMENTE ADEQUADA abaixo do N.A.**, pois o trado helicoidal sustenta as paredes durante a perfuração e o concreto é injetado sob **pressão positiva contínua** pela haste central à medida que o trado sobe, impedindo entrada de água e desmoronamento.
  - **Limitação real neste local:** o problema não é o lençol freático em si, e sim a **incapacidade da hélice contínua de penetrar o topo rochoso** (`12,5–15,8 m`) somada à baixa resistência de ponta quando há solo amolgado na base (exigindo monitoramento eletrônico 100%, slump `220 ± 30 mm` e **prova de carga estática/dinâmica**).
- **Subpressão nos tanques vazios:** como o N.A. está em `cota 230,6–232,1 m` (`~5,5 a 7,0 m` abaixo do fundo dos tanques), **não há risco de flutuação** pelo lençol freático medido.

---

## 5. Viabilidade de Fundação Direta (Radier) e Melhoramento de Solo (Rachão / Solo-Cimento)

### 5.1 Capacidade de Carga (Ruptura — Vesic com $c', \phi'$ reais de `AI-01`..`AI-06`)
- Tensão média em radier: **`86 kPa`** (`61 kPa` líquida) no 360 L/s e **`81 kPa`** (`56 kPa` líquida) no 600 L/s.
- Tensão admissível à ruptura (`FS = 3`): **`141 kPa`** (envoltória mínima `AI-02`, $\phi'=14{,}1^\circ, c'=16\text{ kPa}$) a **`381 kPa`** (`AI-01`). **Logo, a ruptura NÃO é o fator limitante.**

### 5.2 Recalques por Adensamento (Curvas Edométricas Reais `AI-01` e `AI-02`, Propagação 2:1)

Como a argila vermelha superficial tem $e_0 = 1{,}33\text{–}1{,}63$, $\sigma'_{vm} = 65\text{–}110\text{ kPa}$ e $C_c = 0{,}43\text{–}0{,}54$, o carregamento do tanque cheio **ultrapassa a tensão de pré-adensamento** em `AI-02` e entra na reta virgem de compressão:

| Cenário de Troca / Reforço abaixo da laje (`prof. 1,5 m`) | ACTIFLO 360 (`argila mole até 4,8 m`)<br>Recalque Total Estimado (`AI-01` a `AI-02`) | ACTIFLO 600 (`argila mole até 7,8 m`)<br>Recalque Total Estimado (`AI-01` a `AI-02`) | Viabilidade (limite ≤ 2,5–3,0 cm) |
| :--- | :---: | :---: | :--- |
| **0,0 m** (Radier direto sobre solo natural) | `3,6` a **`14,0–19,3 cm`** | `8,9` a **`21,9–30,6 cm`** | **INVIÁVEL** (ambos) |
| **1,5 m** de rachão / brita / solo-cimento | `3,0` a **`9,8–12,5 cm`** | `8,7` a **`18,4–24,5 cm`** | **INVIÁVEL** (bulbo atravessa camada mole!) |
| **2,5 m** de rachão / solo-cimento | `2,3` a **`5,1–6,2 cm`** | `8,8` a **`14,5–19,1 cm`** | Limite/Arriscado no 360; **INVIÁVEL** no 600 |
| **3,3 m** (Troca total da argila mole até cota `~234,8 m`) | **`~0,9–1,5 cm`** (apoio direto no silte rijo!) | `8,0` a **`11,1–14,7 cm`** (restam 3 m moles!) | **VIÁVEL NO 360 L/s**; **INVIÁVEL NO 600 L/s** |

> [!IMPORTANT]
> **Por que um colchão superficial de 1–2 m de rachão ou solo-cimento NÃO resolve sozinho?**
> O bulbo de tensões de um radier com largura `B = 8,4 m` (360) ou `16,9 m` (600) atinge **12 a 25+ m de profundidade**. Uma camada rígida de 1,5 m apenas redistribui tensões locais, mas **não impede o adensamento dos 3 a 5 m de argila porosa mole ($C_c = 0{,}54$) que permanecem abaixo**.
> - No **ACTIFLO 360 L/s**, como a argila mole termina a apenas `~3,3 m` abaixo da laje (e `~3,5 m` acima do N.A.), **a troca integral desses 3,3 m por solo-cimento compactado (ou aterro estrutural / rachão drenado)** elimina a camada compressível e viabiliza fundação direta em radier!
> - No **ACTIFLO 600 L/s**, a argila mole vai até **`7,8 m`** (tocando o lençol freático!), inviabilizando economicamente a escavação e troca total.

---

## 6. Matriz Comparativa de Soluções Alternativas de Fundação

| Solução | Adequação ao N.A. (`8 m`) | ACTIFLO 360 L/s | ACTIFLO 600 L/s | Principais Prós e Contras |
| :--- | :---: | :---: | :---: | :--- |
| **1. Hélice Contínua Revisada** (Ø40/Ø50 cm + blocos `80×80` + PCE) | **Sim** (pressão positiva) | **Média** *(precisa PCE p/ validar ponta na rocha ou aumentar nº/Ø)* | **Alta** *(excelente no silte `NSPT 19–30`; só limitar L à rocha e ajustar 4 blocos Ø50)* | Mantém conceito do projeto; exige rigor executivo e compatibilização PBGE×PBES. |
| **2. Estaca Pré-Moldada de Concreto / Metálica Cravada até Nega** | **Excelente** (seca, sem concretagem submersa) | **Muito Alta** *(nega real no basalto a 12,5–14,5 m resolve a baixa NSPT do 360!)* | **Alta** *(crava até nega a 14,5–15,8 m, maior carga/estaca → menos estacas)* | **Melhor desempenho geotécnico de ponta na rocha**; verificar vibração em estruturas existentes da ETA (`Filtro Velho`, `EE Lodo`). |
| **3. Radier Estaqueado (Piled Raft)** com Hélice Contínua | **Sim** | **Alta** | **Muito Alta** *(potencial de reduzir 25–40% das 87 estacas!)* | Aproveita laje de fundo de 30 cm já existente; exige modelagem solo-estrutura (MEF) e validação com fornecedor ACTIFLO. |
| **4. Fundação Direta (Radier) + Troca Total de Solo (Solo-Cimento `3,3 m`)** | **Sim no 360** (acima do N.A.) | **Alta** *(elimina 39 estacas + 30 blocos; recalque `< 1,5 cm`)* | **Inviável** *(argila mole vai até 7,8 m, no N.A.)* | Muito competitiva no **360 L/s** (~`600 m³` escavação + solo-cimento, sem mobilizar perfuratriz para 39 estacas curtas). |
| **5. Estaca Escavada c/ Fluido Estabilizante ou Estaca Raiz** | **Sim** | **Alta** *(Raiz embute no basalto → cargas `70–100+ tf`)* | **Média** *(custo/m maior que Hélice)* | Útil se o topo do basalto for muito irregular ou houver restrição de vibração para cravação. |
| **6. Colunas de Brita / Jet Grouting / DSM + Radier** | **Sim** | **Média** *(troca direta é mais barata)* | **Média** *(controla recalque nos 6,3 m moles)* | Mobilização especializada cara para obra de médio porte; perde em custo para Radier Estaqueado ou Pré-Moldada. |

### Recomendações Práticas de Engenharia
1. **Para o ACTIFLO 360 L/s:** avaliar seriamente duas rotas superiores ao projeto atual:
   - **(a) Fundação direta em radier com troca integral dos ~3,3 m de argila mole por solo-cimento compactado** (acima do N.A., solução limpa e sem dependência da ponta de hélice na rocha), **OU**
   - **(b) Estaca Pré-Moldada/Metálica cravada até nega no basalto** (se a vibração for tolerável às estruturas vizinhas) — ou manter Hélice Contínua **reforçando diâmetro/quantidade** e executando **Prova de Carga Estática**.
2. **Para o ACTIFLO 600 L/s:** manter fundação profunda (**Hélice Contínua revisada** ou **Radier Estaqueado** para otimizar as 87 estacas, ou **Pré-Moldada cravada**), corrigindo obrigatoriamente os **4 blocos de Ø 50 cm para `80×80 cm`**, ajustando as 7 estacas de `16 m` ao topo rochoso real e compatibilizando `C30` vs. `C40`.
