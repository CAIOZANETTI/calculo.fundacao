"""Dimensionamento e verificação de bloco sobre 2 estacas via Bielas e Tirantes (Blévot / NBR 6118:2023)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from fundacao.normas.nbr6118 import (
    ACO_CA50,
    Aco,
    ClasseAgressividade,
    Concreto,
    TF_PARA_KN,
    area_barra_cm2,
)
from fundacao.normas.nbr6122 import RequisitosHeliceContinua


@dataclass(frozen=True)
class GeometriaBloco2Estacas:
    """Dimensões em cm de bloco rígido sobre 2 estacas (padrão PBES: 70 x 190 x 70 cm, e = 120 cm)."""

    largura_b_cm: float = 70.0
    comprimento_l_cm: float = 190.0
    altura_h_cm: float = 70.0
    espacamento_e_cm: float = 120.0
    diametro_estaca_cm: float = 40.0
    embutimento_estaca_cm: float = 5.0
    cobrimento_cm: float = 4.5
    bitola_estribo_mm: float = 8.0
    bitola_tirante_mm: float = 16.0
    pilar_ap_cm: float = 30.0  # espessura da parede/pilar na direção do comprimento L
    pilar_bp_cm: float = 70.0  # largura efetiva de apoio transversal (parede contínua sobre b = 70 cm)

    @property
    def folga_borda_transversal_cm(self) -> float:
        return (self.largura_b_cm - self.diametro_estaca_cm) / 2.0

    @property
    def folga_borda_longitudinal_cm(self) -> float:
        return (self.comprimento_l_cm - self.espacamento_e_cm - self.diametro_estaca_cm) / 2.0

    @property
    def altura_util_d_cm(self) -> float:
        """Altura útil d (cm) descontando embutimento, estribo e centroide do tirante (ou cobrimento)."""
        desconto_inf = max(
            self.embutimento_estaca_cm + self.bitola_estribo_mm / 10.0 + self.bitola_tirante_mm / 20.0,
            self.cobrimento_cm + self.bitola_estribo_mm / 10.0 + self.bitola_tirante_mm / 20.0,
        )
        return self.altura_h_cm - desconto_inf

    @property
    def volume_concreto_m3(self) -> float:
        return (self.largura_b_cm * self.comprimento_l_cm * self.altura_h_cm) * 1e-6

    @property
    def area_forma_m2(self) -> float:
        perimetro_m = 2.0 * (self.largura_b_cm + self.comprimento_l_cm) / 100.0
        return perimetro_m * (self.altura_h_cm / 100.0)


@dataclass(frozen=True)
class ResultadoBloco2Estacas:
    nk_tf: float
    nd_kn: float
    altura_util_d_cm: float
    relacao_e_sobre_d_estaca: float
    angulo_biela_graus: float
    bloco_rigido: bool
    rsd_equilibrio_kn: float
    rsd_blevot_kn: float
    as_tirante_eq_cm2: float
    as_tirante_blevot_cm2: float
    as_min_cm2: float
    as_tirante_adotada_cm2: float
    folga_tirante_pct: float
    atende_tirante: bool
    sigma_biela_pilar_mpa: float
    limite_pilar_nbr6118_mpa: float
    limite_pilar_blevot_mpa: float
    atende_no_pilar_nbr6118: bool
    atende_no_pilar_blevot: bool
    sigma_biela_estaca_mpa: float
    limite_estaca_nbr6118_mpa: float
    limite_estaca_blevot_mpa: float
    atende_no_estaca_nbr6118: bool
    atende_no_estaca_blevot: bool
    as_pele_req_cm2: float
    asw_estribo_req_cm2_m: float
    lb_gancho_nec_cm: float
    comprimento_disp_ancoragem_cm: float
    atende_ancoragem: bool
    volume_concreto_m3: float
    area_forma_m2: float
    aprovado: bool
    alertas: List[str]


def verificar_bloco_2_estacas(
    nk_tf: float,
    geometria: GeometriaBloco2Estacas = GeometriaBloco2Estacas(),
    concreto: Concreto = Concreto(fck_mpa=40.0, caa=ClasseAgressividade.IV),
    aco: Aco = ACO_CA50,
    gamma_f: float = 1.4,
    fator_blevot: float = 1.15,
    n_barras_tirante_adotado: int = 12,
    bitola_tirante_adotada_mm: float = 16.0,
    dobra_vertical_ancoragem_cm: float = 60.0,
) -> ResultadoBloco2Estacas:
    """Verifica bloco rígido sobre 2 estacas pelo método de Bielas e Tirantes (Blévot / NBR 6118:2023).

    Equilíbrio do tirante (Blévot & Frémy, 1967):
      R_sd,eq     = (N_d / 2) · (e/2 - a_p/4) / d = N_d · (2e - a_p) / (8d)
      R_sd,Blévot = 1,15 · R_sd,eq

    Verificação das bielas comprimidas:
      tan(θ)       = d / (e/2 - a_p/4)
      σ_cd,pilar   = N_d / (A_p · sin²θ)       ≤ f_cd1 (NBR 6118) e ≤ 1,40·f_cd (Blévot)
      σ_cd,estaca  = (N_d / 2) / (A_e · sin²θ) ≤ f_cd2 (NBR 6118) e ≤ 0,85·f_cd (Blévot)
    """
    req = RequisitosHeliceContinua()
    nd_kn = gamma_f * nk_tf * TF_PARA_KN

    d_cm = geometria.altura_util_d_cm
    e_cm = geometria.espacamento_e_cm
    ap_cm = geometria.pilar_ap_cm
    bp_cm = geometria.pilar_bp_cm

    braco_horiz_cm = e_cm / 2.0 - ap_cm / 4.0
    if braco_horiz_cm <= 0:
        raise ValueError("Braço horizontal (e/2 - ap/4) deve ser positivo.")

    tan_theta = d_cm / braco_horiz_cm
    theta_rad = math.atan(tan_theta)
    theta_graus = math.degrees(theta_rad)
    sin2_theta = math.sin(theta_rad) ** 2

    # Critério de bloco rígido NBR 6118 item 22.7.2: h >= (L - ap) / 3 e tan(theta) >= 2/3 (~33,7°);
    # Blévot recomenda 45° <= theta <= 55°
    bloco_rigido = (theta_graus >= 40.0) and (geometria.altura_h_cm >= (geometria.comprimento_l_cm - ap_cm) / 3.0)

    # Força de tração no tirante e armadura principal
    rsd_eq_kn = (nd_kn / 2.0) * (braco_horiz_cm / d_cm)
    rsd_blevot_kn = fator_blevot * rsd_eq_kn

    as_eq_cm2 = (rsd_eq_kn * 10.0) / aco.fyd_mpa
    as_blevot_cm2 = (rsd_blevot_kn * 10.0) / aco.fyd_mpa
    as_min_cm2 = 0.0015 * geometria.largura_b_cm * geometria.altura_h_cm
    as_req_final = max(as_blevot_cm2, as_min_cm2)

    as_adotada_cm2 = n_barras_tirante_adotado * area_barra_cm2(bitola_tirante_adotada_mm)
    folga_tirante_pct = ((as_adotada_cm2 / as_req_final) - 1.0) * 100.0 if as_req_final > 0 else 0.0
    atende_tirante = as_adotada_cm2 >= as_req_final

    # Tensões nodais / bielas (MPa)
    area_pilar_m2 = (ap_cm * bp_cm) * 1e-4
    area_estaca_m2 = (math.pi * (geometria.diametro_estaca_cm ** 2) / 4.0) * 1e-4

    sigma_pilar_mpa = (nd_kn / (area_pilar_m2 * sin2_theta)) / 1000.0
    sigma_estaca_mpa = ((nd_kn / 2.0) / (area_estaca_m2 * sin2_theta)) / 1000.0

    lim_pilar_nbr = concreto.fcd1_mpa
    lim_pilar_blevot = 1.40 * concreto.fcd_mpa
    lim_estaca_nbr = concreto.fcd2_mpa
    lim_estaca_blevot = 0.85 * concreto.fcd_mpa

    ok_pilar_nbr = sigma_pilar_mpa <= lim_pilar_nbr
    ok_pilar_blevot = sigma_pilar_mpa <= lim_pilar_blevot
    ok_estaca_nbr = sigma_estaca_mpa <= lim_estaca_nbr
    ok_estaca_blevot = sigma_estaca_mpa <= lim_estaca_blevot

    # Armaduras secundárias (pele lateral >= 20% do tirante; estribos >= 0,14%·b)
    as_pele_req_cm2 = 0.20 * as_blevot_cm2
    asw_req_cm2_m = 0.0014 * geometria.largura_b_cm * 100.0  # cm²/m

    # Ancoragem do tirante a partir da face interna da estaca até a borda + dobra vertical
    lb_basico_cm = concreto.comprimento_ancoragem_basico_cm(bitola_tirante_adotada_mm, aco, boa_aderencia=True)
    # Com gancho (alpha1 = 0,7) e relação As_calc / As_ef
    alpha1 = 0.7
    razao_as = min(1.0, as_blevot_cm2 / as_adotada_cm2) if as_adotada_cm2 > 0 else 1.0
    lb_nec_cm = max(alpha1 * lb_basico_cm * razao_as, 10.0 * (bitola_tirante_adotada_mm / 10.0), 10.0)
    # Comprimento reto disponível a partir do eixo da estaca até a borda (- cobrimento) + dobra
    comp_disp_cm = (
        geometria.diametro_estaca_cm / 2.0
        + geometria.folga_borda_longitudinal_cm
        - geometria.cobrimento_cm
        + dobra_vertical_ancoragem_cm
    )
    atende_anc = comp_disp_cm >= lb_nec_cm

    rel_e_d = e_cm / geometria.diametro_estaca_cm
    alertas: List[str] = []
    if rel_e_d < req.espacamento_min_d:
        alertas.append(f"Espaçamento e/D = {rel_e_d:.2f} < mínimo normativo ({req.espacamento_min_d:.1f}).")
    if not (45.0 <= theta_graus <= 55.0):
        alertas.append(
            f"Ângulo da biela θ = {theta_graus:.1f}° fora da faixa ótima de Blévot (45°–55°); "
            f"{'ainda bloco rígido' if bloco_rigido else 'VERIFICAR RIGIDEZ'}."
        )
    if not atende_tirante:
        alertas.append(
            f"Tirante insuficiente: adotado {as_adotada_cm2:.2f} cm² < requerido {as_req_final:.2f} cm²."
        )
    if not ok_pilar_nbr:
        alertas.append(
            f"Nó CCC sob pilar/parede ({sigma_pilar_mpa:.2f} MPa) excede fcd1 NBR 6118 ({lim_pilar_nbr:.2f} MPa)."
        )
    if not ok_estaca_nbr:
        alertas.append(
            f"Nó CCT sobre estaca ({sigma_estaca_mpa:.2f} MPa) excede fcd2 NBR 6118 ({lim_estaca_nbr:.2f} MPa)."
        )
    if not atende_anc:
        alertas.append(
            f"Ancoragem insuficiente: disponível {comp_disp_cm:.1f} cm < lb,nec = {lb_nec_cm:.1f} cm."
        )

    aprovado = (
        atende_tirante
        and ok_pilar_nbr
        and ok_estaca_nbr
        and atende_anc
        and (rel_e_d >= req.espacamento_min_d)
    )

    return ResultadoBloco2Estacas(
        nk_tf=round(nk_tf, 2),
        nd_kn=round(nd_kn, 2),
        altura_util_d_cm=round(d_cm, 2),
        relacao_e_sobre_d_estaca=round(rel_e_d, 2),
        angulo_biela_graus=round(theta_graus, 2),
        bloco_rigido=bloco_rigido,
        rsd_equilibrio_kn=round(rsd_eq_kn, 2),
        rsd_blevot_kn=round(rsd_blevot_kn, 2),
        as_tirante_eq_cm2=round(as_eq_cm2, 2),
        as_tirante_blevot_cm2=round(as_blevot_cm2, 2),
        as_min_cm2=round(as_min_cm2, 2),
        as_tirante_adotada_cm2=round(as_adotada_cm2, 2),
        folga_tirante_pct=round(folga_tirante_pct, 1),
        atende_tirante=atende_tirante,
        sigma_biela_pilar_mpa=round(sigma_pilar_mpa, 2),
        limite_pilar_nbr6118_mpa=round(lim_pilar_nbr, 2),
        limite_pilar_blevot_mpa=round(lim_pilar_blevot, 2),
        atende_no_pilar_nbr6118=ok_pilar_nbr,
        atende_no_pilar_blevot=ok_pilar_blevot,
        sigma_biela_estaca_mpa=round(sigma_estaca_mpa, 2),
        limite_estaca_nbr6118_mpa=round(lim_estaca_nbr, 2),
        limite_estaca_blevot_mpa=round(lim_estaca_blevot, 2),
        atende_no_estaca_nbr6118=ok_estaca_nbr,
        atende_no_estaca_blevot=ok_estaca_blevot,
        as_pele_req_cm2=round(as_pele_req_cm2, 2),
        asw_estribo_req_cm2_m=round(asw_req_cm2_m, 2),
        lb_gancho_nec_cm=round(lb_nec_cm, 1),
        comprimento_disp_ancoragem_cm=round(comp_disp_cm, 1),
        atende_ancoragem=atende_anc,
        volume_concreto_m3=round(geometria.volume_concreto_m3, 4),
        area_forma_m2=round(geometria.area_forma_m2, 3),
        aprovado=aprovado,
        alertas=alertas,
    )
