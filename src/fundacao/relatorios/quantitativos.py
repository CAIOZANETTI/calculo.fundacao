"""Cálculo de quantitativos de concreto, fôrma, aço (por bitola) e metragem de estacas."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from fundacao.estrutural.bloco_1_estaca import GeometriaBloco1Estaca
from fundacao.estrutural.bloco_2_estacas import GeometriaBloco2Estacas
from fundacao.normas.nbr6118 import massa_linear_kg_m


@dataclass(frozen=True)
class ResumoQuantitativos:
    n_blocos_1e: int
    n_blocos_2e: int
    total_estacas: int
    volume_concreto_blocos_m3: float
    area_forma_blocos_m2: float
    aco_por_bitola_kg: Dict[float, float]
    peso_aco_total_blocos_kg: float
    taxa_aco_kg_m3: float
    metragem_estacas_m: float


def calcular_quantitativos_blocos(
    n_blocos_1e: int,
    n_blocos_2e: int,
    geom_1e: GeometriaBloco1Estaca = GeometriaBloco1Estaca(),
    geom_2e: GeometriaBloco2Estacas = GeometriaBloco2Estacas(),
    comprimento_medio_estaca_m: float = 0.0,
    comprimento_arranque_1e_cm: float = 80.0,
) -> ResumoQuantitativos:
    """Calcula quantitativos dos blocos (1 e 2 estacas) seguindo exatamente o detalhamento PBES.

    Detalhamento unitário de aço (Pranchas 04/12 e 07/21):
      - Bloco 1 estaca: N1 = 12 Ø 6,3 C=345 cm; N2 = 12 Ø 6,3 C=60 cm; N3 = 4 Ø 6,3 C=80/86 cm
      - Bloco 2 estacas: N1 = 16 Ø 8 C=270 cm; N2 = 20 Ø 8 C=220 cm; N3 = 12 Ø 16 C=299 cm; N4 = 4 Ø 6,3 C=80 cm
    """
    vol_1e = n_blocos_1e * geom_1e.volume_concreto_m3
    vol_2e = n_blocos_2e * geom_2e.volume_concreto_m3
    vol_total = vol_1e + vol_2e

    forma_1e = n_blocos_1e * geom_1e.area_forma_m2
    forma_2e = n_blocos_2e * geom_2e.area_forma_m2
    forma_total = forma_1e + forma_2e

    # Comprimentos totais de barras por bitola (m)
    comp_6_3_m = (
        n_blocos_1e * (12 * 3.45 + 12 * 0.60 + 4 * (comprimento_arranque_1e_cm / 100.0))
        + n_blocos_2e * (4 * 0.80)
    )
    comp_8_0_m = n_blocos_2e * (16 * 2.70 + 20 * 2.20)
    comp_16_0_m = n_blocos_2e * (12 * 2.99)

    aco_kg: Dict[float, float] = {
        6.3: round(comp_6_3_m * massa_linear_kg_m(6.3), 1),
        8.0: round(comp_8_0_m * massa_linear_kg_m(8.0), 1),
        16.0: round(comp_16_0_m * massa_linear_kg_m(16.0), 1),
    }
    peso_total = round(sum(aco_kg.values()), 1)
    taxa_aco = round(peso_total / vol_total, 1) if vol_total > 0 else 0.0

    total_estacas = n_blocos_1e + 2 * n_blocos_2e
    metragem = round(total_estacas * comprimento_medio_estaca_m, 1)

    return ResumoQuantitativos(
        n_blocos_1e=n_blocos_1e,
        n_blocos_2e=n_blocos_2e,
        total_estacas=total_estacas,
        volume_concreto_blocos_m3=round(vol_total, 2),
        area_forma_blocos_m2=round(forma_total, 2),
        aco_por_bitola_kg=aco_kg,
        peso_aco_total_blocos_kg=peso_total,
        taxa_aco_kg_m3=taxa_aco,
        metragem_estacas_m=metragem,
    )
