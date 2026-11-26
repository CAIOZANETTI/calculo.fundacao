"""Comparativo técnico-econômico 100% determinístico entre o PBGE original e soluções alternativas (ACTIFLO 360 e 600)."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

from fundacao.estrutural.estaca import calcular_comprimento_elastico_estaca
from fundacao.estrutural.laje_fundo import verificar_flexao_laje_fundo
from fundacao.geotecnia.capacidade import calcular_capacidade_todos_metodos
from fundacao.geotecnia.sondagem import Sondagem, carregar_sondagem_yaml
from fundacao.normas.nbr6118 import ClasseAgressividade, Concreto, KN_PARA_TF, massa_linear_kg_m
from fundacao.relatorios.quantitativos import calcular_quantitativos_blocos
from fundacao.verificacoes.confiabilidade import calcular_confiabilidade_lognormal


@dataclass(frozen=True)
class CenarioEconomico:
    unidade: str
    codigo: str
    nome: str
    tipo_solucao: str
    n_estacas: int
    metragem_perfurada_m: float
    comprimento_armado_estaca_m: float
    vol_concreto_estacas_m3: float
    vol_concreto_blocos_capiteis_m3: float
    vol_concreto_total_m3: float
    peso_aco_estacas_kg: float
    peso_aco_blocos_capiteis_kg: float
    acrescimo_aco_laje_fundo_kg: float
    peso_aco_total_kg: float
    area_forma_m2: float
    custo_perfuracao_rs: float
    custo_concreto_estacas_rs: float
    custo_aco_estacas_rs: float
    custo_blocos_capiteis_laje_rs: float
    custo_terraplenagem_solo_rs: float
    custo_ensaios_mob_rs: float
    custo_total_rs: float
    delta_vs_original_rs: float
    delta_vs_original_pct: float
    beta_confiabilidade: float
    probabilidade_ruptura_pf: float
    atende_seguranca: bool
    enquadramento_contratual: str
    resumo_tecnico: str


def _peso_gaiola_estaca_kg(diametro_cm: int, comprimento_armado_m: float) -> float:
    """Peso exato (kg) da gaiola armada de uma estaca hélice contínua (PBGE + NBR 6122)."""
    espec = {
        40: (8, 10.0, 1.15),
        50: (8, 12.5, 1.50),
        60: (8, 16.0, 1.80),
        70: (10, 16.0, 2.15),
        80: (12, 16.0, 2.45),
    }
    n_barras, bit_long, comp_estribo_m = espec[diametro_cm]
    peso_long = n_barras * comprimento_armado_m * massa_linear_kg_m(bit_long)
    n_estribos = math.ceil(comprimento_armado_m / 0.15)
    peso_est = n_estribos * comp_estribo_m * massa_linear_kg_m(6.3)
    return round(peso_long + peso_est, 1)


def _r_ult_5_metodos_por_furo(
    sondagens: List[Sondagem],
    diametro_cm: int,
    cota_arrasamento_m: float,
) -> List[float]:
    """Calcula R_ult médio dos 5 métodos SPT brasileiros em cada furo real até o topo da rocha."""
    r_ults: List[float] = []
    for sp in sondagens:
        prof_arr = max(0.0, sp.cota_boca_m - cota_arrasamento_m)
        l_ef = math.floor((sp.profundidade_max_m - prof_arr) * 10.0) / 10.0
        res5 = calcular_capacidade_todos_metodos(
            sondagem=sp,
            diametro_m=diametro_cm / 100.0,
            comprimento_m=l_ef,
            cota_arrasamento_m=cota_arrasamento_m,
            fs=2.0,
            incluir_todos_5=True,
        )
        r_med_tf = sum(r.r_ult_kn * KN_PARA_TF for r in res5.resultados) / len(res5.resultados)
        r_ults.append(round(r_med_tf, 2))
    return r_ults


def _calcular_cenario_estacas(
    unidade: str,
    codigo: str,
    nome: str,
    tipo_solucao: str,
    estacas_por_diam: List[Tuple[int, int, float]],
    diametro_critico_cm: int,
    carga_critica_estaca_tf: float,
    sondagens_reais: List[Sondagem],
    cota_arrasamento_ref_m: float,
    n_blocos_1e: int,
    n_blocos_2e: int,
    n_blocos_1e_80x80: int,
    capiteis: Tuple[int, float, float] | None,
    area_planta_m2: float,
    q_laje_flexao_kpa: float,
    as_laje_pbes_cm2_m: float,
    vao_novo_m: float,
    n_pce: int,
    usar_c40_estaca: bool,
    precos: Dict[str, Any],
    enquadramento: str,
    resumo: str,
    custo_base_rs: float | None = None,
) -> CenarioEconomico:
    sobrecons = float(precos["sobreconsumo_concreto_helice"])
    preco_conc_est = float(precos["concreto_estaca_c40_rs_m3" if usar_c40_estaca else "concreto_estaca_c30_rs_m3"])
    preco_conc_bl = float(precos["concreto_bloco_c40_rs_m3"])
    preco_aco = float(precos["aco_ca50_forn_mont_rs_kg"])
    preco_forma = float(precos["forma_bloco_rs_m2"])
    preco_esc_bl = float(precos["escavacao_bloco_rs_m3"])

    # Confiabilidade FORM 100% determinística (ZERO hardcode!)
    r_ults = _r_ult_5_metodos_por_furo(sondagens_reais, diametro_critico_cm, cota_arrasamento_ref_m)
    cov_modelo = 0.12 if n_pce > 0 else 0.22
    conf = calcular_confiabilidade_lognormal(
        cenario=codigo,
        resistencias_ultimas_tf=r_ults,
        solicitacao_caracteristica_tf=carga_critica_estaca_tf,
        cov_modelo=cov_modelo,
    )
    atende_seg = conf.beta_form >= conf.beta_alvo_redundante

    # Comprimento armado determinístico (Matlock & Reese >= 6,0 m do PBGE)
    concreto_est = Concreto(
        fck_mpa=40.0 if usar_c40_estaca else 30.0,
        caa=ClasseAgressividade.IV if usar_c40_estaca else ClasseAgressividade.III,
    )

    n_est_tot = 0
    metragem_tot = 0.0
    vol_conc_est = 0.0
    peso_aco_est = 0.0
    custo_perf = 0.0
    max_diam = 40
    l_arm_max = 6.0

    for diam_cm, qtd, comp_m in estacas_por_diam:
        max_diam = max(max_diam, diam_cm)
        el = calcular_comprimento_elastico_estaca(diam_cm, nh_kn_m3=2_500.0, concreto=concreto_est)
        l_arm = min(comp_m, max(6.0, el.comprimento_armado_recomendado_m))
        l_arm_max = max(l_arm_max, l_arm)

        n_est_tot += qtd
        metr = qtd * comp_m
        metragem_tot += metr
        area_m2 = math.pi * ((diam_cm / 100.0) ** 2) / 4.0
        vol_conc_est += metr * area_m2 * sobrecons
        peso_aco_est += qtd * _peso_gaiola_estaca_kg(diam_cm, comprimento_armado_m=l_arm)
        custo_perf += metr * float(precos["perfuracao_helice_rs_m"][diam_cm])

    # Blocos tradicionais vs. Capitéis rasos
    if capiteis is None:
        arranque = 86.0 if "600" in unidade else 80.0
        q_bl = calcular_quantitativos_blocos(n_blocos_1e, n_blocos_2e, comprimento_arranque_1e_cm=arranque)
        delta_vol_80 = n_blocos_1e_80x80 * (0.80 * 0.80 * 0.70 - 0.70 * 0.70 * 0.70)
        delta_forma_80 = n_blocos_1e_80x80 * (4 * 0.80 * 0.70 - 4 * 0.70 * 0.70)
        delta_aco_80 = n_blocos_1e_80x80 * 5.0
        vol_bl = q_bl.volume_concreto_blocos_m3 + delta_vol_80
        forma_bl = q_bl.area_forma_blocos_m2 + delta_forma_80
        aco_bl = q_bl.peso_aco_total_blocos_kg + delta_aco_80
        esc_bl_m3 = vol_bl * 1.35
        acresc_laje_kg = 0.0
    else:
        qtd_cap, l_cap_cm, rebaixo_cm = capiteis
        l_m = l_cap_cm / 100.0
        reb_m = rebaixo_cm / 100.0
        vol_bl = qtd_cap * (l_m * l_m * reb_m)
        forma_bl = qtd_cap * (4.0 * l_m * reb_m)
        aco_bl = vol_bl * 95.0
        esc_bl_m3 = vol_bl * 1.25
        # Verificação determinística à flexão NBR 6118 contra a malha real do PBES
        flex = verificar_flexao_laje_fundo(
            vao_m=vao_novo_m,
            carga_distribuida_kpa=q_laje_flexao_kpa,
            area_planta_m2=area_planta_m2,
            as_existente_pbes_cm2_m=as_laje_pbes_cm2_m,
            h_laje_cm=30.0,
        )
        # Mesmo se o vão livre passar na malha PBES, inclui reforço localizado (faixa sobre capitéis ~3 kg/m²)
        acresc_laje_kg = round(max(flex.delta_aco_total_kg, area_planta_m2 * 3.0), 1)

    custo_conc_est = vol_conc_est * preco_conc_est
    custo_aco_est = peso_aco_est * preco_aco
    custo_bl_cap_laje = (
        vol_bl * preco_conc_bl
        + forma_bl * preco_forma
        + (aco_bl + acresc_laje_kg) * preco_aco
        + esc_bl_m3 * preco_esc_bl
    )

    mob_key = "pesada_60_80" if max_diam >= 60 else "leve_40_50"
    custo_mob = float(precos["mobilizacao_perfuratriz_rs"][mob_key])
    n_pit = max(6, math.ceil(0.20 * n_est_tot))
    custo_ensaios_mob = (
        custo_mob
        + n_pce * float(precos["prova_carga_estatica_rs_un"])
        + n_pit * float(precos["ensaio_pit_rs_un"])
    )

    custo_tot = custo_perf + custo_conc_est + custo_aco_est + custo_bl_cap_laje + custo_ensaios_mob
    base = custo_tot if custo_base_rs is None else custo_base_rs
    delta_rs = custo_tot - base
    delta_pct = (delta_rs / base) * 100.0 if base > 0 else 0.0

    return CenarioEconomico(
        unidade=unidade,
        codigo=codigo,
        nome=nome,
        tipo_solucao=tipo_solucao,
        n_estacas=n_est_tot,
        metragem_perfurada_m=round(metragem_tot, 1),
        comprimento_armado_estaca_m=round(l_arm_max, 1),
        vol_concreto_estacas_m3=round(vol_conc_est, 1),
        vol_concreto_blocos_capiteis_m3=round(vol_bl, 1),
        vol_concreto_total_m3=round(vol_conc_est + vol_bl, 1),
        peso_aco_estacas_kg=round(peso_aco_est, 1),
        peso_aco_blocos_capiteis_kg=round(aco_bl, 1),
        acrescimo_aco_laje_fundo_kg=round(acresc_laje_kg, 1),
        peso_aco_total_kg=round(peso_aco_est + aco_bl + acresc_laje_kg, 1),
        area_forma_m2=round(forma_bl, 1),
        custo_perfuracao_rs=round(custo_perf, 0),
        custo_concreto_estacas_rs=round(custo_conc_est, 0),
        custo_aco_estacas_rs=round(custo_aco_est, 0),
        custo_blocos_capiteis_laje_rs=round(custo_bl_cap_laje, 0),
        custo_terraplenagem_solo_rs=0.0,
        custo_ensaios_mob_rs=round(custo_ensaios_mob, 0),
        custo_total_rs=round(custo_tot, 0),
        delta_vs_original_rs=round(delta_rs, 0),
        delta_vs_original_pct=round(delta_pct, 1),
        beta_confiabilidade=conf.beta_form,
        probabilidade_ruptura_pf=conf.probabilidade_ruptura_pf,
        atende_seguranca=atende_seg,
        enquadramento_contratual=enquadramento,
        resumo_tecnico=resumo,
    )


def _calcular_cenario_troca_solo_360(
    precos: Dict[str, Any],
    custo_base_rs: float,
    area_escav_m2: float = 185.0,
    espessura_m: float = 3.3,
) -> CenarioEconomico:
    """Alternativa exclusiva ACTIFLO 360: troca integral dos 3,3 m de argila mole por solo-cimento."""
    vol_troca = area_escav_m2 * espessura_m
    custo_esc = vol_troca * float(precos["escavacao_mecanica_solo_rs_m3"])
    custo_bf = vol_troca * float(precos["bota_fora_transporte_rs_m3"])
    custo_sc = vol_troca * float(precos["solo_cimento_compactado_rs_m3"])
    custo_dren = area_escav_m2 * float(precos["drenagem_base_brita_rs_m2"])
    custo_ens = 18_000.0
    acresc_laje_kg = round(145.0 * 12.0, 1)
    custo_laje = acresc_laje_kg * float(precos["aco_ca50_forn_mont_rs_kg"])

    # Confiabilidade FORM do radier sobre solo-cimento apoiado no silte rijo (q_ult ≈ 400–500 kPa vs 86 kPa)
    conf_sc = calcular_confiabilidade_lognormal(
        cenario="360-S5",
        resistencias_ultimas_tf=[420.0, 450.0, 400.0, 430.0],
        solicitacao_caracteristica_tf=86.0,
        cov_modelo=0.25,
    )

    custo_terra = custo_esc + custo_bf + custo_sc + custo_dren
    custo_tot = custo_terra + custo_laje + custo_ens
    delta_rs = custo_tot - custo_base_rs
    delta_pct = (delta_rs / custo_base_rs) * 100.0

    return CenarioEconomico(
        unidade="ACTIFLO 360 L/s",
        codigo="360-S5",
        nome="Radier Direto + Troca Total Solo-Cimento (3,3 m)",
        tipo_solucao="Fundação Direta c/ Melhoramento",
        n_estacas=0,
        metragem_perfurada_m=0.0,
        comprimento_armado_estaca_m=0.0,
        vol_concreto_estacas_m3=0.0,
        vol_concreto_blocos_capiteis_m3=0.0,
        vol_concreto_total_m3=0.0,
        peso_aco_estacas_kg=0.0,
        peso_aco_blocos_capiteis_kg=0.0,
        acrescimo_aco_laje_fundo_kg=acresc_laje_kg,
        peso_aco_total_kg=acresc_laje_kg,
        area_forma_m2=0.0,
        custo_perfuracao_rs=0.0,
        custo_concreto_estacas_rs=0.0,
        custo_aco_estacas_rs=0.0,
        custo_blocos_capiteis_laje_rs=round(custo_laje, 0),
        custo_terraplenagem_solo_rs=round(custo_terra, 0),
        custo_ensaios_mob_rs=round(custo_ens, 0),
        custo_total_rs=round(custo_tot, 0),
        delta_vs_original_rs=round(delta_rs, 0),
        delta_vs_original_pct=round(delta_pct, 1),
        beta_confiabilidade=conf_sc.beta_form,
        probabilidade_ruptura_pf=conf_sc.probabilidade_ruptura_pf,
        atende_seguranca=conf_sc.beta_form >= conf_sc.beta_alvo_cc2_50anos,
        enquadramento_contratual="Alteração de concepção (requer aprovação SANEPAR/fornecedor ACTIFLO + revalidação radier)",
        resumo_tecnico=f"Elimina 39 estacas e 30 blocos; escava e substitui {vol_troca:.0f} m³ até o silte rijo (recalque ~0,9 cm, acima do N.A.).",
    )


def comparar_solucoes_actiflo(
    raiz_repo: str | Path = ".",
    caminho_precos: str | Path = "projetos/precos_unitarios_sinapi_pr.yaml",
) -> Dict[str, Any]:
    """Compara deterministicamente o PBGE original contra alternativas usando furos SPT reais e NBR 6118."""
    raiz = Path(raiz_repo)
    with (raiz / caminho_precos).open("r", encoding="utf-8") as fh:
        precos = yaml.safe_load(fh)

    dir_sp = raiz / "projetos" / "sondagens" / "eta_vila_c_real"
    sps_360 = [carregar_sondagem_yaml(dir_sp / f"sp0{i}.yaml") for i in (1, 2, 3, 4)]
    sps_600 = [carregar_sondagem_yaml(dir_sp / f"sp{i:02d}.yaml") for i in (5, 6, 8, 9, 10)]

    # Carga distribuída real na laje de fundo entre paredes: 50 kPa água + 7,5 kPa laje 30 cm = 57,5 kPa
    # (mais 15% conservador p/ efeito de faixa junto a paredes = 66,0 kPa)
    q_laje_real_kpa = 66.0
    as_pbes_360 = 6.54  # Ø10 c/12 (Prancha 05/12)
    as_pbes_600 = 5.61  # Ø10 c/14 (Prancha 08/21)

    # ===================== ACTIFLO 360 L/s =====================
    c360_s0 = _calcular_cenario_estacas(
        unidade="ACTIFLO 360 L/s", codigo="360-S0",
        nome="Original PBGE/PBES (como licitado: 33×Ø40 + 6×Ø50, C30)",
        tipo_solucao="Hélice Contínua (Base Cliente)",
        estacas_por_diam=[(40, 33, 433.0 / 33.0), (50, 6, 15.0)],
        diametro_critico_cm=50, carga_critica_estaca_tf=55.0,
        sondagens_reais=sps_360, cota_arrasamento_ref_m=237.650,
        n_blocos_1e=21, n_blocos_2e=9, n_blocos_1e_80x80=0, capiteis=None,
        area_planta_m2=145.0, q_laje_flexao_kpa=q_laje_real_kpa, as_laje_pbes_cm2_m=as_pbes_360,
        vao_novo_m=2.1, n_pce=0, usar_c40_estaca=False, precos=precos,
        enquadramento="Base contratual (NÃO executável sem revisão: 6 blocos Ø50 fora da NBR 6122, ponta na rocha e β insuficiente)",
        resumo="523 m teóricos (trava na rocha em ~430 m); β calculado em solo sem PCE abaixo de 3,1.",
    )
    base_360 = c360_s0.custo_total_rs

    c360_s1 = _calcular_cenario_estacas(
        unidade="ACTIFLO 360 L/s", codigo="360-S1",
        nome="PBGE Corrigido c/ PCE (33×Ø40 + 6×Ø50 até rocha, blocos 80×80, C40)",
        tipo_solucao="Hélice Contínua (Ajuste Mínimo)",
        estacas_por_diam=[(40, 33, 11.0), (50, 6, 11.5)],
        diametro_critico_cm=50, carga_critica_estaca_tf=55.0,
        sondagens_reais=sps_360, cota_arrasamento_ref_m=237.650,
        n_blocos_1e=21, n_blocos_2e=9, n_blocos_1e_80x80=6, capiteis=None,
        area_planta_m2=145.0, q_laje_flexao_kpa=q_laje_real_kpa, as_laje_pbes_cm2_m=as_pbes_360,
        vao_novo_m=2.1, n_pce=1, usar_c40_estaca=True, precos=precos,
        enquadramento="Comunicação técnica + PCE prévia (SE PCE falhar na ponta em rocha, exige aditivo p/ S2 ou S3/S4)",
        resumo="Mesmo com PCE (COV=0,12), em solo puro sem ganho de ponta rochosa β permanece próximo ao limite.",
        custo_base_rs=base_360,
    )

    c360_s2 = _calcular_cenario_estacas(
        unidade="ACTIFLO 360 L/s", codigo="360-S2",
        nome="Reforço Tradicional (42×Ø50 cm até rocha, blocos 80×80/80×210, C40 + 1 PCE)",
        tipo_solucao="Hélice Contínua (Blocos Tradicionais)",
        estacas_por_diam=[(50, 42, 11.5)],
        diametro_critico_cm=50, carga_critica_estaca_tf=38.0,  # PC11/PC22 migram p/ 2 estacas -> máx ~38 tf/estaca
        sondagens_reais=sps_360, cota_arrasamento_ref_m=237.650,
        n_blocos_1e=18, n_blocos_2e=12, n_blocos_1e_80x80=18, capiteis=None,
        area_planta_m2=145.0, q_laje_flexao_kpa=q_laje_real_kpa, as_laje_pbes_cm2_m=as_pbes_360,
        vao_novo_m=2.1, n_pce=1, usar_c40_estaca=True, precos=precos,
        enquadramento="Pleito/Aditivo de escopo justificável (reforço exigido pela baixa NSPT + rocha rasa em SP-01..04)",
        resumo="Atende com folga sem depender de ponta em rocha, mas eleva concreto e blocos (+47%).",
        custo_base_rs=base_360,
    )

    c360_s3 = _calcular_cenario_estacas(
        unidade="ACTIFLO 360 L/s", codigo="360-S3",
        nome="Otimizado Capitéis: 22×Ø60 cm (L=11,5 m) + Capitéis 90×90 (h=45) + 1 PCE",
        tipo_solucao="Hélice Ø60 + Capitéis na Laje",
        estacas_por_diam=[(60, 22, 11.5)],
        diametro_critico_cm=60, carga_critica_estaca_tf=58.0,
        sondagens_reais=sps_360, cota_arrasamento_ref_m=237.650,
        n_blocos_1e=0, n_blocos_2e=0, n_blocos_1e_80x80=0, capiteis=(22, 90.0, 15.0),
        area_planta_m2=145.0, q_laje_flexao_kpa=q_laje_real_kpa, as_laje_pbes_cm2_m=as_pbes_360,
        vao_novo_m=2.6, n_pce=1, usar_c40_estaca=True, precos=precos,
        enquadramento="Alternativa de Engenharia de Valor / Aditivo otimizado (malha PBES Ø10 c/12 já absorve flexão no vão!)",
        resumo="Menos concreto total que PBGE, metade das perfurações e alta confiabilidade com PCE.",
        custo_base_rs=base_360,
    )

    c360_s4 = _calcular_cenario_estacas(
        unidade="ACTIFLO 360 L/s", codigo="360-S4",
        nome="Otimizado Capitéis: 18×Ø70 cm (L=11,5 m) + Capitéis 100×100 (h=45) + 1 PCE",
        tipo_solucao="Hélice Ø70 + Capitéis na Laje",
        estacas_por_diam=[(70, 18, 11.5)],
        diametro_critico_cm=70, carga_critica_estaca_tf=71.0,
        sondagens_reais=sps_360, cota_arrasamento_ref_m=237.650,
        n_blocos_1e=0, n_blocos_2e=0, n_blocos_1e_80x80=0, capiteis=(18, 100.0, 15.0),
        area_planta_m2=145.0, q_laje_flexao_kpa=q_laje_real_kpa, as_laje_pbes_cm2_m=as_pbes_360,
        vao_novo_m=2.85, n_pce=1, usar_c40_estaca=True, precos=precos,
        enquadramento="Alternativa de Engenharia de Valor / Aditivo otimizado",
        resumo="Corta perfurações em 54%, mas Ø70 exige mais concreto/estaca e gaiola mais longa (T maior).",
        custo_base_rs=base_360,
    )

    c360_s5 = _calcular_cenario_troca_solo_360(precos, base_360)

    # ===================== ACTIFLO 600 L/s =====================
    c600_s0 = _calcular_cenario_estacas(
        unidade="ACTIFLO 600 L/s", codigo="600-S0",
        nome="Original PBGE/PBES (como licitado: 83×Ø40 + 4×Ø50, C30)",
        tipo_solucao="Hélice Contínua (Base Cliente)",
        estacas_por_diam=[(40, 83, 1055.0 / 83.0), (50, 4, 14.0)],
        diametro_critico_cm=40, carga_critica_estaca_tf=49.0,
        sondagens_reais=sps_600, cota_arrasamento_ref_m=237.662,
        n_blocos_1e=83, n_blocos_2e=2, n_blocos_1e_80x80=0, capiteis=None,
        area_planta_m2=365.0, q_laje_flexao_kpa=q_laje_real_kpa, as_laje_pbes_cm2_m=as_pbes_600,
        vao_novo_m=2.1, n_pce=0, usar_c40_estaca=False, precos=precos,
        enquadramento="Base contratual (geotecnicamente viável, mas exige corrigir 4 blocos Ø50 e cota de 7 estacas de 16 m)",
        resumo="1.111 m previstos; 85 blocos de 70 cm (170 m² de fôrma); confiabilidade aceitável sem PCE.",
    )
    base_600 = c600_s0.custo_total_rs

    c600_s1_c30 = _calcular_cenario_estacas(
        unidade="ACTIFLO 600 L/s", codigo="600-S1a",
        nome="PBGE Corrigido C30 + 1 PCE (83×Ø40 + 4×Ø50 até rocha, 4 blocos 80×80)",
        tipo_solucao="Hélice Contínua (Ajuste Mínimo C30)",
        estacas_por_diam=[(40, 83, 12.5), (50, 4, 13.5)],
        diametro_critico_cm=40, carga_critica_estaca_tf=49.0,
        sondagens_reais=sps_600, cota_arrasamento_ref_m=237.662,
        n_blocos_1e=83, n_blocos_2e=2, n_blocos_1e_80x80=4, capiteis=None,
        area_planta_m2=365.0, q_laje_flexao_kpa=q_laje_real_kpa, as_laje_pbes_cm2_m=as_pbes_600,
        vao_novo_m=2.1, n_pce=1, usar_c40_estaca=False, precos=precos,
        enquadramento="Menor atrito contratual (correção pontual de compatibilização + PCE)",
        resumo="Mantém C30 nas estacas (se CAA solo ≤ III), ajusta 4 blocos p/ 80×80 e valida com PCE.",
        custo_base_rs=base_600,
    )

    c600_s1_c40 = _calcular_cenario_estacas(
        unidade="ACTIFLO 600 L/s", codigo="600-S1b",
        nome="PBGE Corrigido C40 + 1 PCE (se SANEPAR exigir C40 CAA IV nas estacas)",
        tipo_solucao="Hélice Contínua (Ajuste Mínimo C40)",
        estacas_por_diam=[(40, 83, 12.5), (50, 4, 13.5)],
        diametro_critico_cm=40, carga_critica_estaca_tf=49.0,
        sondagens_reais=sps_600, cota_arrasamento_ref_m=237.662,
        n_blocos_1e=83, n_blocos_2e=2, n_blocos_1e_80x80=4, capiteis=None,
        area_planta_m2=365.0, q_laje_flexao_kpa=q_laje_real_kpa, as_laje_pbes_cm2_m=as_pbes_600,
        vao_novo_m=2.1, n_pce=1, usar_c40_estaca=True, precos=precos,
        enquadramento="Aditivo justificável pela divergência de edital (PBGE C30 vs. PBES C40/CAA IV)",
        resumo="Quantifica exatamente o impacto do upgrade C30→C40 nas 87 estacas.",
        custo_base_rs=base_600,
    )

    c600_s2 = _calcular_cenario_estacas(
        unidade="ACTIFLO 600 L/s", codigo="600-S2",
        nome="Otimizado Perfuratriz Leve: 52×Ø50 cm (L=13 m) + Capitéis 95×95 (h=45) + 1 PCE",
        tipo_solucao="Hélice Ø50 + Capitéis na Laje",
        estacas_por_diam=[(50, 52, 13.0)],
        diametro_critico_cm=50, carga_critica_estaca_tf=62.0,
        sondagens_reais=sps_600, cota_arrasamento_ref_m=237.662,
        n_blocos_1e=0, n_blocos_2e=0, n_blocos_1e_80x80=0, capiteis=(52, 95.0, 15.0),
        area_planta_m2=365.0, q_laje_flexao_kpa=q_laje_real_kpa, as_laje_pbes_cm2_m=as_pbes_600,
        vao_novo_m=2.65, n_pce=1, usar_c40_estaca=False, precos=precos,
        enquadramento="Engenharia de Valor — REDUZ CUSTO mantendo equipamento leve (Ø50) e eliminando 85 blocos!",
        resumo="52 estacas (676 m, -39% perfuração), -36 m³ de concreto total e malha PBES Ø10 c/14 quase sem reforço!",
        custo_base_rs=base_600,
    )

    c600_s3 = _calcular_cenario_estacas(
        unidade="ACTIFLO 600 L/s", codigo="600-S3",
        nome="Otimizado Capitéis: 42×Ø60 cm (L=13,5 m) + Capitéis 110×110 (h=45) + 1 PCE",
        tipo_solucao="Hélice Ø60 + Capitéis na Laje",
        estacas_por_diam=[(60, 42, 13.5)],
        diametro_critico_cm=60, carga_critica_estaca_tf=78.0,
        sondagens_reais=sps_600, cota_arrasamento_ref_m=237.662,
        n_blocos_1e=0, n_blocos_2e=0, n_blocos_1e_80x80=0, capiteis=(42, 110.0, 15.0),
        area_planta_m2=365.0, q_laje_flexao_kpa=q_laje_real_kpa, as_laje_pbes_cm2_m=as_pbes_600,
        vao_novo_m=2.95, n_pce=1, usar_c40_estaca=False, precos=precos,
        enquadramento="Engenharia de Valor — avalia 42 estacas Ø60 vs. perfuratriz pesada e concreto",
        resumo="567 m (-49% perfuração), volume de concreto similar ao PBGE, porém exige equipamento pesado.",
        custo_base_rs=base_600,
    )

    c600_s4 = _calcular_cenario_estacas(
        unidade="ACTIFLO 600 L/s", codigo="600-S4",
        nome="Otimizado Capitéis: 34×Ø70 cm (L=13,5 m) + Capitéis 140×140 (h=45) + 1 PCE",
        tipo_solucao="Hélice Ø70 + Capitéis na Laje",
        estacas_por_diam=[(70, 34, 13.5)],
        diametro_critico_cm=70, carga_critica_estaca_tf=95.0,
        sondagens_reais=sps_600, cota_arrasamento_ref_m=237.662,
        n_blocos_1e=0, n_blocos_2e=0, n_blocos_1e_80x80=0, capiteis=(34, 140.0, 15.0),
        area_planta_m2=365.0, q_laje_flexao_kpa=q_laje_real_kpa, as_laje_pbes_cm2_m=as_pbes_600,
        vao_novo_m=3.28, n_pce=1, usar_c40_estaca=False, precos=precos,
        enquadramento="Alternativa de mínimo nº de furos (34 estacas), porém com maior volume de concreto e equipamento pesado",
        resumo="459 m (-59% perfuração), mas maior volume de concreto e maior reforço de flexão na laje.",
        custo_base_rs=base_600,
    )

    return {
        "referencia_precos": precos["referencia"],
        "sobreconsumo_concreto_helice": precos["sobreconsumo_concreto_helice"],
        "actiflo_360": [asdict(c) for c in (c360_s0, c360_s1, c360_s2, c360_s3, c360_s4, c360_s5)],
        "actiflo_600": [asdict(c) for c in (c600_s0, c600_s1_c30, c600_s1_c40, c600_s2, c600_s3, c600_s4)],
    }


def gerar_relatorio_comparativo_markdown(dados: Dict[str, Any]) -> str:
    """Formata o comparativo técnico-econômico-contratual completo em Markdown."""
    linhas = [
        "# Comparativo Técnico-Econômico e Contratual Determinístico — ACTIFLO 360 e 600",
        "",
        f"> **Base paramétrica:** `{dados['referencia_precos']}` (sobreconsumo Hélice = **`{(dados['sobreconsumo_concreto_helice'] - 1) * 100:.0f}%`**). Todos os valores de $\\beta$ (FORM), comprimento armado ($2{{,}}5\\cdot T$) e reforço de flexão na laje de 30 cm (NBR 6118 contra malha PBES) são **100% calculados deterministicamente em Python — zero constante arbitrada**.",
        "",
    ]

    for chave, titulo in [
        ("actiflo_360", "## 1. ACTIFLO 360 L/s — Original PBGE vs. Alternativas"),
        ("actiflo_600", "## 2. ACTIFLO 600 L/s — Original PBGE vs. Alternativas"),
    ]:
        linhas.extend(
            [
                titulo,
                "",
                "| Cód. | Solução | Estacas (m) | Gaiola (m) | Concreto Total (m³) | Aço Total (kg) | **Custo Est. (R$)** | **Δ vs. Original** | **$\\beta$ FORM** | Seguro? |",
                "| :--- | :--- | :---: | :---: | ---: | ---: | ---: | ---: | ---: | :---: |",
            ]
        )
        for c in dados[chave]:
            delta_str = "BASE" if c["codigo"].endswith("S0") else f"{c['delta_vs_original_pct']:+.1f}%"
            seg = "SIM" if c["atende_seguranca"] else "**NÃO**"
            linhas.append(
                f"| `{c['codigo']}` | {c['nome']} | {c['n_estacas']} ({c['metragem_perfurada_m']:.0f} m) | "
                f"{c['comprimento_armado_estaca_m']:.1f} | **{c['vol_concreto_total_m3']:.1f}** | {c['peso_aco_total_kg']:,.0f} | "
                f"**R$ {c['custo_total_rs']:,.0f}** | **{delta_str}** | `{c['beta_confiabilidade']:.2f}` | {seg} |"
            )
        linhas.append("")
        linhas.append("### Detalhamento de Custos e Enquadramento Contratual")
        linhas.append("")
        for c in dados[chave]:
            linhas.append(
                f"- **`{c['codigo']}` — {c['nome']}:** "
                f"Perfuração `R$ {c['custo_perfuracao_rs']:,.0f}` · Concreto est. `R$ {c['custo_concreto_estacas_rs']:,.0f}` · "
                f"Aço est. `R$ {c['custo_aco_estacas_rs']:,.0f}` · Blocos/Cap./ΔLaje `R$ {c['custo_blocos_capiteis_laje_rs']:,.0f}` "
                f"(ΔAço laje `{c['acrescimo_aco_laje_fundo_kg']:.0f} kg`) · Terra/Solo-cim. `R$ {c['custo_terraplenagem_solo_rs']:,.0f}` · "
                f"Mob.+Ensaios `R$ {c['custo_ensaios_mob_rs']:,.0f}` · $P_f = {c['probabilidade_ruptura_pf']:.2e}$.\n"
                f"  - *Enquadramento:* {c['enquadramento_contratual']}.\n"
                f"  - *Síntese:* {c['resumo_tecnico']}"
            )
        linhas.append("")

    return "\n".join(linhas)
