"""Método semi-empírico de Aoki & Velloso (1975) com fatores de Monteiro (1997) para Hélice Contínua."""

from __future__ import annotations

import math
from typing import Dict, Tuple

from fundacao.geotecnia.sondagem import Sondagem, TipoSolo
from fundacao.normas.nbr6118 import KN_PARA_TF

# Tabela de K (MPa) e alpha (%) — Aoki & Velloso (1975)
TABELA_SOLO_AOKI_VELLOSO: Dict[TipoSolo, Tuple[float, float]] = {
    TipoSolo.AREIA: (1.00, 1.4),
    TipoSolo.AREIA_SILTOSA: (0.80, 2.0),
    TipoSolo.AREIA_SILTO_ARGILOSA: (0.70, 2.4),
    TipoSolo.AREIA_ARGILOSA: (0.60, 3.0),
    TipoSolo.AREIA_ARGILO_SILTOSA: (0.50, 2.8),
    TipoSolo.SILTE: (0.40, 3.0),
    TipoSolo.SILTE_ARENOSO: (0.55, 2.2),
    TipoSolo.SILTE_ARENO_ARGILOSO: (0.45, 2.8),
    TipoSolo.SILTE_ARGILOSO: (0.23, 3.4),
    TipoSolo.SILTE_ARGILO_ARENOSO: (0.25, 3.0),
    TipoSolo.ARGILA: (0.20, 6.0),
    TipoSolo.ARGILA_ARENOSA: (0.35, 2.4),
    TipoSolo.ARGILA_ARENO_SILTOSA: (0.30, 2.8),
    TipoSolo.ARGILA_SILTOSA: (0.22, 4.0),
    TipoSolo.ARGILA_SILTO_ARENOSA: (0.33, 3.0),
}

# Fatores F1 (ponta) e F2 (atrito lateral) para Estaca Hélice Contínua (Monteiro, 1997 / Velloso & Lopes)
F1_HELICE_CONTINUA = 2.0
F2_HELICE_CONTINUA = 4.0


def calcular_aoki_velloso(
    sondagem: Sondagem,
    diametro_m: float,
    comprimento_m: float,
    cota_arrasamento_m: float | None = None,
    fs: float = 2.0,
    f1: float = F1_HELICE_CONTINUA,
    f2: float = F2_HELICE_CONTINUA,
) -> Dict[str, float | str]:
    """Calcula a capacidade de carga de estaca Hélice Contínua por Aoki-Velloso (1975/1997).

    Fórmulas:
      r_p = (K * N_p) / F1          [MPa -> kPa = * 1000]
      r_l = (alpha/100 * K * N_l) / F2
      R_p = r_p * A_p               [kN]
      R_l = U * sum(r_l,i * ΔL_i)   [kN]
      R_ult = R_p + R_l             [kN]
      P_adm = R_ult / FS            [kN]
    """
    prof_ini = 0.0 if cota_arrasamento_m is None else max(0.0, sondagem.profundidade_por_cota(cota_arrasamento_m))
    prof_ponta = prof_ini + comprimento_m

    camadas = sondagem.camadas_no_trecho(prof_ini, prof_ponta)
    perimetro_m = math.pi * diametro_m
    area_ponta_m2 = math.pi * (diametro_m ** 2) / 4.0

    # Atrito lateral acumulado (kN)
    rl_kn = 0.0
    for camada in camadas:
        k_mpa, alpha_pct = TABELA_SOLO_AOKI_VELLOSO[camada.tipo_solo]
        rl_kpa = ((alpha_pct / 100.0) * k_mpa * 1000.0 * camada.nspt) / f2
        rl_kn += rl_kpa * perimetro_m * camada.espessura_m

    # Resistência de ponta na cota da ponta (kN)
    nspt_ponta, solo_ponta = sondagem.nspt_na_profundidade(prof_ponta)
    k_ponta_mpa, _ = TABELA_SOLO_AOKI_VELLOSO[solo_ponta]
    rp_kpa = (k_ponta_mpa * 1000.0 * nspt_ponta) / f1
    rp_kn = rp_kpa * area_ponta_m2

    r_ult_kn = rp_kn + rl_kn
    p_adm_kn = r_ult_kn / fs

    return {
        "metodo": "Aoki-Velloso (1975 / Monteiro 1997)",
        "prof_arrasamento_m": round(prof_ini, 3),
        "prof_ponta_m": round(prof_ponta, 3),
        "rp_kn": round(rp_kn, 2),
        "rl_kn": round(rl_kn, 2),
        "r_ult_kn": round(r_ult_kn, 2),
        "p_adm_kn": round(p_adm_kn, 2),
        "p_adm_tf": round(p_adm_kn * KN_PARA_TF, 2),
        "rl_tracao_adm_tf": round((0.7 * rl_kn / fs) * KN_PARA_TF, 2),
    }
