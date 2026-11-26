"""Verificação estrutural e geométrica de bloco sobre 1 estaca (NBR 6118:2023 / NBR 6122:2022)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from fundacao.normas.nbr6118 import (
    ACO_CA50,
    Aco,
    ClasseAgressividade,
    Concreto,
    TF_PARA_KN,
)
from fundacao.normas.nbr6122 import RequisitosHeliceContinua


@dataclass(frozen=True)
class GeometriaBloco1Estaca:
    """Dimensões em cm de bloco sobre 1 estaca (padrão PBES: 70 x 70 x 70 cm)."""

    largura_x_cm: float = 70.0
    largura_y_cm: float = 70.0
    altura_h_cm: float = 70.0
    diametro_estaca_cm: float = 40.0
    embutimento_estaca_cm: float = 5.0
    cobrimento_cm: float = 4.5
    pilar_a_cm: float = 30.0
    pilar_b_cm: float = 30.0

    @property
    def folga_borda_cm(self) -> float:
        return (min(self.largura_x_cm, self.largura_y_cm) - self.diametro_estaca_cm) / 2.0

    @property
    def volume_concreto_m3(self) -> float:
        return (self.largura_x_cm * self.largura_y_cm * self.altura_h_cm) * 1e-6

    @property
    def area_forma_m2(self) -> float:
        perimetro_m = 2.0 * (self.largura_x_cm + self.largura_y_cm) / 100.0
        return perimetro_m * (self.altura_h_cm / 100.0)


@dataclass(frozen=True)
class ResultadoBloco1Estaca:
    nk_tf: float
    nd_kn: float
    folga_borda_cm: float
    atende_geometria: bool
    tensao_contato_pilar_mpa: float
    tensao_contato_estaca_mpa: float
    fcd1_limite_mpa: float
    atende_esmagamento: bool
    forca_fendimento_kn: float
    as_fendimento_req_cm2: float
    as_horizontal_adotada_cm2: float
    atende_fendimento: bool
    volume_concreto_m3: float
    area_forma_m2: float
    aprovado: bool
    alertas: List[str]


def verificar_bloco_1_estaca(
    nk_tf: float,
    geometria: GeometriaBloco1Estaca = GeometriaBloco1Estaca(),
    concreto: Concreto = Concreto(fck_mpa=40.0, caa=ClasseAgressividade.IV),
    aco: Aco = ACO_CA50,
    gamma_f: float = 1.4,
    as_horizontal_adotada_cm2: float = 3.74,  # 12 ramos Ø 6,3 mm (6 grampos por direção no PBES)
) -> ResultadoBloco1Estaca:
    """Verifica geometria, esmagamento e armadura de fendimento (bursting) em bloco de 1 estaca.

    Força de tração transversal por fendimento (Leonhardt / NBR 6118 modelo de carga parcial):
      F_td = 0,25 · N_d · (1 - a_p / B)   (quando a_p < B)
    """
    req = RequisitosHeliceContinua()
    nd_kn = gamma_f * nk_tf * TF_PARA_KN

    folga = geometria.folga_borda_cm
    atende_geom = (
        folga >= req.borda_min_bloco_cm - 1e-6
        and geometria.embutimento_estaca_cm >= req.embutimento_min_bloco_cm - 1e-6
        and geometria.altura_h_cm >= max(50.0, geometria.diametro_estaca_cm + 20.0) - 1e-6
    )

    area_pilar_m2 = (geometria.pilar_a_cm * geometria.pilar_b_cm) * 1e-4
    area_estaca_m2 = (math.pi * (geometria.diametro_estaca_cm ** 2) / 4.0) * 1e-4

    sigma_pilar_mpa = (nd_kn / area_pilar_m2) / 1000.0
    sigma_estaca_mpa = (nd_kn / area_estaca_m2) / 1000.0
    limite_mpa = concreto.fcd1_mpa
    atende_esm = (sigma_pilar_mpa <= limite_mpa) and (sigma_estaca_mpa <= limite_mpa)

    # Fendimento transversal (Leonhardt): considera menor razão a/B entre pilar e estaca
    b_bloco = min(geometria.largura_x_cm, geometria.largura_y_cm)
    a_crit = min(geometria.pilar_a_cm, geometria.pilar_b_cm, geometria.diametro_estaca_cm)
    f_td_kn = max(0.0, 0.25 * nd_kn * (1.0 - a_crit / b_bloco))
    as_req_cm2 = (f_td_kn * 10.0) / aco.fyd_mpa
    atende_fend = as_horizontal_adotada_cm2 >= as_req_cm2

    alertas: List[str] = []
    if not atende_geom:
        alertas.append(
            f"Geometria fora do recomendado (folga={folga:.1f} cm, embut={geometria.embutimento_estaca_cm:.1f} cm, h={geometria.altura_h_cm:.1f} cm)."
        )
    if not atende_esm:
        alertas.append(
            f"Tensão de contato excede fcd1={limite_mpa:.2f} MPa (pilar={sigma_pilar_mpa:.2f} MPa, estaca={sigma_estaca_mpa:.2f} MPa)."
        )
    if not atende_fend:
        alertas.append(
            f"Armadura horizontal adotada ({as_horizontal_adotada_cm2:.2f} cm²) < requerida por fendimento ({as_req_cm2:.2f} cm²)."
        )

    aprovado = atende_geom and atende_esm and atende_fend
    return ResultadoBloco1Estaca(
        nk_tf=round(nk_tf, 2),
        nd_kn=round(nd_kn, 2),
        folga_borda_cm=round(folga, 2),
        atende_geometria=atende_geom,
        tensao_contato_pilar_mpa=round(sigma_pilar_mpa, 2),
        tensao_contato_estaca_mpa=round(sigma_estaca_mpa, 2),
        fcd1_limite_mpa=round(limite_mpa, 2),
        atende_esmagamento=atende_esm,
        forca_fendimento_kn=round(f_td_kn, 2),
        as_fendimento_req_cm2=round(as_req_cm2, 2),
        as_horizontal_adotada_cm2=round(as_horizontal_adotada_cm2, 2),
        atende_fendimento=atende_fend,
        volume_concreto_m3=round(geometria.volume_concreto_m3, 4),
        area_forma_m2=round(geometria.area_forma_m2, 3),
        aprovado=aprovado,
        alertas=alertas,
    )
