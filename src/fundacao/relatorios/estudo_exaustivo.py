"""Orquestrador 100% determinístico em Python para estudo exaustivo de fundações (ACTIFLO 360 e 600)."""

from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

from fundacao.estrutural.puncao_capitel import dimensionar_capitel_minimo, verificar_puncao_laje_com_capitel
from fundacao.geotecnia.capacidade import calcular_capacidade_todos_metodos
from fundacao.geotecnia.fundacao_direta import (
    calcular_capacidade_vesic,
    carregar_ensaios_yaml,
    estudo_troca_solo,
)
from fundacao.geotecnia.grupo_radier_estaqueado import (
    calcular_grupo_estacas,
    calcular_radier_estaqueado_pdr,
)
from fundacao.geotecnia.sondagem import Sondagem, carregar_sondagem_yaml
from fundacao.geotecnia.vibracao_cravacao import avaliar_vibracao_cravacao
from fundacao.normas.nbr6118 import ClasseAgressividade, Concreto, KN_PARA_TF
from fundacao.verificacoes.auditoria import carregar_projeto
from fundacao.verificacoes.cargas_tanque import calcular_cargas_tanque
from fundacao.verificacoes.confiabilidade import calcular_confiabilidade_lognormal


def _comprimento_efetivo_ate_rocha(sondagem: Sondagem, cota_arrasamento_m: float) -> float:
    prof_arr = max(0.0, sondagem.cota_boca_m - cota_arrasamento_m)
    return math.floor((sondagem.profundidade_max_m - prof_arr) * 10.0) / 10.0


