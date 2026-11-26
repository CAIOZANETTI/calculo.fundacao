"""Análise de fundação direta (radier/sapata): capacidade de carga (Vesic) e recalque por adensamento 1D."""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import yaml


@dataclass(frozen=True)
class ParametrosSoloDireta:
    """Parâmetros geotécnicos de ensaios de cisalhamento direto e adensamento unidimensional."""

    nome: str
    coesao_kpa: float
    angulo_atrito_graus: float
    gamma_nat_kn_m3: float
    e0: float
    tensao_pre_adensamento_kpa: float
    cc: float
    cr: float


@dataclass(frozen=True)
class ResultadoVesic:
    amostra: str
    b_m: float
    l_m: float
    df_m: float
    q_ult_kpa: float
    q_adm_kpa: float
    fs: float


@dataclass(frozen=True)
class ResultadoTrocaSolo:
    espessura_troca_m: float
    espessura_mole_remanescente_m: float
    recalque_adensamento_liq_cm: float
    recalque_adensamento_bruto_cm: float
    recalque_silte_subjacente_cm: float
    recalque_total_liq_cm: float
    recalque_total_bruto_cm: float
    atende_limite_els: bool


def calcular_capacidade_vesic(
    solo: ParametrosSoloDireta,
    b_m: float,
    l_m: float,
    df_m: float = 1.5,
    fs: float = 3.0,
) -> ResultadoVesic:
    """Capacidade de carga de fundação superficial retangular pelo método de Vesic (1973)."""
    phi = math.radians(solo.angulo_atrito_graus)
    if phi > 1e-6:
        nq = math.exp(math.pi * math.tan(phi)) * (math.tan(math.radians(45.0) + phi / 2.0) ** 2)
        nc = (nq - 1.0) / math.tan(phi)
    else:
        nq = 1.0
        nc = 5.14
    ngamma = 2.0 * (nq + 1.0) * math.tan(phi)

    sc = 1.0 + (b_m / l_m) * (nq / nc)
    sq = 1.0 + (b_m / l_m) * math.tan(phi)
    sg = max(0.6, 1.0 - 0.4 * (b_m / l_m))

    q_sobrecarga = solo.gamma_nat_kn_m3 * df_m
    q_ult = (
        solo.coesao_kpa * nc * sc
        + q_sobrecarga * nq * sq
        + 0.5 * solo.gamma_nat_kn_m3 * b_m * ngamma * sg
    )
    return ResultadoVesic(
        amostra=solo.nome,
        b_m=b_m,
        l_m=l_m,
        df_m=df_m,
        q_ult_kpa=round(q_ult, 1),
        q_adm_kpa=round(q_ult / fs, 1),
        fs=fs,
    )


def calcular_recalque_adensamento_cm(
    solo: ParametrosSoloDireta,
    q_aplicada_kpa: float,
    b_m: float,
    l_m: float,
    z_ini_m: float,
    z_fim_m: float,
    z_na_m: float = 8.0,
    n_subcamadas: int = 20,
) -> float:
    """Recalque por adensamento unidimensional (cm) com propagação de tensões 2:1.

    Usa a curva edométrica bilinear (Cr até σ'vm e Cc acima de σ'vm).
    """
    if z_fim_m <= z_ini_m or q_aplicada_kpa <= 0.0:
        return 0.0

    dz = (z_fim_m - z_ini_m) / n_subcamadas
    dh_m = 0.0
    for i in range(n_subcamadas):
        z = z_ini_m + (i + 0.5) * dz
        z_rel = z - z_ini_m
        sv0 = solo.gamma_nat_kn_m3 * min(z, z_na_m) + max(0.0, solo.gamma_nat_kn_m3 - 9.81) * max(
            0.0, z - z_na_m
        )
        sv0 = max(sv0, 1.0)
        ds = q_aplicada_kpa * (b_m * l_m) / ((b_m + z_rel) * (l_m + z_rel))
        svf = sv0 + ds
        svm = solo.tensao_pre_adensamento_kpa

        if svf <= svm:
            dh_i = (dz / (1.0 + solo.e0)) * solo.cr * math.log10(svf / sv0)
        elif sv0 >= svm:
            dh_i = (dz / (1.0 + solo.e0)) * solo.cc * math.log10(svf / sv0)
        else:
            dh_i = (dz / (1.0 + solo.e0)) * (
                solo.cr * math.log10(svm / sv0) + solo.cc * math.log10(svf / svm)
            )
        dh_m += dh_i

    return round(dh_m * 100.0, 2)


