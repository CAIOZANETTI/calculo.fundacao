"""Geração de memorial de cálculo em Markdown e exportação CSV da auditoria."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Optional

from fundacao.relatorios.quantitativos import calcular_quantitativos_blocos
from fundacao.verificacoes.auditoria import ResultadoAuditoriaProjeto, estudo_sensibilidade_carga_adm
from fundacao.verificacoes.subpressao import ResultadoSubpressao


def gerar_memorial_markdown(
    resultado: ResultadoAuditoriaProjeto,
    subpressao: Optional[ResultadoSubpressao] = None,
    cargas_sensibilidade_tf: Optional[List[float]] = None,
) -> str:
    """Gera memorial técnico completo em Markdown pronto para revisão de engenharia."""
    cfg = resultado.config
    arranque_1e = 86.0 if "600" in cfg.nome else 80.0
    quant = calcular_quantitativos_blocos(
        n_blocos_1e=resultado.n_blocos_1e_pbes,
        n_blocos_2e=resultado.n_blocos_2e_pbes,
        geom_1e=cfg.geometria_bloco_1e,
        geom_2e=cfg.geometria_bloco_2e,
        comprimento_arranque_1e_cm=arranque_1e,
    )

    linhas: List[str] = [
        f"# Memorial de Verificação de Fundações — {cfg.nome}",
        "",
        f"- **Empreendimento:** {cfg.empreendimento}",
        f"- **Referência PBES:** `{cfg.codigo_pbes}`",
        f"- **Concreto / Durabilidade:** C{cfg.fck_mpa:.0f} (`fck = {cfg.fck_mpa:.0f} MPa`, CAA {cfg.caa.value}, cobrimento `{cfg.cobrimento_cm:.1f} cm`)",
        f"- **Estacas:** Hélice Contínua Ø `{cfg.diametro_estaca_cm:.0f} cm` (embutimento `{cfg.embutimento_cm:.0f} cm`), $P_{{\\text{{adm}}}}$ adotada = **{resultado.p_adm_adotada_tf:.1f} tf**",
        "",
        "## 1. Resumo Geral do Carregamento e Alocação",
        "",
        "| Indicador | Valor |",
        "| :--- | ---: |",
        f"| Total de pontos de carga | {resultado.total_pontos} |",
        f"| Carga vertical característica total ($\\sum N_k$) | {resultado.carga_total_tf:,.1f} tf |",
        f"| Blocos de 1 estaca (PBES) | {resultado.n_blocos_1e_pbes} |",
        f"| Blocos de 2 estacas (PBES) | {resultado.n_blocos_2e_pbes} |",
        f"| Total de estacas (PBES) | {resultado.total_estacas_pbes} |",
        f"| Total de estacas recalculado ($P_{{\\text{{adm}}}} = {resultado.p_adm_adotada_tf:.1f}$ tf) | {resultado.total_estacas_otimizado} |",
        f"| Ponto mais carregado (1 estaca) | {resultado.ponto_mais_solicitado_1e} |",
        f"| Ponto mais carregado (2 estacas) | {resultado.ponto_mais_solicitado_2e} |",
        f"| Máxima carga atuante por estaca (PBES) | {resultado.max_carga_por_estaca_pbes_tf:.1f} tf |",
        f"| Pontos que excedem $P_{{\\text{{adm}}}}$ no PBES | **{len(resultado.pontos_excedentes)}** |",
        "",
    ]

    if resultado.pontos_excedentes:
        linhas.append("### ⚠️ Pontos de Carga Acima da Capacidade Admissível Adotada")
        linhas.append("")
        linhas.append("| Ponto | $N_k$ (tf) | Estacas PBES | Carga/Estaca (tf) | Estacas Necessárias | Observação |")
        linhas.append("| :--- | ---: | :---: | ---: | :---: | :--- |")
        for ex in resultado.pontos_excedentes:
            linhas.append(
                f"| `{ex.ponto.id}` | {ex.ponto.nk_tf:.1f} | {ex.ponto.n_estacas_pbes} | "
                f"{ex.carga_por_estaca_pbes_tf:.1f} | {ex.n_estacas_necessario} | {ex.observacao_auditoria} |"
            )
        linhas.append("")

    # 2. Verificação estrutural da estaca
    ve = resultado.verificacao_estaca_critica
    linhas.extend(
        [
            "## 2. Verificação Estrutural da Estaca (Fuste)",
            "",
            f"- **Seção:** Ø `{ve.diametro_cm:.0f} cm` ($A_c = {ve.area_concreto_cm2:.1f}\\text{{ cm}}^2$)",
            f"- **Tensão média atuante máxima:** `{ve.tensao_atuante_mpa:.2f} MPa` (para `{ve.carga_atuante_tf:.1f} tf`) vs. limite adotado `{ve.tensao_adm_mpa:.2f} MPa` (`{ve.carga_estrutural_adm_tf:.1f} tf`)",
            f"- **Taxa de utilização à compressão:** `{ve.taxa_utilizacao_compressao * 100:.1f}%` — **{'APROVADO' if ve.atende_compressao else 'REPROVADO'}**",
            f"- **Armadura longitudinal mínima (0,4%):** `{ve.as_min_cm2:.2f} cm²` → Sugestão: `{ve.sugestao_armadura}` (mín. `{ve.comprimento_armado_min_m:.1f} m`)",
            "",
        ]
    )

    # 3. Verificação estrutural dos blocos
    linhas.append("## 3. Verificação Estrutural dos Blocos sobre Estacas")
    linhas.append("")
    if resultado.verificacao_bloco_1e_critico:
        b1 = resultado.verificacao_bloco_1e_critico
        linhas.extend(
            [
                f"### 3.1 Bloco de 1 Estaca (`{cfg.geometria_bloco_1e.largura_x_cm:.0f}×{cfg.geometria_bloco_1e.largura_y_cm:.0f}×{cfg.geometria_bloco_1e.altura_h_cm:.0f} cm`) — Caso Crítico ($N_k = {b1.nk_tf:.1f}$ tf)",
                "",
                f"- **Folga à borda:** `{b1.folga_borda_cm:.1f} cm` (mín. 15,0 cm) — {'OK' if b1.atende_geometria else 'REVISAR'}",
                f"- **Tensão de contato pilar / estaca:** `{b1.tensao_contato_pilar_mpa:.2f} MPa` / `{b1.tensao_contato_estaca_mpa:.2f} MPa` (limite $f_{{cd1}} = {b1.fcd1_limite_mpa:.2f}$ MPa) — {'OK' if b1.atende_esmagamento else 'REVISAR'}",
                f"- **Fendimento transversal:** $F_{{td}} = {b1.forca_fendimento_kn:.1f}$ kN → $A_{{s,\\text{{req}}}} = {b1.as_fendimento_req_cm2:.2f}\\text{{ cm}}^2$ vs. adotado `{b1.as_horizontal_adotada_cm2:.2f} cm²` — **{'APROVADO' if b1.aprovado else 'REVISAR'}**",
                "",
            ]
        )

    if resultado.verificacao_bloco_2e_critico:
        b2 = resultado.verificacao_bloco_2e_critico
        b2c = resultado.verificacao_bloco_2e_capacidade_cheia
        linhas.extend(
            [
                f"### 3.2 Bloco de 2 Estacas (`{cfg.geometria_bloco_2e.largura_b_cm:.0f}×{cfg.geometria_bloco_2e.comprimento_l_cm:.0f}×{cfg.geometria_bloco_2e.altura_h_cm:.0f} cm`, $e = {cfg.geometria_bloco_2e.espacamento_e_cm:.0f}$ cm) — Bielas e Tirantes",
                "",
                "| Verificação | Caso Crítico PBES | Capacidade Cheia ($2\\cdot P_{\\text{adm}}$) | Limite / Adotado |",
                "| :--- | ---: | ---: | ---: |",
                f"| Carga característica $N_k$ (tf) | {b2.nk_tf:.1f} | {b2c.nk_tf:.1f} | — |",
                f"| Altura útil $d$ (cm) / Ângulo $\\theta$ | {b2.altura_util_d_cm:.1f} cm / {b2.angulo_biela_graus:.1f}° | {b2c.altura_util_d_cm:.1f} cm / {b2c.angulo_biela_graus:.1f}° | 45°–55° (Blévot) |",
                f"| Tração no tirante $R_{{sd,\\text{{Blévot}}}}$ (kN) | {b2.rsd_blevot_kn:.1f} | {b2c.rsd_blevot_kn:.1f} | — |",
                f"| Armadura requerida $A_{{s,\\text{{Blévot}}}}$ (cm²) | {b2.as_tirante_blevot_cm2:.2f} | {b2c.as_tirante_blevot_cm2:.2f} | **{b2.as_tirante_adotada_cm2:.2f} cm²** ({cfg.n_barras_tirante_2e} Ø {cfg.bitola_tirante_2e_mm:g}) |",
                f"| Tensão nó pilar CCC $\\sigma_{{cd,p}}$ (MPa) | {b2.sigma_biela_pilar_mpa:.2f} | {b2c.sigma_biela_pilar_mpa:.2f} | $f_{{cd1}} = {b2.limite_pilar_nbr6118_mpa:.2f}$ MPa |",
                f"| Tensão nó estaca CCT $\\sigma_{{cd,e}}$ (MPa) | {b2.sigma_biela_estaca_mpa:.2f} | {b2c.sigma_biela_estaca_mpa:.2f} | $f_{{cd2}} = {b2.limite_estaca_nbr6118_mpa:.2f}$ MPa |",
                f"| Ancoragem $l_{{b,\\text{{nec}}}}$ com gancho (cm) | {b2.lb_gancho_nec_cm:.1f} | {b2c.lb_gancho_nec_cm:.1f} | disp. `{b2.comprimento_disp_ancoragem_cm:.1f} cm` |",
                f"| Status | **{'APROVADO' if b2.aprovado else 'REVISAR'}** | **{'APROVADO' if b2c.aprovado else 'REVISAR'}** | — |",
                "",
            ]
        )

    sec = 4

    # Geotecnia por cota (se sondagem fornecida)
    if resultado.dimensionamento_geotecnico_por_cota:
        linhas.append(f"## {sec}. Pré-Dimensionamento Geotécnico por Cota de Arrasamento")
        sec += 1
        linhas.append("")
        algum_hip = any(
            v is not None and v.hipotetico for v in resultado.dimensionamento_geotecnico_por_cota.values()
        )
        if algum_hip:
            linhas.append(
                "> ⚠️ **ATENÇÃO:** Calculado com perfil de sondagem **HIPOTÉTICO** (substituir pelos laudos SPT reais do `2. PBGE`)."
            )
            linhas.append("")
        linhas.append("| Cota Arrasamento (m) | Compr. Recomendado $L$ (m) | Cota Ponta (m) | $P_{\\text{adm,mín}}$ (tf) | $P_{\\text{adm,média}}$ (tf) | Tração Adm. (tf) |")
        linhas.append("| ---: | ---: | ---: | ---: | ---: | ---: |")
        for cota, res_geo in sorted(resultado.dimensionamento_geotecnico_por_cota.items()):
            if res_geo is None:
                linhas.append(f"| {cota:.3f} | *Não atingiu na sondagem* | — | — | — | — |")
            else:
                linhas.append(
                    f"| {cota:.3f} | {res_geo.comprimento_m:.1f} | {res_geo.cota_ponta_m:.3f} | "
                    f"{res_geo.p_adm_min_tf:.1f} | {res_geo.p_adm_media_tf:.1f} | {res_geo.rl_tracao_min_tf:.1f} |"
                )
        linhas.append("")

    # Subpressão (se fornecida)
    if subpressao is not None:
        linhas.extend(
            [
                f"## {sec}. Verificação de Subpressão / Flutuação (Tanque Vazio)",
                "",
                f"- **Lâmina de subpressão:** `{subpressao.lamina_subpressao_m:.2f} m` (NA `{subpressao.cota_nivel_agua_m:.2f} m` vs. fundo `{subpressao.cota_fundo_laje_m:.2f} m`)",
                f"- **Empuxo ascensional:** `{subpressao.empuxo_subpressao_tf:.1f} tf` vs. peso próprio estrutura `{subpressao.peso_proprio_estrutura_tf:.1f} tf`",
                f"- **FS somente peso próprio:** `{subpressao.fs_somente_peso:.2f}` | **FS com tração das estacas:** `{subpressao.fs_com_estacas:.2f}` (mín. `{subpressao.fs_minimo:.2f}`)",
                f"- **Resultado:** **{'APROVADO' if subpressao.aprovado else 'REPROVADO'}**",
                "",
            ]
        )
        sec += 1

    # Quantitativos comparados ao PBES
    linhas.extend(
        [
            f"## {sec}. Quantitativos dos Blocos (Calculado vs. Resumo PBES)",
            "",
            "| Item | Calculado (Geometria Blocos) | Resumo PBES (Pranchas) |",
            "| :--- | ---: | ---: |",
            f"| Volume de concreto dos blocos (m³) | {quant.volume_concreto_blocos_m3:.2f} | {cfg.volume_blocos_pbes_m3:.2f} |",
            f"| Área lateral de fôrmas dos blocos (m²) | {quant.area_forma_blocos_m2:.2f} | {cfg.area_forma_blocos_pbes_m2:.2f} |",
            f"| Aço CA-50 nos blocos — total (kg) | {quant.peso_aco_total_blocos_kg:.1f} | — |",
            f"| Taxa média de aço nos blocos (kg/m³) | {quant.taxa_aco_kg_m3:.1f} | — |",
            "",
            f"*Detalhamento do aço nos blocos por bitola:* Ø6,3 = `{quant.aco_por_bitola_kg[6.3]:.1f} kg` | "
            f"Ø8,0 = `{quant.aco_por_bitola_kg[8.0]:.1f} kg` | Ø16,0 = `{quant.aco_por_bitola_kg[16.0]:.1f} kg`.",
            "",
        ]
    )
    sec += 1

    # Sensibilidade
    if cargas_sensibilidade_tf:
        sens = estudo_sensibilidade_carga_adm([a.ponto for a in resultado.auditoria_pontos], cargas_sensibilidade_tf)
        linhas.extend(
            [
                f"## {sec}. Estudo de Sensibilidade ($P_{{\\text{{adm}}}}$ vs. Quantidade de Estacas)",
                "",
                "| $P_{\\text{adm}}$ (tf/estaca) | Blocos 1 Est. | Blocos 2 Est. | Blocos 3+ Est. | Total Estacas | Carga Média/Estaca (tf) |",
                "| ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for s in sens:
            linhas.append(
                f"| {s['p_adm_tf']:.0f} | {s['blocos_1e']} | {s['blocos_2e']} | "
                f"{s['blocos_3e_ou_mais']} | **{s['total_estacas']}** | {s['carga_media_estaca_tf']:.1f} |"
            )
        linhas.append("")

    return "\n".join(linhas)


def exportar_auditoria_csv(resultado: ResultadoAuditoriaProjeto, destino: str | Path) -> Path:
    """Exporta tabela ponto a ponto da auditoria em formato CSV."""
    path = Path(destino)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(
            [
                "id",
                "tipo_elemento",
                "nk_tf",
                "cota_topo_bloco_m",
                "cota_arrasamento_m",
                "n_estacas_pbes",
                "carga_por_estaca_pbes_tf",
                "n_estacas_necessario",
                "taxa_utilizacao_pbes",
                "status",
                "observacao",
            ]
        )
        for a in resultado.auditoria_pontos:
            writer.writerow(
                [
                    a.ponto.id,
                    a.ponto.tipo_elemento,
                    f"{a.ponto.nk_tf:.1f}",
                    f"{a.ponto.cota_topo_bloco_m:.3f}",
                    f"{a.ponto.cota_arrasamento_m:.3f}",
                    a.ponto.n_estacas_pbes,
                    f"{a.carga_por_estaca_pbes_tf:.2f}",
                    a.n_estacas_necessario,
                    f"{a.taxa_utilizacao_pbes:.3f}",
                    a.status,
                    a.observacao_auditoria,
                ]
            )
    return path
