"""Verificação estrutural de estacas Hélice Contínua (ABNT NBR 6122:2022 e NBR 6118:2023)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from fundacao.normas.nbr6118 import (
    ACO_CA50,
    Aco,
    ClasseAgressividade,
    Concreto,
    KN_PARA_TF,
    TF_PARA_KN,
    selecionar_armadura,
)
from fundacao.normas.nbr6122 import (
    RequisitosHeliceContinua,
    fck_minimo_estaca_helice_mpa,
    tensao_admissivel_estaca_helice_mpa,
)


@dataclass(frozen=True)
class ResultadoEstacaEstrutural:
    diametro_cm: float
    area_concreto_cm2: float
    fck_mpa: float
    caa: str
    fck_min_caa_mpa: float
    atende_durabilidade: bool
    tensao_adm_mpa: float
    carga_estrutural_adm_tf: float
    carga_atuante_tf: float
    tensao_atuante_mpa: float
    taxa_utilizacao_compressao: float
    atende_compressao: bool
    as_min_cm2: float
    as_tracao_cm2: float
    as_adotar_cm2: float
    sugestao_armadura: str
    comprimento_armado_min_m: float
    alertas: List[str]


def verificar_estaca_helice_continua(
    diametro_cm: float,
    carga_atuante_tf: float,
    concreto: Concreto = Concreto(fck_mpa=40.0, caa=ClasseAgressividade.IV),
    aco: Aco = ACO_CA50,
    armada_compressao: bool = False,
    tracao_k_tf: float = 0.0,
    gamma_f: float = 1.4,
) -> ResultadoEstacaEstrutural:
    """Verifica a capacidade estrutural do fuste de estaca Hélice Contínua."""
    req = RequisitosHeliceContinua()
    area_cm2 = math.pi * (diametro_cm ** 2) / 4.0
    area_m2 = area_cm2 * 1e-4

    fck_min = fck_minimo_estaca_helice_mpa(concreto.caa)
    atende_durabilidade = concreto.fck_mpa >= fck_min

    sigma_adm_mpa = tensao_admissivel_estaca_helice_mpa(
        fck_mpa=concreto.fck_mpa,
        armada_compressao=armada_compressao,
    )
    p_est_adm_kn = sigma_adm_mpa * 1000.0 * area_m2
    p_est_adm_tf = p_est_adm_kn * KN_PARA_TF

    carga_atuante_kn = carga_atuante_tf * TF_PARA_KN
    sigma_atuante_mpa = (carga_atuante_kn / area_m2) / 1000.0
    taxa_util = carga_atuante_tf / p_est_adm_tf if p_est_adm_tf > 0 else float("inf")
    atende_comp = carga_atuante_tf <= p_est_adm_tf + 1e-6

    # Armadura longitudinal mínima (0,4% da seção) e eventual tração (subpressão)
    as_min_cm2 = req.taxa_armadura_min_compressao * area_cm2
    if tracao_k_tf > 0.0:
        td_kn = gamma_f * tracao_k_tf * TF_PARA_KN
        as_tracao_cm2 = (td_kn * 10.0) / aco.fyd_mpa  # kN * 10 / MPa = cm²
    else:
        as_tracao_cm2 = 0.0

    as_adotar_cm2 = max(as_min_cm2, as_tracao_cm2)
    opcoes = selecionar_armadura(as_adotar_cm2, bitolas_mm=(10.0, 12.5, 16.0), n_min=req.n_barras_min)
    melhor = min(opcoes, key=lambda o: o["as_efetiva_cm2"])
    sugestao = f"{int(melhor['quantidade'])} Ø {melhor['bitola_mm']:g} mm (As = {melhor['as_efetiva_cm2']:.2f} cm²)"

    alertas: List[str] = []
    if not atende_durabilidade:
        alertas.append(
            f"fck={concreto.fck_mpa:.0f} MPa inferior ao mínimo ({fck_min:.0f} MPa) para CAA {concreto.caa.value}."
        )
    if not atende_comp:
        alertas.append(
            f"Carga atuante ({carga_atuante_tf:.1f} tf) excede capacidade estrutural ({p_est_adm_tf:.1f} tf)."
        )
    if tracao_k_tf > 0.0:
        alertas.append(
            f"Estaca submetida à tração ({tracao_k_tf:.1f} tf): armar ao longo de todo o trecho de atrito necessário."
        )

    return ResultadoEstacaEstrutural(
        diametro_cm=diametro_cm,
        area_concreto_cm2=round(area_cm2, 2),
        fck_mpa=concreto.fck_mpa,
        caa=concreto.caa.value,
        fck_min_caa_mpa=fck_min,
        atende_durabilidade=atende_durabilidade,
        tensao_adm_mpa=round(sigma_adm_mpa, 2),
        carga_estrutural_adm_tf=round(p_est_adm_tf, 2),
        carga_atuante_tf=round(carga_atuante_tf, 2),
        tensao_atuante_mpa=round(sigma_atuante_mpa, 2),
        taxa_utilizacao_compressao=round(taxa_util, 3),
        atende_compressao=atende_comp,
        as_min_cm2=round(as_min_cm2, 2),
        as_tracao_cm2=round(as_tracao_cm2, 2),
        as_adotar_cm2=round(as_adotar_cm2, 2),
        sugestao_armadura=sugestao,
        comprimento_armado_min_m=req.comprimento_min_armado_m,
        alertas=alertas,
    )