def executar_estudo_exaustivo(
    raiz_repo: str | Path = ".",
    out_md: str | Path = "saidas/estudo_exaustivo_actiflo_360_600.md",
    out_json: str | Path = "saidas/estudo_exaustivo_resultados.json",
) -> Dict[str, Any]:
    """Executa toda a bateria determinística de engenharia (5 métodos SPT, confiabilidade FORM,
    vibração de cravação, estacas de grande diâmetro + capitéis na laje, radier estaqueado PDR e
    fundação direta) e salva o memorial Markdown + JSON estruturado.
    """
    raiz = Path(raiz_repo)
    dir_sp = raiz / "projetos" / "sondagens" / "eta_vila_c_real"

    sps_360 = [carregar_sondagem_yaml(dir_sp / f"sp0{i}.yaml") for i in (1, 2, 3, 4)]
    sps_600 = [carregar_sondagem_yaml(dir_sp / f"sp{i:02d}.yaml") for i in (5, 6, 8, 9, 10)]
    ensaios = carregar_ensaios_yaml(dir_sp / "ensaios_laboratorio.yaml")

    cfg_360, pts_360 = carregar_projeto(raiz / "projetos" / "actiflo_360")
    cfg_600, pts_600 = carregar_projeto(raiz / "projetos" / "actiflo_600")
    concreto_c40 = Concreto(fck_mpa=40.0, caa=ClasseAgressividade.IV)

    # 1. Verificação pelos 5 métodos SPT para diâmetros 40, 50, 60, 70 e 80 cm até o topo rochoso
    diametros_cm = [40, 50, 60, 70, 80]
    matriz_5_metodos: Dict[str, List[Dict[str, Any]]] = {"actiflo_360": [], "actiflo_600": []}

    for chave, sps, cota_arr in [
        ("actiflo_360", sps_360, 237.650),
        ("actiflo_600", sps_600, 237.662),
    ]:
        for d_cm in diametros_cm:
            por_furo = []
            for sp in sps:
                l_ef = _comprimento_efetivo_ate_rocha(sp, cota_arr)
                res5 = calcular_capacidade_todos_metodos(
                    sondagem=sp,
                    diametro_m=d_cm / 100.0,
                    comprimento_m=l_ef,
                    cota_arrasamento_m=cota_arr,
                    fs=2.0,
                    incluir_todos_5=True,
                )
                r_dict = {r.metodo: r.p_adm_tf for r in res5.resultados}
                r_ult_med_tf = sum(r.r_ult_kn * KN_PARA_TF for r in res5.resultados) / len(res5.resultados)
                por_furo.append(
                    {
                        "furo": sp.codigo,
                        "cota_rocha_m": sp.cota_rocha_m,
                        "l_ef_m": l_ef,
                        "metodos_tf": r_dict,
                        "p_adm_min_tf": res5.p_adm_min_tf,
                        "p_adm_media_tf": res5.p_adm_media_tf,
                        "r_ult_media_tf": round(r_ult_med_tf, 1),
                    }
                )
            p_adm_geral_med = sum(x["p_adm_media_tf"] for x in por_furo) / len(por_furo)
            p_adm_pior_furo = min(x["p_adm_media_tf"] for x in por_furo)
            matriz_5_metodos[chave].append(
                {
                    "diametro_cm": d_cm,
                    "p_adm_media_furos_tf": round(p_adm_geral_med, 1),
                    "p_adm_pior_furo_tf": round(p_adm_pior_furo, 1),
                    "furos": por_furo,
                }
            )

    # 2. Análise de Confiabilidade Geotécnica (FORM Lognormal — ISO 2394 / Eurocode 7)
    def _r_ults(chave: str, d_cm: int) -> List[float]:
        for item in matriz_5_metodos[chave]:
            if item["diametro_cm"] == d_cm:
                return [f["r_ult_media_tf"] for f in item["furos"]]
        return []

    confiabilidades = [
        # PBGE atual — 360 L/s (críticos em solo sem comprovar ponta em rocha)
        calcular_confiabilidade_lognormal("360 PBGE atual — Ø40 em PC15/PC24 (42 tf), sem PCE", _r_ults("actiflo_360", 40), 42.0, cov_modelo=0.22),
        calcular_confiabilidade_lognormal("360 PBGE atual — Ø50 em PC11 (55 tf), sem PCE", _r_ults("actiflo_360", 50), 55.0, cov_modelo=0.22),
        calcular_confiabilidade_lognormal("360 Alternativa — Ø70 p/ 55 tf, sem PCE", _r_ults("actiflo_360", 70), 55.0, cov_modelo=0.22),
        calcular_confiabilidade_lognormal("360 Alternativa — Ø70 p/ 55 tf, COM PCE (COV=0,12)", _r_ults("actiflo_360", 70), 55.0, cov_modelo=0.12),
        calcular_confiabilidade_lognormal("360 Alternativa — Ø80 p/ 60 tf, COM PCE (COV=0,12)", _r_ults("actiflo_360", 80), 60.0, cov_modelo=0.12),
        # PBGE atual — 600 L/s
        calcular_confiabilidade_lognormal("600 PBGE atual — Ø40 em P4/PC5 (49 tf), sem PCE", _r_ults("actiflo_600", 40), 49.0, cov_modelo=0.22),
        calcular_confiabilidade_lognormal("600 PBGE atual — Ø50 em PC59 (61 tf), sem PCE", _r_ults("actiflo_600", 50), 61.0, cov_modelo=0.22),
        calcular_confiabilidade_lognormal("600 PBGE atual — Ø50 em PC59 (61 tf), COM PCE (COV=0,12)", _r_ults("actiflo_600", 50), 61.0, cov_modelo=0.12),
        calcular_confiabilidade_lognormal("600 Alternativa — Ø70 p/ 85 tf, COM PCE (COV=0,12)", _r_ults("actiflo_600", 70), 85.0, cov_modelo=0.12),
    ]

    # 3. Avaliação de Vibração na Cravação de Estacas (Wiss / Woods & Jedele / DIN 4150-3 / NBR 9653)
    vibracoes = [
        avaliar_vibracao_cravacao("Filtro Velho (Mód. 1) — ao sul do ACTIFLO 360", distancia_m=4.0, energia_martelo_kj=45.0, classe_solo="classe_II_argila_silte"),
        avaliar_vibracao_cravacao("Floculador Existente — a leste do ACTIFLO 360", distancia_m=6.0, energia_martelo_kj=45.0, classe_solo="classe_II_argila_silte"),
        avaliar_vibracao_cravacao("EE Lodo Existente — a oeste do ACTIFLO 360", distancia_m=12.0, energia_martelo_kj=45.0, classe_solo="classe_II_argila_silte"),
        avaliar_vibracao_cravacao("Tanque de Lodo / Filtros Adjacentes — colados ao ACTIFLO 600", distancia_m=3.5, energia_martelo_kj=45.0, classe_solo="classe_II_argila_silte"),
        avaliar_vibracao_cravacao("Filtro Velho (nega em basalto — transmissão Classe IV)", distancia_m=4.0, energia_martelo_kj=45.0, classe_solo="classe_IV_rocha"),
    ]

    # 4. Solução de Estacas de Grande Diâmetro (Ø60/Ø70/Ø80 cm) + Capitéis na Laje de Fundo (30 cm)
    capiteis_cenarios = []
    for desc, d_cm, carga_est_tf, n_est_est in [
        ("ACTIFLO 360 — 22 estacas Ø60 cm (~58 tf/est)", 60.0, 65.0, 22),
        ("ACTIFLO 360 — 18 estacas Ø70 cm (~71 tf/est)", 70.0, 75.0, 18),
        ("ACTIFLO 360 — 15 estacas Ø80 cm (~85 tf/est)", 80.0, 90.0, 15),
        ("ACTIFLO 600 — 42 estacas Ø60 cm (~72 tf/est)", 60.0, 80.0, 42),
        ("ACTIFLO 600 — 34 estacas Ø70 cm (~89 tf/est)", 70.0, 95.0, 34),
        ("ACTIFLO 600 — 28 estacas Ø80 cm (~108 tf/est)", 80.0, 115.0, 28),
    ]:
        sem_cap = verificar_puncao_laje_com_capitel(
            nk_tf=carga_est_tf, diametro_estaca_cm=d_cm, h_laje_cm=30.0, concreto=concreto_c40
        )
        cap_opt = dimensionar_capitel_minimo(
            nk_tf=carga_est_tf, diametro_estaca_cm=d_cm, h_laje_cm=30.0, concreto=concreto_c40
        )
        capiteis_cenarios.append(
            {
                "cenario": desc,
                "n_estacas_est": n_est_est,
                "diametro_cm": d_cm,
                "carga_projeto_capitel_tf": carga_est_tf,
                "sem_capitel_passa_sem_armadura": sem_cap.dispensa_armadura_puncao,
                "sem_capitel_tau_c1_mpa": sem_cap.tau_sd_c_linha_mpa,
                "sem_capitel_tau_rd1_mpa": sem_cap.tau_rd1_laje_mpa,
                "capitel_min_l_cm": cap_opt.l_capitel_cm,
                "capitel_min_h_total_cm": cap_opt.h_capitel_total_cm,
                "capitel_rebaixo_cm": cap_opt.h_capitel_total_cm - 30.0,
                "capitel_tau_c1_mpa": cap_opt.tau_sd_c_linha_mpa,
                "capitel_tau_c2_laje_mpa": cap_opt.tau_sd_c_duas_linhas_mpa,
                "dispensa_armadura_puncao": cap_opt.dispensa_armadura_puncao,
            }
        )

    # 5. Radier Estaqueado (PDR — Poulos, Davis & Randolph) e Recalque de Grupo
    pdr_cenarios = [
        ("ACTIFLO 360 — PBGE atual (39 est Ø40, L=11,5m)", calcular_radier_estaqueado_pdr(8.4, 20.4, 1270.0, 39, 0.40, 11.5, es_solo_superficial_kpa=4500.0, es_solo_profundo_kpa=28000.0)),
        ("ACTIFLO 360 — Otimizado Capitéis (18 est Ø70, L=11,5m)", calcular_radier_estaqueado_pdr(8.4, 20.4, 1270.0, 18, 0.70, 11.5, es_solo_superficial_kpa=4500.0, es_solo_profundo_kpa=28000.0)),
        ("ACTIFLO 360 — Otimizado Capitéis (15 est Ø80, L=11,5m)", calcular_radier_estaqueado_pdr(8.4, 20.4, 1270.0, 15, 0.80, 11.5, es_solo_superficial_kpa=4500.0, es_solo_profundo_kpa=28000.0)),
        ("ACTIFLO 600 — PBGE atual (87 est Ø40, L=13,5m)", calcular_radier_estaqueado_pdr(16.9, 23.7, 3023.0, 87, 0.40, 13.5, es_solo_superficial_kpa=4000.0, es_solo_profundo_kpa=45000.0)),
        ("ACTIFLO 600 — Otimizado Capitéis (42 est Ø60, L=13,5m)", calcular_radier_estaqueado_pdr(16.9, 23.7, 3023.0, 42, 0.60, 13.5, es_solo_superficial_kpa=4000.0, es_solo_profundo_kpa=45000.0)),
        ("ACTIFLO 600 — Otimizado Capitéis (34 est Ø70, L=13,5m)", calcular_radier_estaqueado_pdr(16.9, 23.7, 3023.0, 34, 0.70, 13.5, es_solo_superficial_kpa=4000.0, es_solo_profundo_kpa=45000.0)),
        ("ACTIFLO 600 — Otimizado Capitéis (28 est Ø80, L=13,5m)", calcular_radier_estaqueado_pdr(16.9, 23.7, 3023.0, 28, 0.80, 13.5, es_solo_superficial_kpa=4000.0, es_solo_profundo_kpa=45000.0)),
    ]

    grupo_360 = calcular_grupo_estacas(4, 10, 0.40, 11.5, 2.0, 1270.0, es_solo_ponta_kpa=28_000.0, espessura_solo_abaixo_2_3_l_m=3.8)
    grupo_600 = calcular_grupo_estacas(8, 11, 0.40, 13.5, 2.1, 3023.0, es_solo_ponta_kpa=45_000.0, espessura_solo_abaixo_2_3_l_m=4.5)

    # 6. Balanço de cargas dos tanques e Fundação Direta (AI-02)
    tanque_360 = calcular_cargas_tanque("ACTIFLO 360", 202.2, 13.26, 112.0, 4.85, 145.0, sum(p.nk_tf for p in pts_360))
    tanque_600 = calcular_cargas_tanque("ACTIFLO 600", 478.1, 42.75, 295.0, 4.85, 365.0, sum(p.nk_tf for p in pts_600))
    ai02 = ensaios["AI-02"]
    vesic_360 = calcular_capacidade_vesic(ai02, 8.4, 20.4, 1.5, 3.0)
    vesic_600 = calcular_capacidade_vesic(ai02, 16.9, 23.7, 1.5, 3.0)
    troca_360 = estudo_troca_solo(ai02, tanque_360.tensao_media_pbes_kpa, 8.4, 20.4, 1.5, 4.8, [0.0, 1.5, 2.5, 3.3])
    troca_600 = estudo_troca_solo(ai02, tanque_600.tensao_media_pbes_kpa, 16.9, 23.7, 1.5, 7.8, [0.0, 1.5, 2.5, 3.3])

    resultados = {
        "matriz_5_metodos_spt": matriz_5_metodos,
        "confiabilidade_form": [asdict(c) for c in confiabilidades],
        "vibracao_cravacao": [asdict(v) for v in vibracoes],
        "capiteis_puncao_nbr6118": capiteis_cenarios,
        "radier_estaqueado_pdr": [{"cenario": n, **asdict(r)} for n, r in pdr_cenarios],
        "grupos_estacas": {"actiflo_360": asdict(grupo_360), "actiflo_600": asdict(grupo_600)},
        "tanques": {"actiflo_360": asdict(tanque_360), "actiflo_600": asdict(tanque_600)},
        "fundacao_direta_ai02": {
            "vesic_360": asdict(vesic_360),
            "vesic_600": asdict(vesic_600),
            "troca_360": [asdict(t) for t in troca_360],
            "troca_600": [asdict(t) for t in troca_600],
        },
    }

    # Salvar JSON estruturado
    p_json = raiz / out_json
    p_json.parent.mkdir(parents=True, exist_ok=True)
    p_json.write_text(json.dumps(resultados, indent=2, ensure_ascii=False), encoding="utf-8")

    # Gerar Memorial Markdown 100% reproduzível a partir dos números calculados em Python
    md = _formatar_markdown_exaustivo(resultados)
    p_md = raiz / out_md
    p_md.parent.mkdir(parents=True, exist_ok=True)
    p_md.write_text(md, encoding="utf-8")
    return resultados


