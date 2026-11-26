"""Efeito de grupo de estacas e Radier Estaqueado (PDR — Poulos, Davis & Randolph / Velloso & Lopes)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from fundacao.normas.nbr6118 import KN_PARA_TF, TF_PARA_KN


@dataclass(frozen=True)
class ResultadoGrupoEstacas:
    n_linhas: int
    n_colunas: int
    n_estacas: int
    espacamento_sobre_d: float
    eficiencia_converse_labarre: float
    recalque_elastico_fuste_mm: float
    recalque_solo_abaixo_2_3_l_mm: float
    recalque_total_grupo_mm: float


@dataclass(frozen=True)
class ResultadoRadierEstaqueado:
    n_estacas: int
    diametro_cm: float
    comprimento_m: float
    carga_total_tf: float
    rigidez_radier_kr_kn_m: float
    rigidez_grupo_kp_kn_m: float
    rigidez_radier_estaqueado_kpr_kn_m: float
    fator_interacao_alpha_rp: float
    parcela_carga_radier_pct: float
    parcela_carga_estacas_pct: float
    carga_media_por_estaca_tf: float
    tensao_contato_radier_kpa: float
    recalque_radier_isolado_mm: float
    recalque_radier_estaqueado_mm: float
    reducao_recalque_pct: float
    atende_recalque_els: bool


def calcular_grupo_estacas(
    n_linhas: int,
    n_colunas: int,
    diametro_m: float,
    comprimento_m: float,
    espacamento_m: float,
    carga_total_tf: float,
    es_solo_ponta_kpa: float = 35_000.0,
    espessura_solo_abaixo_2_3_l_m: float = 4.0,
    e_concreto_kpa: float = 30_000_000.0,
) -> ResultadoGrupoEstacas:
    """Calcula eficiência Converse-Labarre e recalque de grupo pelo método da Sapata Equivalente (2L/3)."""
    n_est = n_linhas * n_colunas
    theta_deg = math.degrees(math.atan(diametro_m / espacamento_m))
    if n_linhas == 1 and n_colunas == 1:
        eta = 1.0
    else:
        eta = 1.0 - (theta_deg / 90.0) * (((n_linhas - 1) * n_colunas + (n_colunas - 1) * n_linhas) / n_est)

    # Encurtamento elástico do fuste (xi ≈ 0.6 para estaca predominantemente de atrito + ponta)
    area_est = math.pi * (diametro_m ** 2) / 4.0
    p_est_kn = (carga_total_tf * TF_PARA_KN) / n_est
    w_fuste_m = 0.65 * (p_est_kn * comprimento_m) / (area_est * e_concreto_kpa)

    # Sapata equivalente em 2L/3 com propagação 2:1 até o topo rochoso
    bg = (n_linhas - 1) * espacamento_m + diametro_m
    lg = (n_colunas - 1) * espacamento_m + diametro_m
    z_meio = espessura_solo_abaixo_2_3_l_m / 2.0
    q_eq_kpa = (carga_total_tf * TF_PARA_KN) / ((bg + z_meio) * (lg + z_meio))
    w_solo_m = (q_eq_kpa * espessura_solo_abaixo_2_3_l_m) / es_solo_ponta_kpa

    return ResultadoGrupoEstacas(
        n_linhas=n_linhas,
        n_colunas=n_colunas,
        n_estacas=n_est,
        espacamento_sobre_d=round(espacamento_m / diametro_m, 2),
        eficiencia_converse_labarre=round(eta, 3),
        recalque_elastico_fuste_mm=round(w_fuste_m * 1000.0, 2),
        recalque_solo_abaixo_2_3_l_mm=round(w_solo_m * 1000.0, 2),
        recalque_total_grupo_mm=round((w_fuste_m + w_solo_m) * 1000.0, 2),
    )


def calcular_radier_estaqueado_pdr(
    b_m: float,
    l_m: float,
    carga_total_tf: float,
    n_estacas: int,
    diametro_m: float,
    comprimento_m: float,
    es_solo_superficial_kpa: float = 4_500.0,
    es_solo_profundo_kpa: float = 35_000.0,
    poisson: float = 0.35,
    e_concreto_kpa: float = 30_000_000.0,
    limite_recalque_mm: float = 25.0,
) -> ResultadoRadierEstaqueado:
    """Dimensionamento preliminar de Radier Estaqueado pelo método PDR (Poulos, Davis & Randolph, 2001).

    Referência: Poulos (2001) / Randolph (1994) / Velloso & Lopes (Fundações — Cap. Radiers Estaqueados):
      - Rigidez do radier isolado: K_r ≈ (E_s · sqrt(B·L)) / ((1 - ν²) · I_w)
      - Rigidez de 1 estaca (Randolph & Wroth): K_p1
      - Rigidez do grupo de n estacas: K_p = K_p1 · sqrt(n) · (s/D)^0.15  (aprox. conservadora de interação)
      - Fator de interação radier-estaca: α_rp = 1 - ln(r_c / r_0) / ζ
      - Rigidez combinada: K_pr = (K_p + K_r · (1 - 2·α_rp)) / (1 - (K_r / K_p) · α_rp²)
      - Fração de carga no radier: X = ((1 - α_rp) · K_r) / (K_p + (1 - 2·α_rp) · K_r)
    """
    q_total_kn = carga_total_tf * TF_PARA_KN
    area_radier = b_m * l_m

    # Rigidez do radier isolado sobre camada compressível (fator de forma médio Iw ≈ 0,88 p/ radier rígido)
    iw = 0.88
    kr = (es_solo_superficial_kpa * math.sqrt(area_radier)) / ((1.0 - poisson ** 2) * iw)

    # Rigidez de estaca isolada (Randolph & Wroth, 1978)
    g_prof = es_solo_profundo_kpa / (2.0 * (1.0 + poisson))
    r0 = diametro_m / 2.0
    rm = max(2.5 * comprimento_m * (1.0 - poisson), 5.0 * r0)
    zeta = math.log(rm / r0)
    mu_l = math.sqrt(2.0 / (zeta * (e_concreto_kpa / g_prof))) * (comprimento_m / r0)
    tanh_mul = math.tanh(mu_l) / mu_l if mu_l > 1e-6 else 1.0
    eta_ponta = 1.0  # ponta apoiada em estrato rijo/rocha
    kp1_num = (4.0 / (1.0 - poisson)) * eta_ponta + (2.0 * math.pi / zeta) * (comprimento_m / r0) * tanh_mul
    kp1_den = 1.0 + (4.0 / (math.pi * (1.0 - poisson))) * (g_prof / e_concreto_kpa) * (comprimento_m / r0) * tanh_mul
    kp1 = g_prof * r0 * (kp1_num / kp1_den)

    # Espaçamento médio das estacas sob o radier e rigidez do grupo (Fleming/Randolph: expoente ~0.55)
    s_med = math.sqrt(area_radier / max(n_estacas, 1))
    kp = kp1 * (n_estacas ** 0.58) * min(1.2, max(0.8, (s_med / (4.0 * diametro_m)) ** 0.15))

    # Fator de interação radier-estaca α_rp (Randolph 1994)
    rc = math.sqrt(area_radier / (math.pi * max(n_estacas, 1)))
    alpha_rp = max(0.0, min(0.80, 1.0 - math.log(max(rc / r0, 1.1)) / max(zeta, 1.5)))

    # Rigidez combinada K_pr e partilha de carga
    denom = 1.0 - (kr / kp) * (alpha_rp ** 2)
    denom = max(denom, 0.25)
    kpr = (kp + kr * (1.0 - 2.0 * alpha_rp)) / denom

    x_radier = ((1.0 - alpha_rp) * kr) / (kp + (1.0 - 2.0 * alpha_rp) * kr)
    x_radier = max(0.0, min(0.85, x_radier))
    x_estacas = 1.0 - x_radier

    w_radier_isolado_mm = (q_total_kn / kr) * 1000.0
    w_pr_mm = (q_total_kn / kpr) * 1000.0
    reducao_pct = (1.0 - w_pr_mm / w_radier_isolado_mm) * 100.0 if w_radier_isolado_mm > 0 else 0.0

    carga_por_estaca_tf = (q_total_kn * x_estacas / max(n_estacas, 1)) * KN_PARA_TF
    tensao_radier_kpa = (q_total_kn * x_radier) / area_radier

    return ResultadoRadierEstaqueado(
        n_estacas=n_estacas,
        diametro_cm=round(diametro_m * 100.0, 1),
        comprimento_m=comprimento_m,
        carga_total_tf=round(carga_total_tf, 1),
        rigidez_radier_kr_kn_m=round(kr, 1),
        rigidez_grupo_kp_kn_m=round(kp, 1),
        rigidez_radier_estaqueado_kpr_kn_m=round(kpr, 1),
        fator_interacao_alpha_rp=round(alpha_rp, 3),
        parcela_carga_radier_pct=round(x_radier * 100.0, 1),
        parcela_carga_estacas_pct=round(x_estacas * 100.0, 1),
        carga_media_por_estaca_tf=round(carga_por_estaca_tf, 1),
        tensao_contato_radier_kpa=round(tensao_radier_kpa, 1),
        recalque_radier_isolado_mm=round(w_radier_isolado_mm, 1),
        recalque_radier_estaqueado_mm=round(w_pr_mm, 1),
        reducao_recalque_pct=round(reducao_pct, 1),
        atende_recalque_els=w_pr_mm <= limite_recalque_mm,
    )


@dataclass(frozen=True)
class ComparativoIsoladaVsConjunto:
    """Compara o comportamento de 1 estaca isolada (PCE) versus o conjunto inteiro trabalhando sob o tanque."""

    nome: str
    n_estacas: int
    diametro_cm: float
    espacamento_medio_m: float
    espacamento_sobre_d: float
    eficiencia_converse_labarre: float
    rigidez_estaca_isolada_kp1_kn_m: float
    recalque_estaca_isolada_mm: float
    recalque_conjunto_pdr_mm: float
    recalque_conjunto_2l3_mm: float
    fator_amplificacao_recalque_rs: float
    classificacao_interferencia: str


def comparar_isolada_vs_conjunto(
    nome: str,
    b_m: float,
    l_m: float,
    carga_total_tf: float,
    n_linhas: int,
    n_colunas: int,
    n_estacas_reais: int,
    diametro_m: float,
    comprimento_m: float,
    espacamento_m: float,
    es_solo_superficial_kpa: float = 4_500.0,
    es_solo_profundo_kpa: float = 35_000.0,
    poisson: float = 0.35,
    e_concreto_kpa: float = 30_000_000.0,
) -> ComparativoIsoladaVsConjunto:
    """Quantifica a interferência estaca-estaca (Poulos & Davis / Randolph & Wroth / Velloso & Lopes).

    Demonstra por que o recalque medido em uma estaca isolada na PCE (w_1 ≈ 1–3 mm) é multiplicado
    pelo fator de amplificação de grupo R_s = w_grupo / w_1 quando dezenas de estacas atuam juntas
    com superposição de bulbos de tensão no subsolo.
    """
    pdr = calcular_radier_estaqueado_pdr(
        b_m=b_m,
        l_m=l_m,
        carga_total_tf=carga_total_tf,
        n_estacas=n_estacas_reais,
        diametro_m=diametro_m,
        comprimento_m=comprimento_m,
        es_solo_superficial_kpa=es_solo_superficial_kpa,
        es_solo_profundo_kpa=es_solo_profundo_kpa,
        poisson=poisson,
        e_concreto_kpa=e_concreto_kpa,
    )
    grp = calcular_grupo_estacas(
        n_linhas=n_linhas,
        n_colunas=n_colunas,
        diametro_m=diametro_m,
        comprimento_m=comprimento_m,
        espacamento_m=espacamento_m,
        carga_total_tf=carga_total_tf,
        es_solo_ponta_kpa=es_solo_profundo_kpa,
        e_concreto_kpa=e_concreto_kpa,
    )

    # Rigidez da estaca isolada K_p1 (Randolph & Wroth)
    g_prof = es_solo_profundo_kpa / (2.0 * (1.0 + poisson))
    r0 = diametro_m / 2.0
    rm = max(2.5 * comprimento_m * (1.0 - poisson), 5.0 * r0)
    zeta = math.log(rm / r0)
    mu_l = math.sqrt(2.0 / (zeta * (e_concreto_kpa / g_prof))) * (comprimento_m / r0)
    tanh_mul = math.tanh(mu_l) / mu_l if mu_l > 1e-6 else 1.0
    kp1_num = (4.0 / (1.0 - poisson)) + (2.0 * math.pi / zeta) * (comprimento_m / r0) * tanh_mul
    kp1_den = 1.0 + (4.0 / (math.pi * (1.0 - poisson))) * (g_prof / e_concreto_kpa) * (comprimento_m / r0) * tanh_mul
    kp1 = g_prof * r0 * (kp1_num / kp1_den)

    p_est_kn = (carga_total_tf * TF_PARA_KN) / max(n_estacas_reais, 1)
    w1_mm = (p_est_kn / kp1) * 1000.0
    rs = pdr.recalque_radier_estaqueado_mm / w1_mm if w1_mm > 1e-6 else 1.0

    s_sobre_d = espacamento_m / diametro_m
    if s_sobre_d < 3.0:
        clas = "ALTA interferência (s/D < 3,0 — superposição severa de bulbos, típico de blocos duplos)"
    elif s_sobre_d < 4.5:
        clas = "MODERADA interferência (3,0 ≤ s/D < 4,5 — atende NBR 6122 com boa distribuição)"
    else:
        clas = "BAIXA interferência (s/D ≥ 4,5 — estacas bem espaçadas, mínima sobreposição de bulbos)"

    return ComparativoIsoladaVsConjunto(
        nome=nome,
        n_estacas=n_estacas_reais,
        diametro_cm=round(diametro_m * 100.0, 1),
        espacamento_medio_m=round(espacamento_m, 2),
        espacamento_sobre_d=round(s_sobre_d, 2),
        eficiencia_converse_labarre=grp.eficiencia_converse_labarre,
        rigidez_estaca_isolada_kp1_kn_m=round(kp1, 1),
        recalque_estaca_isolada_mm=round(w1_mm, 2),
        recalque_conjunto_pdr_mm=pdr.recalque_radier_estaqueado_mm,
        recalque_conjunto_2l3_mm=grp.recalque_total_grupo_mm,
        fator_amplificacao_recalque_rs=round(rs, 2),
        classificacao_interferencia=clas,
    )

