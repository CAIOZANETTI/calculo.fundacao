# calculo.fundacao

Biblioteca e CLI em Python para **cálculo geotécnico e verificação estrutural de fundações profundas** (estacas hélice contínua e blocos rígidos sobre estacas), seguindo **ABNT NBR 6122:2022** e **ABNT NBR 6118:2023**, com datasets completos dos módulos de tratamento com microareia **ACTIFLO 360 L/s** e **ACTIFLO 600 L/s** (SANEPAR — ETA Vila C, Foz do Iguaçu/PR).

## Estrutura do Repositório

```text
calculo.fundacao/
├── pyproject.toml
├── src/fundacao/
│   ├── normas/
│   │   ├── nbr6118.py          # Concreto, aço, CAA I–IV, nós CCC/CCT e ancoragem
│   │   └── nbr6122.py          # Fatores de segurança e requisitos de hélice contínua
│   ├── geotecnia/
│   │   ├── sondagem.py         # Modelo SPT com desconto automático por cota de arrasamento
│   │   ├── aoki_velloso.py     # Aoki & Velloso (1975) + Monteiro (1997)
│   │   ├── decourt_quaresma.py # Décourt & Quaresma (1978/1996)
│   │   ├── antunes_cabral.py   # Antunes & Cabral (1996) — Hélice Contínua
│   │   ├── teixeira.py         # Teixeira (1996) — Velloso & Lopes
│   │   ├── alonso.py           # Alonso (1996) — Hélice Contínua
│   │   ├── capacidade.py       # Envelope 3 ou 5 métodos e dimensionamento de L
│   │   ├── fundacao_direta.py  # Capacidade Vesic, adensamento 1D e troca de solo
│   │   ├── grupo_radier_estaqueado.py # Eficiência/recalque de grupo e PDR (Poulos-Davis-Randolph)
│   │   └── vibracao_cravacao.py       # Atenuação PPV (Wiss / Woods-Jedele / DIN 4150-3 / NBR 9653)
│   ├── estrutural/
│   │   ├── estaca.py           # Verificação de fuste (compressão, durabilidade e armadura)
│   │   ├── bloco_1_estaca.py   # Bloco 1 estaca (geometria, esmagamento e fendimento)
│   │   ├── bloco_2_estacas.py  # Bloco 2 estacas (Bielas e Tirantes — Blévot / NBR 6118)
│   │   └── puncao_capitel.py   # Punção em laje de fundo e capitéis (NBR 6118:2023 Seção 19.5)
│   ├── verificacoes/
│   │   ├── auditoria.py        # Auditoria ponto a ponto e estudo de sensibilidade
│   │   ├── cargas_tanque.py    # Balanço de cargas (vazio vs. cheio vs. agitadores)
│   │   ├── confiabilidade.py   # Confiabilidade FORM Lognormal (β e Pf — ISO 2394 / EC7)
│   │   └── subpressao.py       # Estabilidade global à flutuação (tanque vazio)
│   ├── relatorios/
│   │   ├── quantitativos.py    # Concreto, fôrma, aço por bitola e metragem de estacas
│   │   ├── memorial.py         # Gerador de memorial técnico (.md) e planilha (.csv)
│   │   └── estudo_exaustivo.py # Orquestrador determinístico completo (.md + .json)
│   └── cli.py                  # Interface de linha de comando (`fundacao`)
├── projetos/
│   ├── actiflo_360/            # 30 pontos de carga (39 estacas, 1.270 tf)
│   ├── actiflo_600/            # 85 pontos de carga (87 estacas, 3.023 tf)
│   └── sondagens/
│       ├── eta_vila_c_real/    # 9 furos SPT reais (SP-01..SP-10) + ensaios AI-01..AI-06
│       └── exemplo_hipotetico_basalto.yaml
├── saidas/                     # Memoriais, estudo exaustivo (.md/.json) e auditorias CSV
└── tests/
    └── test_fundacao.py
```

## Instalação Rápida

```bash
pip install -e .
```

Ou execute diretamente sem instalar usando `PYTHONPATH=src`:

```bash
PYTHONPATH=src python3 -m fundacao --help
```

## Exemplos de Uso (CLI)

### 1. Estudo Exaustivo 100% Determinístico (gera memória em Markdown + JSON estruturado)

```bash
PYTHONPATH=src python3 -m fundacao exaustivo
```

### 2. Auditar as estruturas ACTIFLO 360 L/s e 600 L/s

```bash
PYTHONPATH=src python3 -m fundacao auditar actiflo_360 --sondagem projetos/sondagens/eta_vila_c_real/sp02.yaml
PYTHONPATH=src python3 -m fundacao auditar actiflo_600 --sondagem projetos/sondagens/eta_vila_c_real/sp08.yaml
```

### 3. Balanço de cargas (vazio vs. cheio estático vs. operação com agitadores)

```bash
PYTHONPATH=src python3 -m fundacao tanque actiflo_360
PYTHONPATH=src python3 -m fundacao tanque actiflo_600
```

### 4. Fundação direta (radier), recalque por adensamento e troca de solo

```bash
PYTHONPATH=src python3 -m fundacao direta actiflo_360 --amostra AI-02
PYTHONPATH=src python3 -m fundacao direta actiflo_600 --amostra AI-02
```

### 5. Curva geotécnica $P_{\text{adm}}(L)$ nas sondagens reais da ETA Vila C

```bash
PYTHONPATH=src python3 -m fundacao geotecnia projetos/sondagens/eta_vila_c_real/sp01.yaml \
  --diametro-cm 70 --cota-arrasamento 237.650 --comprimentos 6,8,10,11.5
PYTHONPATH=src python3 -m fundacao geotecnia projetos/sondagens/eta_vila_c_real/sp08.yaml \
  --diametro-cm 70 --cota-arrasamento 235.812 --comprimentos 6,8,10,12
```

### 6. Gerar memorial de cálculo completo e planilha CSV

```bash
PYTHONPATH=src python3 -m fundacao memorial actiflo_360 \
  --sondagem projetos/sondagens/eta_vila_c_real/sp02.yaml \
  --out saidas/memorial_actiflo_360.md \
  --csv-out saidas/auditoria_actiflo_360.csv

PYTHONPATH=src python3 -m fundacao memorial actiflo_600 \
  --sondagem projetos/sondagens/eta_vila_c_real/sp08.yaml \
  --out saidas/memorial_actiflo_600.md \
  --csv-out saidas/auditoria_actiflo_600.csv
```

## Testes

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