def estudo_troca_solo(
    solo: ParametrosSoloDireta,
    q_bruta_kpa: float,
    b_m: float,
    l_m: float,
    z_base_laje_m: float,
    z_fim_argila_mole_m: float,
    espessuras_troca_m: List[float],
    z_topo_rocha_m: float = 14.0,
    z_na_m: float = 8.0,
    es_silte_kpa: float = 30_000.0,
    recalque_limite_cm: float = 3.0,
) -> List[ResultadoTrocaSolo]:
    """Avalia o efeito da substituição parcial ou integral da argila mole (rachão / solo-cimento)."""
    q_liq = max(0.0, q_bruta_kpa - solo.gamma_nat_kn_m3 * z_base_laje_m)
    resultados: List[ResultadoTrocaSolo] = []

    for troca in espessuras_troca_m:
        z_ini = z_base_laje_m + troca
        rem = max(0.0, z_fim_argila_mole_m - z_ini)
        rec_liq = calcular_recalque_adensamento_cm(
            solo=solo,
            q_aplicada_kpa=q_liq,
            b_m=b_m,
            l_m=l_m,
            z_ini_m=z_ini,
            z_fim_m=z_fim_argila_mole_m,
            z_na_m=z_na_m,
        )
        rec_brt = calcular_recalque_adensamento_cm(
            solo=solo,
            q_aplicada_kpa=q_bruta_kpa,
            b_m=b_m,
            l_m=l_m,
            z_ini_m=z_ini,
            z_fim_m=z_fim_argila_mole_m,
            z_na_m=z_na_m,
        )
        esp_silte = max(0.0, z_topo_rocha_m - max(z_ini, z_fim_argila_mole_m))
        rec_silte = round((q_liq * 0.5 * esp_silte / es_silte_kpa) * 100.0, 2)
        tot_liq = round(rec_liq + rec_silte, 2)
        tot_brt = round(rec_brt + rec_silte, 2)

        resultados.append(
            ResultadoTrocaSolo(
                espessura_troca_m=round(troca, 2),
                espessura_mole_remanescente_m=round(rem, 2),
                recalque_adensamento_liq_cm=rec_liq,
                recalque_adensamento_bruto_cm=rec_brt,
                recalque_silte_subjacente_cm=rec_silte,
                recalque_total_liq_cm=tot_liq,
                recalque_total_bruto_cm=tot_brt,
                atende_limite_els=tot_liq <= recalque_limite_cm,
            )
        )
    return resultados


def carregar_ensaios_yaml(caminho: str | Path) -> Dict[str, ParametrosSoloDireta]:
    """Carrega amostras de ensaios geotécnicos (cisalhamento + adensamento) de um YAML."""
    with Path(caminho).open("r", encoding="utf-8") as fh:
        dados = yaml.safe_load(fh)
    amostras: Dict[str, ParametrosSoloDireta] = {}
    for item in dados["amostras"]:
        amostra = ParametrosSoloDireta(
            nome=str(item["nome"]),
            coesao_kpa=float(item["coesao_kpa"]),
            angulo_atrito_graus=float(item["angulo_atrito_graus"]),
            gamma_nat_kn_m3=float(item["gamma_nat_kn_m3"]),
            e0=float(item.get("e0", 1.45)),
            tensao_pre_adensamento_kpa=float(item.get("tensao_pre_adensamento_kpa", 85.0)),
            cc=float(item.get("cc", 0.48)),
            cr=float(item.get("cr", 0.07)),
        )
        amostras[amostra.nome] = amostra
    return amostras


@dataclass(frozen=True)
class ResultadoTempoAdensamento:
    espessura_camada_mole_m: float
    distancia_drenagem_hd_m: float
    cv_cm2_s: float
    t50_dias: float
    t90_dias: float
    fator_skempton_bjerrum_mu: float
    recalque_1d_cm: float
    recalque_corrigido_sb_cm: float


def calcular_tempo_adensamento(
    espessura_camada_mole_m: float,
    recalque_1d_cm: float,
    cv_cm2_s: float = 0.0085,  # valor real medido nos ensaios AI-01 / AI-02 (0,0079 a 0,0144 cm²/s)
    dupla_drenagem: bool = True,
    fator_skempton_bjerrum_mu: float = 0.80,
) -> ResultadoTempoAdensamento:
    """Calcula tempo para 50% e 90% de adensamento (Terzaghi 1D) e recalque corrigido por Skempton-Bjerrum.

    Fórmulas:
      t = (T_v · H_d²) / c_v    (T_50 = 0,197; T_90 = 0,848)
      S_SB = μ · S_1D           (μ ≈ 0,75–0,85 para argilas lateríticas / sobreadensadas)
    """
    hd_m = espessura_camada_mole_m / 2.0 if dupla_drenagem else espessura_camada_mole_m
    hd_cm = hd_m * 100.0
    t50_s = 0.197 * (hd_cm ** 2) / cv_cm2_s
    t90_s = 0.848 * (hd_cm ** 2) / cv_cm2_s
    seg_dia = 86400.0
    return ResultadoTempoAdensamento(
        espessura_camada_mole_m=round(espessura_camada_mole_m, 2),
        distancia_drenagem_hd_m=round(hd_m, 2),
        cv_cm2_s=cv_cm2_s,
        t50_dias=round(t50_s / seg_dia, 1),
        t90_dias=round(t90_s / seg_dia, 1),
        fator_skempton_bjerrum_mu=fator_skempton_bjerrum_mu,
        recalque_1d_cm=round(recalque_1d_cm, 2),
        recalque_corrigido_sb_cm=round(recalque_1d_cm * fator_skempton_bjerrum_mu, 2),
    )


def tensao_ponta_rocha_necessaria_mpa(
    carga_alvo_tf: float,
    rl_solo_ult_tf: float,
    diametro_cm: float,
    fs: float = 2.0,
) -> float:
    """Calcula a tensão última de ponta na rocha q_p,ult (MPa) que a estaca precisaria mobilizar
    (e comprovar via PCE) para atingir carga_alvo_tf quando o atrito lateral em solo não basta.
    """
    rp_ult_nec_tf = max(0.0, fs * carga_alvo_tf - rl_solo_ult_tf)
    area_m2 = math.pi * ((diametro_cm / 100.0) ** 2) / 4.0
    rp_ult_kn = rp_ult_nec_tf * 9.80665
    return round((rp_ult_kn / area_m2) / 1000.0, 2)
