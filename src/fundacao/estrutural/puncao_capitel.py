"""Verificação de punção em laje de fundo / radier e dimensionamento de capitéis (ABNT NBR 6118:2023 Seção 19.5)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from fundacao.normas.nbr6118 import ClasseAgressividade, Concreto, TF_PARA_KN


@dataclass(frozen=True)
class ResultadoPuncaoCapitel:
    nk_tf: float
    nd_kn: float
    diametro_estaca_cm: float
    h_laje_cm: float
    tem_capitel: bool
    l_capitel_cm: float
    h_capitel_total_cm: float
    d_capitel_cm: float
    d_laje_cm: float
    tau_sd_c_mpa: float
    tau_rd2_mpa: float
    atende_c_esmagamento: bool
    tau_sd_c_linha_mpa: float
    tau_rd1_capitel_mpa: float
    atende_c_linha_sem_armadura: bool
    tau_sd_c_duas_linhas_mpa: float
    tau_rd1_laje_mpa: float
    atende_c_duas_linhas_sem_armadura: bool
    dispensa_armadura_puncao: bool
    aprovado_com_ou_sem_studs: bool
    alertas: List[str]


def _tau_rd1_nbr6118_mpa(concreto: Concreto, d_cm: float, rho: float) -> float:
    """Resistência à punção sem armadura transversal τ_Rd1 (MPa) — NBR 6118:2023 item 19.5.3.2."""
    k = 1.0 + math.sqrt(20.0 / d_cm)  # sem limite de 2,0 na revisão NBR 6118:2023 (ou conservador <= 2,0)
    k_cons = min(k, 2.0)
    rho_lim = min(rho, 0.02)
    return 0.13 * k_cons * ((100.0 * rho_lim * concreto.fck_mpa) ** (1.0 / 3.0))


def _tau_rd2_nbr6118_mpa(concreto: Concreto) -> float:
    """Resistência à compressão diagonal na face do apoio τ_Rd2 (MPa) — NBR 6118:2023 item 19.5.3.1."""
    return 0.27 * concreto.alpha_v2 * concreto.fcd_mpa


def verificar_puncao_laje_com_capitel(
    nk_tf: float,
    diametro_estaca_cm: float,
    h_laje_cm: float = 30.0,
    l_capitel_cm: float = 0.0,
    h_capitel_total_cm: float = 30.0,
    rho_laje: float = 0.005,
    rho_capitel: float = 0.006,
    cobrimento_cm: float = 4.5,
    concreto: Concreto = Concreto(fck_mpa=40.0, caa=ClasseAgressividade.IV),
    gamma_f: float = 1.4,
    fator_excentricidade_beta: float = 1.05,
) -> ResultadoPuncaoCapitel:
    """Verifica punção de estaca de grande diâmetro diretamente na laje de fundo com ou sem capitel.

    Contornos críticos (NBR 6118:2023 Seção 19.5):
      - Contorno C  (face da estaca): u0 = π · D
      - Contorno C' (a 2·d_cap da face da estaca, dentro do capitel ou laje): u1 = π · (D + 4·d_cap)
      - Contorno C'' (fora do capitel quadrado de lado l_cap, a 2·d_laje da borda):
          u2 = 4 · l_cap + 4 · π · d_laje
    """
    nd_kn = gamma_f * fator_excentricidade_beta * nk_tf * TF_PARA_KN
    tem_capitel = (l_capitel_cm > diametro_estaca_cm) and (h_capitel_total_cm > h_laje_cm)

    d_laje_cm = h_laje_cm - cobrimento_cm - 1.5
    d_cap_cm = (h_capitel_total_cm if tem_capitel else h_laje_cm) - cobrimento_cm - 1.5

    # Contorno C (esmagamento da biela na face da estaca)
    u0_m = math.pi * (diametro_estaca_cm / 100.0)
    tau_sd_c = (nd_kn / (u0_m * (d_cap_cm / 100.0))) / 1000.0
    tau_rd2 = _tau_rd2_nbr6118_mpa(concreto)
    ok_c = tau_sd_c <= tau_rd2

    # Contorno C' (a 2·d_cap da face da estaca)
    u1_m = math.pi * ((diametro_estaca_cm + 4.0 * d_cap_cm) / 100.0)
    tau_sd_c1 = (nd_kn / (u1_m * (d_cap_cm / 100.0))) / 1000.0
    tau_rd1_cap = _tau_rd1_nbr6118_mpa(concreto, d_cap_cm, rho_capitel if tem_capitel else rho_laje)
    ok_c1_sem_arm = tau_sd_c1 <= tau_rd1_cap

    # Contorno C'' (na laje de fundo fora do capitel, a 2·d_laje da borda do capitel quadrado)
    if tem_capitel:
        u2_m = (4.0 * l_capitel_cm + 4.0 * math.pi * d_laje_cm) / 100.0
        tau_sd_c2 = (nd_kn / (u2_m * (d_laje_cm / 100.0))) / 1000.0
    else:
        tau_sd_c2 = tau_sd_c1
    tau_rd1_laje = _tau_rd1_nbr6118_mpa(concreto, d_laje_cm, rho_laje)
    ok_c2_sem_arm = tau_sd_c2 <= tau_rd1_laje

    dispensa_arm = ok_c and ok_c1_sem_arm and ok_c2_sem_arm
    # Com armadura de punção (studs), τ_Rd3 pode chegar a ~1,5·τ_Rd1 (limitado por τ_Rd2)
    aprovado_com_studs = ok_c and (tau_sd_c1 <= min(1.5 * tau_rd1_cap, tau_rd2)) and (
        tau_sd_c2 <= min(1.5 * tau_rd1_laje, tau_rd2)
    )

    alertas: List[str] = []
    if not ok_c:
        alertas.append(f"Contorno C excede τ_Rd2 ({tau_sd_c:.2f} > {tau_rd2:.2f} MPa): aumentar h do capitel.")
    if not ok_c1_sem_arm:
        alertas.append(
            f"Contorno C' ({tau_sd_c1:.2f} MPa) > τ_Rd1 ({tau_rd1_cap:.2f} MPa): exige armadura de punção ou capitel mais espesso."
        )
    if tem_capitel and not ok_c2_sem_arm:
        alertas.append(
            f"Contorno C'' fora do capitel ({tau_sd_c2:.2f} MPa) > τ_Rd1 da laje ({tau_rd1_laje:.2f} MPa): aumentar largura l_capitel."
        )

    return ResultadoPuncaoCapitel(
        nk_tf=round(nk_tf, 1),
        nd_kn=round(nd_kn, 1),
        diametro_estaca_cm=diametro_estaca_cm,
        h_laje_cm=h_laje_cm,
        tem_capitel=tem_capitel,
        l_capitel_cm=l_capitel_cm,
        h_capitel_total_cm=h_capitel_total_cm if tem_capitel else h_laje_cm,
        d_capitel_cm=round(d_cap_cm, 1),
        d_laje_cm=round(d_laje_cm, 1),
        tau_sd_c_mpa=round(tau_sd_c, 2),
        tau_rd2_mpa=round(tau_rd2, 2),
        atende_c_esmagamento=ok_c,
        tau_sd_c_linha_mpa=round(tau_sd_c1, 2),
        tau_rd1_capitel_mpa=round(tau_rd1_cap, 2),
        atende_c_linha_sem_armadura=ok_c1_sem_arm,
        tau_sd_c_duas_linhas_mpa=round(tau_sd_c2, 2),
        tau_rd1_laje_mpa=round(tau_rd1_laje, 2),
        atende_c_duas_linhas_sem_armadura=ok_c2_sem_arm,
        dispensa_armadura_puncao=dispensa_arm,
        aprovado_com_ou_sem_studs=aprovado_com_studs,
        alertas=alertas,
    )


def dimensionar_capitel_minimo(
    nk_tf: float,
    diametro_estaca_cm: float,
    h_laje_cm: float = 30.0,
    concreto: Concreto = Concreto(fck_mpa=40.0, caa=ClasseAgressividade.IV),
) -> ResultadoPuncaoCapitel:
    """Encontra o menor capitel (h_cap, l_cap) que dispensa armadura de punção (τ_sd ≤ τ_Rd1)."""
    # Testa primeiro sem capitel (direto na laje de 30 cm)
    sem_cap = verificar_puncao_laje_com_capitel(
        nk_tf=nk_tf,
        diametro_estaca_cm=diametro_estaca_cm,
        h_laje_cm=h_laje_cm,
        l_capitel_cm=0.0,
        h_capitel_total_cm=h_laje_cm,
        concreto=concreto,
    )
    if sem_cap.dispensa_armadura_puncao:
        return sem_cap

    # Busca h_capitel (45 a 90 cm, passo 5 cm) e l_capitel (D+30 a 260 cm, passo 10 cm)
    for h_cap in range(45, 95, 5):
        l_min = int(math.ceil((diametro_estaca_cm + 30.0) / 10.0) * 10)
        for l_cap in range(l_min, 270, 10):
            res = verificar_puncao_laje_com_capitel(
                nk_tf=nk_tf,
                diametro_estaca_cm=diametro_estaca_cm,
                h_laje_cm=h_laje_cm,
                l_capitel_cm=float(l_cap),
                h_capitel_total_cm=float(h_cap),
                concreto=concreto,
            )
            if res.dispensa_armadura_puncao:
                return res
    return res
