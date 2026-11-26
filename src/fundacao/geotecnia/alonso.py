"""Método de Alonso (1996) específico para Estacas Hélice Contínua — Velloso & Lopes."""

from __future__ import annotations

import math
from typing import Dict, Tuple

from fundacao.geotecnia.sondagem import Sondagem
from fundacao.normas.nbr6118 import KN_PARA_TF

# Parâmetros calibrados de Alonso (1996) para Hélice Contínua em solos brasileiros:
# (fator_lateral_kpa_por_N, ql_max_kpa, fator_ponta_kpa_por_N, qp_max_kpa)
# Referência: Alonso (1996) / Velloso & Lopes (Fundações — Hélice Contínua):
#   - Atrito lateral limitado (especialmente em argilas e siltes) e ponta reduzida por alívio da hélice
PARAMETROS_ALONSO_HELICE: Dict[str, Tuple[float, float, float, float]] = {
    "areia": (4.0, 120.0, 200.0, 3500.0),
    "silte": (3.2, 100.0, 140.0, 2200.0),
    "argila": (2.8, 90.0, 100.0, 1600.0),
}


def calcular_alonso(
    sondagem: Sondagem,
    diametro_m: float,
    comprimento_m: float,
    cota_arrasamento_m: float | None = None,
    fs: float = 2.0,
) -> Dict[str, float | str]:
    """Calcula a capacidade de carga de estaca Hélice Contínua por Alonso (1996)."""
    prof_ini = 0.0 if cota_arrasamento_m is None else max(0.0, sondagem.profundidade_por_cota(cota_arrasamento_m))
    prof_ponta = prof_ini + comprimento_m

    camadas = sondagem.camadas_no_trecho(prof_ini, prof_ponta)
    perimetro_m = math.pi * diametro_m
    area_ponta_m2 = math.pi * (diametro_m ** 2) / 4.0

    rl_kn = 0.0
    for camada in camadas:
        fl, ql_max, _, _ = PARAMETROS_ALONSO_HELICE[camada.tipo_solo.grupo_generico]
        ql_kpa = min(fl * camada.nspt, ql_max)
        rl_kn += ql_kpa * perimetro_m * camada.espessura_m

    # Ponta: média entre ponta e 1 m acima/abaixo (quando disponível)
    amostras = []
    for dz in (-1.0, 0.0, 1.0):
        z = prof_ponta + dz
        if 0.0 <= z <= sondagem.profundidade_max_m:
            n_val, _ = sondagem.nspt_na_profundidade(z)
            amostras.append(n_val)
    np_med = sum(amostras) / len(amostras)
    _, solo_ponta = sondagem.nspt_na_profundidade(prof_ponta)
    _, _, fp, qp_max = PARAMETROS_ALONSO_HELICE[solo_ponta.grupo_generico]
    qp_kpa = min(fp * np_med, qp_max)
    rp_kn = qp_kpa * area_ponta_m2

    r_ult_kn = rp_kn + rl_kn
    p_adm_kn = r_ult_kn / fs

    return {
        "metodo": "Alonso (1996)",
        "prof_arrasamento_m": round(prof_ini, 3),
        "prof_ponta_m": round(prof_ponta, 3),
        "rp_kn": round(rp_kn, 2),
        "rl_kn": round(rl_kn, 2),
        "r_ult_kn": round(r_ult_kn, 2),
        "p_adm_kn": round(p_adm_kn, 2),
        "p_adm_tf": round(p_adm_kn * KN_PARA_TF, 2),
        "rl_tracao_adm_tf": round((0.7 * rl_kn / fs) * KN_PARA_TF, 2),
    }
