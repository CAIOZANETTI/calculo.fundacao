"""Método de Antunes & Cabral (1996) específico para Estacas Hélice Contínua Monitoradas."""

from __future__ import annotations

import math
from typing import Dict, Tuple

from fundacao.geotecnia.sondagem import Sondagem
from fundacao.normas.nbr6118 import KN_PARA_TF

# Parâmetros de Antunes & Cabral (1996) por grupo de solo:
# (beta1_pct [%], beta2_pct [%], ql_max [kPa], qp_max [kPa])
# onde q_l = (beta1_pct / 100) * N [MPa] = beta1_pct * 10 * N [kPa], limitado a ql_max
#      q_p = (beta2_pct / 100) * N_p [MPa] = beta2_pct * 10 * N_p [kPa], limitado a qp_max
# Valores médios conservadores da faixa publicada por Antunes & Cabral (1996):
#   Areias:  β1 = 0,40–0,50%, β2 = 2,0–2,5% (limites ql_max = 100 kPa, qp_max = 4000 kPa)
#   Siltes:  β1 = 0,25–0,40%, β2 = 1,0–2,0% (limites ql_max = 100 kPa, qp_max = 2500 kPa)
#   Argilas: β1 = 0,20–0,35%, β2 = 1,0–1,5% (limites ql_max = 100 kPa, qp_max = 2000 kPa)
PARAMETROS_ANTUNES_CABRAL: Dict[str, Tuple[float, float, float, float]] = {
    "areia": (0.45, 2.00, 100.0, 4000.0),
    "silte": (0.30, 1.50, 100.0, 2500.0),
    "argila": (0.25, 1.00, 100.0, 2000.0),
}


def calcular_antunes_cabral(
    sondagem: Sondagem,
    diametro_m: float,
    comprimento_m: float,
    cota_arrasamento_m: float | None = None,
    fs: float = 2.0,
) -> Dict[str, float | str]:
    """Calcula a capacidade de carga de estaca Hélice Contínua por Antunes & Cabral (1996)."""
    prof_ini = 0.0 if cota_arrasamento_m is None else max(0.0, sondagem.profundidade_por_cota(cota_arrasamento_m))
    prof_ponta = prof_ini + comprimento_m

    camadas = sondagem.camadas_no_trecho(prof_ini, prof_ponta)
    perimetro_m = math.pi * diametro_m
    area_ponta_m2 = math.pi * (diametro_m ** 2) / 4.0

    rl_kn = 0.0
    for camada in camadas:
        beta1_pct, _, ql_max_kpa, _ = PARAMETROS_ANTUNES_CABRAL[camada.tipo_solo.grupo_generico]
        ql_kpa = min(beta1_pct * 10.0 * camada.nspt, ql_max_kpa)
        rl_kn += ql_kpa * perimetro_m * camada.espessura_m

    nspt_ponta, solo_ponta = sondagem.nspt_na_profundidade(prof_ponta)
    _, beta2_pct, _, qp_max_kpa = PARAMETROS_ANTUNES_CABRAL[solo_ponta.grupo_generico]
    qp_kpa = min(beta2_pct * 10.0 * nspt_ponta, qp_max_kpa)
    rp_kn = qp_kpa * area_ponta_m2

    r_ult_kn = rp_kn + rl_kn
    p_adm_kn = r_ult_kn / fs

    return {
        "metodo": "Antunes-Cabral (1996)",
        "prof_arrasamento_m": round(prof_ini, 3),
        "prof_ponta_m": round(prof_ponta, 3),
        "rp_kn": round(rp_kn, 2),
        "rl_kn": round(rl_kn, 2),
        "r_ult_kn": round(r_ult_kn, 2),
        "p_adm_kn": round(p_adm_kn, 2),
        "p_adm_tf": round(p_adm_kn * KN_PARA_TF, 2),
        "rl_tracao_adm_tf": round((0.7 * rl_kn / fs) * KN_PARA_TF, 2),
    }
