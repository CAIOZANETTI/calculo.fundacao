"""Método semi-empírico de Teixeira (1996) para estacas — Velloso & Lopes (Fundações)."""

from __future__ import annotations

import math
from typing import Dict

from fundacao.geotecnia.sondagem import Sondagem, TipoSolo
from fundacao.normas.nbr6118 import KN_PARA_TF

# Parâmetro α (kPa) de resistência de ponta — Teixeira (1996) para estacas escavadas / hélice contínua
# Referência: Velloso & Lopes, Fundações — Volume Completo (Tabela Teixeira 1996)
ALPHA_TEIXEIRA_ESCAVADA_KPA: Dict[TipoSolo, float] = {
    TipoSolo.ARGILA: 100.0,
    TipoSolo.ARGILA_SILTOSA: 100.0,
    TipoSolo.ARGILA_SILTO_ARENOSA: 110.0,
    TipoSolo.ARGILA_ARENO_SILTOSA: 110.0,
    TipoSolo.ARGILA_ARENOSA: 130.0,
    TipoSolo.SILTE_ARGILOSO: 110.0,
    TipoSolo.SILTE_ARGILO_ARENOSO: 130.0,
    TipoSolo.SILTE: 160.0,
    TipoSolo.SILTE_ARENO_ARGILOSO: 160.0,
    TipoSolo.SILTE_ARENOSO: 210.0,
    TipoSolo.AREIA_ARGILOSA: 210.0,
    TipoSolo.AREIA_ARGILO_SILTOSA: 210.0,
    TipoSolo.AREIA_SILTO_ARGILOSA: 210.0,
    TipoSolo.AREIA_SILTOSA: 270.0,
    TipoSolo.AREIA: 270.0,
}

# Parâmetro β (kPa) de atrito lateral — Teixeira (1996): 4,0 kPa para escavadas/hélice, 5,0 kPa para cravadas
BETA_TEIXEIRA_HELICE_KPA = 4.0


def _nspt_medio_ponta_teixeira(sondagem: Sondagem, prof_ponta_m: float, diametro_m: float) -> float:
    """Média do NSPT no intervalo [prof_ponta - 4D, prof_ponta + 1D] segundo Teixeira (1996)."""
    z_ini = max(0.0, prof_ponta_m - 4.0 * diametro_m)
    z_fim = min(sondagem.profundidade_max_m, prof_ponta_m + 1.0 * diametro_m)
    amostras = []
    z = math.ceil(z_ini)
    while z <= z_fim + 1e-6:
        if 0.0 <= z <= sondagem.profundidade_max_m:
            n_val, _ = sondagem.nspt_na_profundidade(z)
            amostras.append(min(n_val, 40.0))
        z += 1.0
    if not amostras:
        n_val, _ = sondagem.nspt_na_profundidade(prof_ponta_m)
        return min(n_val, 40.0)
    return sum(amostras) / len(amostras)


def calcular_teixeira(
    sondagem: Sondagem,
    diametro_m: float,
    comprimento_m: float,
    cota_arrasamento_m: float | None = None,
    fs: float = 2.0,
    beta_kpa: float = BETA_TEIXEIRA_HELICE_KPA,
) -> Dict[str, float | str]:
    """Calcula a capacidade de carga de estaca Hélice Contínua por Teixeira (1996).

    Fórmulas:
      R_p = α · N_p · A_p           [kN]  (N_p médio entre 4D acima e 1D abaixo da ponta)
      R_l = β · N_l · U · L         [kN]  (N_l médio ao longo do fuste, limitado a 40)
      R_ult = R_p + R_l             [kN]
      P_adm = R_ult / FS            [kN]
    """
    prof_ini = 0.0 if cota_arrasamento_m is None else max(0.0, sondagem.profundidade_por_cota(cota_arrasamento_m))
    prof_ponta = prof_ini + comprimento_m

    camadas = sondagem.camadas_no_trecho(prof_ini, prof_ponta)
    perimetro_m = math.pi * diametro_m
    area_ponta_m2 = math.pi * (diametro_m ** 2) / 4.0

    # Atrito lateral (integração camada a camada, N limitado a 40)
    rl_kn = 0.0
    for camada in camadas:
        n_lim = min(camada.nspt, 40.0)
        rl_kn += beta_kpa * n_lim * perimetro_m * camada.espessura_m

    # Resistência de ponta
    _, solo_ponta = sondagem.nspt_na_profundidade(prof_ponta)
    alpha_kpa = ALPHA_TEIXEIRA_ESCAVADA_KPA[solo_ponta]
    np_medio = _nspt_medio_ponta_teixeira(sondagem, prof_ponta, diametro_m)
    rp_kn = alpha_kpa * np_medio * area_ponta_m2

    r_ult_kn = rp_kn + rl_kn
    p_adm_kn = r_ult_kn / fs

    return {
        "metodo": "Teixeira (1996)",
        "prof_arrasamento_m": round(prof_ini, 3),
        "prof_ponta_m": round(prof_ponta, 3),
        "rp_kn": round(rp_kn, 2),
        "rl_kn": round(rl_kn, 2),
        "r_ult_kn": round(r_ult_kn, 2),
        "p_adm_kn": round(p_adm_kn, 2),
        "p_adm_tf": round(p_adm_kn * KN_PARA_TF, 2),
        "rl_tracao_adm_tf": round((0.7 * rl_kn / fs) * KN_PARA_TF, 2),
    }
