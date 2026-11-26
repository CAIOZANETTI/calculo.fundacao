"""Dimensionamento determinístico à flexão da laje de fundo de 30 cm sobre malha de estacas/capitéis (NBR 6118:2023)."""

from __future__ import annotations

import math
from dataclasses import dataclass

from fundacao.normas.nbr6118 import ACO_CA50, Aco, ClasseAgressividade, Concreto


@dataclass(frozen=True)
class ResultadoFlexaoLajeFundo:
    vao_m: float
    carga_distribuida_kpa: float
    h_laje_cm: float
    d_util_cm: float
    mk_negativo_knm_m: float
    md_negativo_knm_m: float
    kmd: float
    kx: float
    dominio: str
    as_calc_cm2_m: float
    as_min_cm2_m: float
    as_req_cm2_m: float
    as_existente_pbes_cm2_m: float
    delta_as_cm2_m: float
    delta_aco_total_kg: float
    atende_malha_existente: bool


def verificar_flexao_laje_fundo(
    vao_m: float,
    carga_distribuida_kpa: float,
    area_planta_m2: float,
    as_existente_pbes_cm2_m: float,
    h_laje_cm: float = 30.0,
    cobrimento_cm: float = 4.5,
    bitola_mm: float = 10.0,
    concreto: Concreto = Concreto(fck_mpa=40.0, caa=ClasseAgressividade.IV),
    aco: Aco = ACO_CA50,
    gamma_f: float = 1.4,
    coef_momento_apoio: float = 1.0 / 10.0,  # placa contínua sobre apoios elásticos/capitéis
) -> ResultadoFlexaoLajeFundo:
    """Verifica flexão simples em faixa unitária (b = 1,00 m) da laje de fundo segundo NBR 6118:2023.

    Equações determinísticas (seção retangular sem armadura de compressão):
      M_k = coef_momento · q · L²
      M_d = γ_f · M_k
      k_md = M_d / (b · d² · f_cd)
      k_x = (1 - √(1 - 2 · k_md / 0,85)) / 0,8
      k_z = 1 - 0,4 · k_x
      A_s = M_d / (k_z · d · f_yd)
      A_s,min = ρ_min · b · h  (NBR 6118 Tabela 17.3: ρ_min = 0,187% para C40 -> 5,61 cm²/m em h=30 cm)
    """
    d_cm = h_laje_cm - cobrimento_cm - (bitola_mm / 10.0)
    d_m = d_cm / 100.0
    b_m = 1.0

    mk = coef_momento_apoio * carga_distribuida_kpa * (vao_m ** 2)
    md = gamma_f * mk

    fcd_kpa = concreto.fcd_mpa * 1000.0
    kmd = md / (b_m * (d_m ** 2) * fcd_kpa)
    if kmd >= 0.35:
        raise ValueError(f"Seção superarmada ou fora do domínio 2/3 (kmd={kmd:.3f}) para vão={vao_m:.2f} m.")

    kx = (1.0 - math.sqrt(max(0.0, 1.0 - 2.0 * kmd / 0.85))) / 0.8
    kz = 1.0 - 0.4 * kx
    dominio = "Domínio 2" if kx <= 0.259 else ("Domínio 3 (dúctil)" if kx <= 0.45 else "Domínio 3 (>0,45 — revisar)")

    # fyd em kN/cm² = fyd_mpa / 10
    as_calc_cm2_m = md / (kz * d_m * (aco.fyd_mpa / 10.0))
    # NBR 6118 Tabela 17.3: para C40, rho_min = 0,179% (laje armada em 2 direções -> 0,67*rho_min positivo, 100% negativo)
    as_min_cm2_m = 0.00179 * 100.0 * h_laje_cm
    as_req_cm2_m = max(as_calc_cm2_m, as_min_cm2_m)

    delta_as = max(0.0, as_req_cm2_m - as_existente_pbes_cm2_m)
    # 2 direções × (faixa negativa sobre capitéis ~50% + faixa positiva ~50% = 1,0 face equivalente + ancoragem 15%)
    # 1 cm²/m em 1 m² = 0,785 kg/m²
    delta_kg = area_planta_m2 * (delta_as * 0.785 * 2.0 * 1.15)

    return ResultadoFlexaoLajeFundo(
        vao_m=round(vao_m, 2),
        carga_distribuida_kpa=round(carga_distribuida_kpa, 1),
        h_laje_cm=h_laje_cm,
        d_util_cm=round(d_cm, 1),
        mk_negativo_knm_m=round(mk, 1),
        md_negativo_knm_m=round(md, 1),
        kmd=round(kmd, 4),
        kx=round(kx, 3),
        dominio=dominio,
        as_calc_cm2_m=round(as_calc_cm2_m, 2),
        as_min_cm2_m=round(as_min_cm2_m, 2),
        as_req_cm2_m=round(as_req_cm2_m, 2),
        as_existente_pbes_cm2_m=round(as_existente_pbes_cm2_m, 2),
        delta_as_cm2_m=round(delta_as, 2),
        delta_aco_total_kg=round(delta_kg, 1),
        atende_malha_existente=delta_as <= 1e-6,
    )
