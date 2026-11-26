"""Análise de confiabilidade geotécnica (FORM Lognormal — ISO 2394 / JRC Eurocode 7 / Aoki & Cintra)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ResultadoConfiabilidade:
    cenario: str
    r_ult_medio_tf: float
    s_medio_tf: float
    fs_medio: float
    cov_espacial: float
    cov_modelo: float
    cov_resistencia_total: float
    cov_solicitacao: float
    beta_form: float
    probabilidade_ruptura_pf: float
    beta_alvo_redundante: float
    beta_alvo_cc2_50anos: float
    status_confiabilidade: str


def _norm_cdf(x: float) -> float:
    """Função de distribuição acumulada da Normal Padrão Φ(x)."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def calcular_confiabilidade_lognormal(
    cenario: str,
    resistencias_ultimas_tf: List[float],
    solicitacao_caracteristica_tf: float,
    cov_modelo: float = 0.22,
    cov_solicitacao: float = 0.10,
    vies_modelo: float = 1.00,
    vies_solicitacao: float = 0.95,
    beta_alvo_redundante: float = 3.1,
    beta_alvo_cc2_50anos: float = 3.8,
) -> ResultadoConfiabilidade:
    """Calcula índice de confiabilidade β e probabilidade de ruptura P_f (FORM Lognormal exato).

    Referência: ISO 2394 / JRC Eurocode 7 (2024) — Reliability-Based Verification of Limit States
    for Geotechnical Structures & Aoki & Cintra (segurança de fundações):
      - R ~ Lognormal(μ_R, COV_R), com COV_R = √(COV_espacial² + COV_modelo²)
      - S ~ Lognormal(μ_S, COV_S)
      - β = ln[(μ_R / μ_S) · √((1 + COV_S²) / (1 + COV_R²))] / √(ln[(1 + COV_R²)(1 + COV_S²)])
      - P_f = Φ(-β)

    Observação sobre COV_modelo:
      - Métodos semi-empíricos SPT sem prova de carga: COV_modelo ≈ 0,20 a 0,25
      - Com prova de carga estática (PCE) na obra: COV_modelo reduz para ≈ 0,12 a 0,15
    """
    if not resistencias_ultimas_tf:
        raise ValueError("Forneça ao menos um valor de resistência última R_ult.")

    n = len(resistencias_ultimas_tf)
    media_r_raw = sum(resistencias_ultimas_tf) / n
    if n > 1:
        var_r = sum((x - media_r_raw) ** 2 for x in resistencias_ultimas_tf) / (n - 1)
        cov_esp = math.sqrt(var_r) / media_r_raw
    else:
        cov_esp = 0.15  # variabilidade espacial típica quando há apenas 1 furo

    mu_r = media_r_raw * vies_modelo
    mu_s = solicitacao_caracteristica_tf * vies_solicitacao
    cov_r = math.sqrt(cov_esp ** 2 + cov_modelo ** 2)

    ln_arg = (mu_r / mu_s) * math.sqrt((1.0 + cov_solicitacao ** 2) / (1.0 + cov_r ** 2))
    denom = math.sqrt(math.log((1.0 + cov_r ** 2) * (1.0 + cov_solicitacao ** 2)))
    beta = math.log(ln_arg) / denom
    pf = _norm_cdf(-beta)

    if beta >= beta_alvo_cc2_50anos:
        status = f"SEGURO (atende CC2/50a β ≥ {beta_alvo_cc2_50anos:.1f})"
    elif beta >= beta_alvo_redundante:
        status = f"ACEITÁVEL P/ SISTEMA REDUNDANTE ({beta_alvo_redundante:.1f} ≤ β < {beta_alvo_cc2_50anos:.1f} — recomenda-se PCE)"
    else:
        status = f"INSUFICIENTE (β = {beta:.2f} < {beta_alvo_redundante:.1f} — revisar fundação ou comprovar ponta com PCE)"

    return ResultadoConfiabilidade(
        cenario=cenario,
        r_ult_medio_tf=round(mu_r, 1),
        s_medio_tf=round(mu_s, 1),
        fs_medio=round(mu_r / mu_s, 2),
        cov_espacial=round(cov_esp, 3),
        cov_modelo=round(cov_modelo, 3),
        cov_resistencia_total=round(cov_r, 3),
        cov_solicitacao=round(cov_solicitacao, 3),
        beta_form=round(beta, 2),
        probabilidade_ruptura_pf=pf,
        beta_alvo_redundante=beta_alvo_redundante,
        beta_alvo_cc2_50anos=beta_alvo_cc2_50anos,
        status_confiabilidade=status,
    )