def _formatar_markdown_exaustivo(r: Dict[str, Any]) -> str:
    linhas: List[str] = [
        "# Estudo Exaustivo e Reproduzível de Fundações — ACTIFLO 360 L/s e 600 L/s",
        "",
        "> **Gerado 100% deterministicamente por `src/fundacao/relatorios/estudo_exaustivo.py`** a partir dos 9 furos SPT reais (`SP-01`..`SP-10`), ensaios de laboratório (`AI-01`..`AI-06`) e pranchas PBES/PBGE da ETA Vila C (SANEPAR — Foz do Iguaçu/PR).",
        "",
        "## 1. Verificação Multi-Método (5 Métodos Brasileiros — Velloso & Lopes) por Diâmetro",
        "",
        "Métodos avaliados até o topo da rocha impenetrável (`FS = 2,0`): **Aoki-Velloso (1975/97)**, **Décourt-Quaresma (1978/96)**, **Antunes-Cabral (1996)**, **Teixeira (1996)** e **Alonso (1996)**.",
        "",
    ]

    for chave, titulo in [
        ("actiflo_360", "### 1.1 ACTIFLO 360 L/s (`SP-01` a `SP-04`, arrasamento `237,65 m`, rocha `225,1–227,6 m`)"),
        ("actiflo_600", "### 1.2 ACTIFLO 600 L/s (`SP-05` a `SP-10`, arrasamento `237,66 m`, rocha `223,1–224,3 m`)"),
    ]:
        linhas.extend(
            [
                titulo,
                "",
                "| Diâmetro | $P_{\\text{adm}}$ Média 5 Métodos (tf) | Pior Furo (tf) | Aoki | Décourt | Antunes | Teixeira | Alonso |",
                "| :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for item in r["matriz_5_metodos_spt"][chave]:
            furos = item["furos"]
            def _med(m_sub: str) -> float:
                vals = [v for f in furos for k, v in f["metodos_tf"].items() if m_sub in k]
                return sum(vals) / len(vals)
            linhas.append(
                f"| **Ø {item['diametro_cm']} cm** | **{item['p_adm_media_furos_tf']:.1f}** | {item['p_adm_pior_furo_tf']:.1f} | "
                f"{_med('Aoki'):.1f} | {_med('Décourt'):.1f} | {_med('Antunes'):.1f} | {_med('Teixeira'):.1f} | {_med('Alonso'):.1f} |"
            )
        linhas.append("")

    # 2. Confiabilidade
    linhas.extend(
        [
            "## 2. Análise de Confiabilidade Geotécnica (FORM Lognormal — ISO 2394 / JRC Eurocode 7)",
            "",
            "Alvos da literatura (`Reliability Targets for Geotechnical Structures`): $\\beta_T \\ge 3{,}1$ (sistema redundante, $P_f \\le 10^{-3}$) e $\\beta_T \\ge 3{,}8$ (CC2 / 50 anos, $P_f \\le 7{,}2\\times 10^{-5}$).",
            "",
            "| Cenário | $R_{\\text{ult}}$ médio (tf) | $S$ médio (tf) | $FS_{\\text{méd}}$ | $COV_R$ | **$\\beta$ (FORM)** | **$P_f$** | Diagnóstico |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |",
        ]
    )
    for c in r["confiabilidade_form"]:
        linhas.append(
            f"| {c['cenario']} | {c['r_ult_medio_tf']:.1f} | {c['s_medio_tf']:.1f} | {c['fs_medio']:.2f} | "
            f"{c['cov_resistencia_total']:.2f} | **{c['beta_form']:.2f}** | `{c['probabilidade_ruptura_pf']:.2e}` | {c['status_confiabilidade']} |"
        )
    linhas.append("")

    # 3. Vibração de cravação
    linhas.extend(
        [
            "## 3. Avaliação Quantitativa de Vibração em Estacas Cravadas (Wiss / Woods-Jedele / DIN 4150-3 / NBR 9653)",
            "",
            "| Estrutura Existente Vizinha | Distância (m) | Martelo (kJ) | **PPV est. (mm/s)** | Dist. Segura DIN (`5 mm/s`) | Dist. Segura NBR (`15 mm/s`) | Risco |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | :--- |",
        ]
    )
    for v in r["vibracao_cravacao"]:
        linhas.append(
            f"| {v['estrutura_vizinha']} | {v['distancia_m']:.1f} | {v['energia_martelo_kj']:.0f} | "
            f"**{v['ppv_estimado_mm_s']:.1f}** | {v['distancia_segura_din_5mms_m']:.1f} m | {v['distancia_segura_nbr_15mms_m']:.1f} m | {v['risco_fissuracao']} |"
        )
    linhas.append("")

    # 4. Estacas de Grande Diâmetro + Capitéis
    linhas.extend(
        [
            "## 4. Alternativa: Estacas de Maior Diâmetro (`Ø60–80 cm`) + Capitéis na Laje de Fundo (`h = 30 cm`, NBR 6118:2023)",
            "",
            "| Cenário | Carga Projeto Capitel (tf) | Sem Capitel (`τ_sd / τ_Rd1` MPa) | **Capitel Mínimo (`L × L`, `h_total`)** | Rebaixo abaixo laje | `τ_sd (C'')` na laje 30 cm | Dispensa armadura punção? |",
            "| :--- | ---: | :---: | :---: | ---: | ---: | :---: |",
        ]
    )
    for cap in r["capiteis_puncao_nbr6118"]:
        linhas.append(
            f"| {cap['cenario']} | {cap['carga_projeto_capitel_tf']:.0f} | "
            f"`{cap['sem_capitel_tau_c1_mpa']:.2f} / {cap['sem_capitel_tau_rd1_mpa']:.2f}` ({'OK' if cap['sem_capitel_passa_sem_armadura'] else 'PUNÇÃO'}) | "
            f"**`{cap['capitel_min_l_cm']:.0f}×{cap['capitel_min_l_cm']:.0f} cm`, `h = {cap['capitel_min_h_total_cm']:.0f} cm`** | "
            f"`+{cap['capitel_rebaixo_cm']:.0f} cm` | `{cap['capitel_tau_c2_laje_mpa']:.2f} MPa` | **{'SIM' if cap['dispensa_armadura_puncao'] else 'NÃO'}** |"
        )
    linhas.append("")

    # 5. Radier Estaqueado (PDR)
    linhas.extend(
        [
            "## 5. Interação Solo–Laje–Estaca: Radier Estaqueado (Método PDR — Poulos, Davis & Randolph)",
            "",
            "| Cenário | Estacas / Ø | Carga Radier (%) | Carga Estacas (%) | Média/Estaca (tf) | Recalque Radier Isolado (mm) | **Recalque PDR (mm)** | Redução | ELS ≤ 25 mm |",
            "| :--- | :---: | ---: | ---: | ---: | ---: | ---: | ---: | :---: |",
        ]
    )
    for p in r["radier_estaqueado_pdr"]:
        linhas.append(
            f"| {p['cenario']} | {p['n_estacas']}× Ø{p['diametro_cm']:.0f} | {p['parcela_carga_radier_pct']:.1f}% | "
            f"{p['parcela_carga_estacas_pct']:.1f}% | {p['carga_media_por_estaca_tf']:.1f} | "
            f"{p['recalque_radier_isolado_mm']:.1f} | **{p['recalque_radier_estaqueado_mm']:.1f}** | "
            f"{p['reducao_recalque_pct']:.1f}% | **{'SIM' if p['atende_recalque_els'] else 'NÃO'}** |"
        )
    linhas.append("")

    # 6. Recalque de grupo
    g360, g600 = r["grupos_estacas"]["actiflo_360"], r["grupos_estacas"]["actiflo_600"]
    linhas.extend(
        [
            "## 6. Eficiência e Recalque de Grupo (Converse-Labarre & Sapata Equivalente a 2L/3)",
            "",
            f"- **ACTIFLO 360 (grupo PBGE ~4×10 Ø40):** $\\eta_{{CL}} = {g360['eficiencia_converse_labarre']:.3f}$, recalque elástico fuste `{g360['recalque_elastico_fuste_mm']:.1f} mm` + solo abaixo de $2L/3$ `{g360['recalque_solo_abaixo_2_3_l_mm']:.1f} mm` = **`{g360['recalque_total_grupo_mm']:.1f} mm`**.",
            f"- **ACTIFLO 600 (grupo PBGE ~8×11 Ø40):** $\\eta_{{CL}} = {g600['eficiencia_converse_labarre']:.3f}$, recalque elástico fuste `{g600['recalque_elastico_fuste_mm']:.1f} mm` + solo abaixo de $2L/3$ `{g600['recalque_solo_abaixo_2_3_l_mm']:.1f} mm` = **`{g600['recalque_total_grupo_mm']:.1f} mm`**.",
            "",
        ]
    )

    return "\n".join(linhas)
