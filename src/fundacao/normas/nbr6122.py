"""Parâmetros normativos de fundações profundas (ABNT NBR 6122:2022)."""

from __future__ import annotations

from dataclasses import dataclass

from fundacao.normas.nbr6118 import ClasseAgressividade


@dataclass(frozen=True)
class FatoresSegurancaNBR6122:
    """Fatores de segurança globais e parciais segundo ABNT NBR 6122:2022 (Seção 6 e Tabela 3)."""

    # Fator de segurança global à ruptura geotécnica (compressão) sem prova de carga estática
    fs_global_sem_pce: float = 2.0
    # Fator de segurança global com provas de carga estáticas (PCE) atendendo item 6.2.1.2
    fs_global_com_pce: float = 1.6
    # Fator de segurança global à tração (item 6.2.2)
    fs_tracao: float = 2.0
    # Coeficiente de ponderação das ações (ELU)
    gamma_f: float = 1.4
    # Coeficiente de redução da resistência geotécnica no método dos valores de cálculo (Tabela 2)
    gamma_m_sem_pce: float = 1.4
    gamma_m_com_pce: float = 1.25
    # Fator de segurança mínimo contra flutuação / subpressão (NBR 6122 / NBR 8681)
    fs_flutuacao_min: float = 1.10


@dataclass(frozen=True)
class RequisitosHeliceContinua:
    """Requisitos construtivos e estruturais para Estacas Hélice Contínua (NBR 6122:2022 Anexo N)."""

    # Espaçamento mínimo recomendado entre eixos de estacas (em múltiplos do diâmetro D)
    espacamento_min_d: float = 2.5
    espacamento_rec_d: float = 3.0
    # Distância mínima da face da estaca à borda do bloco (cm)
    borda_min_bloco_cm: float = 15.0
    # Embutimento mínimo da cabeça da estaca no bloco (cm)
    embutimento_min_bloco_cm: float = 5.0
    # Taxa mínima de armadura longitudinal útil em estacas armadas (Anexo N / Tabela 5)
    taxa_armadura_min_compressao: float = 0.004  # 0,4% da seção de concreto
    # Comprimento mínimo armado abaixo da cota de arrasamento (m)
    comprimento_min_armado_m: float = 4.0
    # Quantidade mínima de barras longitudinais
    n_barras_min: int = 4
    # Bitola mínima longitudinal (mm)
    bitola_min_mm: float = 10.0


def fck_minimo_estaca_helice_mpa(caa: ClasseAgressividade) -> float:
    """fck mínimo do concreto de estaca hélice contínua (NBR 6122:2022 Tabela 4)."""
    # Tabela 4 da NBR 6122:2022 adota mínimo C20 (CAA I/II), C30 (CAA III), C40 (CAA IV)
    return {
        ClasseAgressividade.I: 20.0,
        ClasseAgressividade.II: 25.0,
        ClasseAgressividade.III: 30.0,
        ClasseAgressividade.IV: 40.0,
    }[caa]


def tensao_admissivel_estaca_helice_mpa(
    fck_mpa: float,
    armada_compressao: bool = False,
) -> float:
    """Estima tensão média de trabalho estrutural no fuste de estaca hélice contínua (NBR 6122:2022).

    Segundo a NBR 6122:2022 Tabela 5 (Estacas moldadas in loco — Hélice Contínua):
    - Concreto C20 a C40, com fator redutor de concretagem in loco (γc_estaca = 1,4 × 1,4 = 1,96
      ou tensão média de trabalho usual de 0,25·fck limitada a 6,0 MPa sem armadura de compressão
      calculada, podendo atingir valores maiores quando devidamente armada e verificada à flexocompressão).

    Retorna a tensão média admissível característica (MPa) para pré-dimensionamento estrutural.
    """
    if fck_mpa < 20.0:
        raise ValueError(f"fck={fck_mpa} MPa abaixo do mínimo normativo (20 MPa) para hélice contínua.")

    if not armada_compressao:
        # Critério conservador NBR 6122:2022 Tabela 5: sem armadura de compressão, limite 6,0 MPa
        # (ou 0,25·fck se inferior; para C40, 0,25*40=10 MPa mas sem armadura de compressão limita-se a 6,0 MPa)
        return min(0.25 * fck_mpa, 6.0)

    # Estaca armada à compressão: fcd_estaca = (0.85 * fck) / (1.4 * 1.4), tensão característica ≈ fcd_estaca / 1.4
    # Para C40: 0.85 * 40 / (1.96 * 1.4) ≈ 12.4 MPa (muito conservador adotar 0.25 * fck = 10.0 MPa)
    return min(0.25 * fck_mpa, 10.0)
