"""Método semi-empírico de Décourt & Quaresma (1978, 1996) para Estacas Hélice Contínua."""

from __future__ import annotations

import math
from typing import Dict

from fundacao.geotecnia.sondagem import Sondagem, TipoSolo
from fundacao.normas.nbr6118 import KN_PARA_TF

# Coeficiente C (kPa) de resistência de ponta — Décourt & Quaresma (1978)
C_DECOURT_KPA: Dict[TipoSolo, float] = {
    TipoSolo.ARGILA: 120.0,
    TipoSolo.ARGILA_SILTOSA: 120.0,
    TipoSolo.ARGILA_SILTO_ARENOSA: 120.0,
    TipoSolo.ARGILA_ARENO_SILTOSA: 120.0,
    TipoSolo.ARGILA_ARENOSA: 120.0,
    TipoSolo.SILTE_ARGILOSO: 200.0,
    TipoSolo.SILTE_ARGILO_ARENOSO: 200.0,
    TipoSolo.SILTE: 200.0,
    TipoSolo.SILTE_ARENO_ARGILOSO: 250.0,
    TipoSolo.SILTE_ARENOSO: 250.0,
    TipoSolo.AREIA_ARGILOSA: 250.0,
    TipoSolo.AREIA_ARGILO_SILTOSA: 250.0,
    TipoSolo.AREIA_SILTO_ARGILOSA: 250.0,
    TipoSolo.AREIA_SILTOSA: 400.0,
    TipoSolo.AREIA: 400.0,
}

# Coeficientes α (ponta) e β (atrito lateral) — Décourt (1996) para Hélice Contínua
ALPHA_HELICE_DECOURT = 0.30
BETA_HELICE_DECOURT = 1.00


def _nspt_ponta_medio(sondagem: Sondagem, prof_ponta_m: float) -> float:
    """Média dos 3 valores de NSPT: na ponta, 1 m acima e 1 m abaixo (quando disponível)."""
    amostras = []
    for dz in (-1.0, 0.0, 1.0):
        z = prof_ponta_m + dz
        if 0.0 <= z <= sondagem.profundidade_max_m:
            n_val, _ = sondagem.nspt_na_profundidade(z)
            amostras.append(n_val)
    return sum(amostras) / len(amostras)


def calcular_decourt_quaresma(
    sondagem: Sondagem,
    diametro_m: float,
    comprimento_m: float,
    cota_arrasamento_m: float | None = None,
    fs: float = 2.0,
    alpha: float = ALPHA_HELICE_DECOURT,
    beta: float = BETA_HELICE_DECOURT,
    nspt_lateral_max: float = 50.0,
) -> Dict[str, float | str]:
    """Calcula a capacidade de carga de estaca Hélice Contínua por Décourt & Quaresma (1978/1996).

    Fórmulas:
      q_p = α · C · N_p                          [kPa]
      q_l = β · 10 · (N_l / 3 + 1)               [kPa], com 3 <= N_l <= nspt_lateral_max
      R_p = q_p · A_p                            [kN]
      R_l = U · sum(q_l,i · ΔL_i)                [kN]
      R_ult = R_p + R_l                          [kN]
      P_adm = R_ult / FS                         [kN] (ou min com 1.3*Rl/FS + Rp/4)
    """
    prof_ini = 0.0 if cota_arrasamento_m is None else max(0.0, sondagem.profundidade_por_cota(cota_arrasamento_m))
    prof_ponta = prof_ini + comprimento_m

    camadas = sondagem.camadas_no_trecho(prof_ini, prof_ponta)
    perimetro_m = math.pi * diametro_m
    area_ponta_m2 = math.pi * (diametro_m ** 2) / 4.0

    # Atrito lateral (kN)
    rl_kn = 0.0
    for camada in camadas:
        n_lim = min(max(camada.nspt, 3.0), nspt_lateral_max)
        ql_kpa = beta * 10.0 * (n_lim / 3.0 + 1.0)
        rl_kn += ql_kpa * perimetro_m * camada.espessura_m

    # Resistência de ponta (kN)
    _, solo_ponta = sondagem.nspt_na_profundidade(prof_ponta)
    c_kpa = C_DECOURT_KPA[solo_ponta]
    np_medio = _nspt_ponta_medio(sondagem, prof_ponta)
    qp_kpa = alpha * c_kpa * np_medio
    rp_kn = qp_kpa * area_ponta_m2

    r_ult_kn = rp_kn + rl_kn
    # Critério clássico NBR 6122 (FS global = 2.0) e critério de recalque de Décourt (Rp/4 + Rl/1.3)
    p_adm_global_kn = r_ult_kn / fs
    p_adm_decourt_kn = rp_kn / 4.0 + rl_kn / 1.3
    p_adm_kn = min(p_adm_global_kn, p_adm_decourt_kn)

    return {
        "metodo": "Décourt-Quaresma (1978/1996)",
        "prof_arrasamento_m": round(prof_ini, 3),
        "prof_ponta_m": round(prof_ponta, 3),
        "rp_kn": round(rp_kn, 2),
        "rl_kn": round(rl_kn, 2),
        "r_ult_kn": round(r_ult_kn, 2),
        "p_adm_kn": round(p_adm_kn, 2),
        "p_adm_tf": round(p_adm_kn * KN_PARA_TF, 2),
        "rl_tracao_adm_tf": round((0.7 * rl_kn / fs) * KN_PARA_TF, 2),
    }
