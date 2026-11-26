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
│   │   └── capacidade.py       # Envelope multi-método e dimensionamento de comprimento L
│   ├── estrutural/
│   │   ├── estaca.py           # Verificação de fuste (compressão, durabilidade e armadura)
│   │   ├── bloco_1_estaca.py   # Bloco 1 estaca (geometria, esmagamento e fendimento)
│   │   └── bloco_2_estacas.py  # Bloco 2 estacas (Bielas e Tirantes — Blévot / NBR 6118)
│   ├── verificacoes/
│   │   ├── auditoria.py        # Auditoria ponto a ponto e estudo de sensibilidade
│   │   └── subpressao.py       # Estabilidade global à flutuação (tanque vazio)
│   ├── relatorios/
│   │   ├── quantitativos.py    # Concreto, fôrma, aço por bitola e metragem de estacas
│   │   └── memorial.py         # Gerador de memorial técnico (.md) e planilha (.csv)
│   └── cli.py                  # Interface de linha de comando (`fundacao`)
├── projetos/
│   ├── actiflo_360/            # 30 pontos de carga (39 estacas, 1.270 tf)
│   ├── actiflo_600/            # 85 pontos de carga (87 estacas, 3.023 tf)
│   └── sondagens/
│       └── exemplo_hipotetico_basalto.yaml  # Exemplo para testes (substituir pelo 2. PBGE)
├── saidas/                     # Memoriais e auditorias gerados para ACTIFLO 360 e 600
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

### 1. Auditar as estruturas ACTIFLO 360 L/s e 600 L/s

```bash
# Auditoria estrutural e de alocação de estacas (P_adm padrão = 55 tf)
PYTHONPATH=src python3 -m fundacao auditar actiflo_360
PYTHONPATH=src python3 -m fundacao auditar actiflo_600

# Testar com outra carga admissível (ex.: 60 tf/estaca)
PYTHONPATH=src python3 -m fundacao auditar actiflo_600 --p-adm 60
```

### 2. Estudo de sensibilidade ($P_{\text{adm}}$ vs. quantidade de estacas)

```bash
PYTHONPATH=src python3 -m fundacao sensibilidade actiflo_360
PYTHONPATH=src python3 -m fundacao sensibilidade actiflo_600
```

### 3. Curva geotécnica $P_{\text{adm}}(L)$ (Aoki-Velloso, Décourt-Quaresma e Antunes-Cabral)

```bash
PYTHONPATH=src python3 -m fundacao geotecnia projetos/sondagens/exemplo_hipotetico_basalto.yaml \
  --diametro-cm 40 --cota-arrasamento 237.650 --comprimentos 6,8,10,12,14,16
```

### 4. Gerar memorial de cálculo completo e planilha CSV

```bash
PYTHONPATH=src python3 -m fundacao memorial actiflo_360 \
  --out saidas/memorial_actiflo_360.md \
  --csv-out saidas/auditoria_actiflo_360.csv

PYTHONPATH=src python3 -m fundacao memorial actiflo_600 \
  --out saidas/memorial_actiflo_600.md \
  --csv-out saidas/auditoria_actiflo_600.csv
```

## Como Inserir as Sondagens Reais (`2. PBGE`)

Quando os laudos SPT da ETA Vila C estiverem disponíveis, crie arquivos YAML em `projetos/sondagens/` seguindo o formato de `projetos/sondagens/exemplo_hipotetico_basalto.yaml` (com `hipotetico: false`, `cota_boca_m` e `camadas` metro a metro) e passe `--sondagem projetos/sondagens/sp01.yaml` aos comandos `auditar`, `memorial` ou `geotecnia`. O motor desconta automaticamente a escavação até cada cota de arrasamento das estacas (`235,562 m` a `239,150 m`).

## Testes

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```
