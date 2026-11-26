"""Interface de linha de comando (CLI) do repositório calculo.fundacao."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

import yaml

from fundacao.geotecnia.capacidade import curva_capacidade_por_comprimento
from fundacao.geotecnia.fundacao_direta import (
    calcular_capacidade_vesic,
    carregar_ensaios_yaml,
    estudo_troca_solo,
)
from fundacao.geotecnia.sondagem import carregar_sondagem_yaml
from fundacao.relatorios.memorial import exportar_auditoria_csv, gerar_memorial_markdown
from fundacao.verificacoes.auditoria import (
    auditar_projeto,
    carregar_projeto,
    estudo_sensibilidade_carga_adm,
)
from fundacao.verificacoes.cargas_tanque import calcular_cargas_tanque
from fundacao.verificacoes.subpressao import verificar_subpressao_tanque


def _resolver_pasta_projeto(nome_ou_caminho: str) -> Path:
    candidato = Path(nome_ou_caminho)
    if candidato.is_dir():
        return candidato
    em_projetos = Path("projetos") / nome_ou_caminho
    if em_projetos.is_dir():
        return em_projetos
    raise FileNotFoundError(
        f"Projeto '{nome_ou_caminho}' não encontrado. Informe um caminho válido ou 'actiflo_360' / 'actiflo_600'."
    )


def _cmd_auditar(args: argparse.Namespace) -> int:
    pasta = _resolver_pasta_projeto(args.projeto)
    config, pontos = carregar_projeto(pasta)
    sondagem = carregar_sondagem_yaml(args.sondagem) if args.sondagem else None

    res = auditar_projeto(
        config=config,
        pontos=pontos,
        p_adm_tf=args.p_adm,
        sondagem=sondagem,
        criterio_geotecnico=args.criterio,
    )

    print(f"=== AUDITORIA: {config.nome} ({config.codigo_pbes}) ===")
    print(f"Pontos de carga: {res.total_pontos} | Carga total: {res.carga_total_tf:.1f} tf")
    print(
        f"PBES: {res.n_blocos_1e_pbes}x(1 est) + {res.n_blocos_2e_pbes}x(2 est) = "
        f"{res.total_estacas_pbes} estacas | Recalculado (P_adm={res.p_adm_adotada_tf:.1f} tf): {res.total_estacas_otimizado} estacas"
    )
    print(f"Crítico 1 estaca: {res.ponto_mais_solicitado_1e} | Crítico 2 estacas: {res.ponto_mais_solicitado_2e}")
    print(
        f"Estaca Ø{res.verificacao_estaca_critica.diametro_cm:.0f} cm: "
        f"atuante={res.verificacao_estaca_critica.carga_atuante_tf:.1f} tf / "
        f"adm_estr={res.verificacao_estaca_critica.carga_estrutural_adm_tf:.1f} tf "
        f"({'OK' if res.verificacao_estaca_critica.atende_compressao else 'EXCEDE'})"
    )
    if res.verificacao_bloco_2e_critico:
        b2 = res.verificacao_bloco_2e_critico
        print(
            f"Bloco 2 estacas (crítico {b2.nk_tf:.0f} tf): θ={b2.angulo_biela_graus:.1f}°, "
            f"As_req(Blévot)={b2.as_tirante_blevot_cm2:.2f} cm² vs adotado={b2.as_tirante_adotada_cm2:.2f} cm² "
            f"({'APROVADO' if b2.aprovado else 'REVISAR'})"
        )
    if res.pontos_excedentes:
        print(f"\n⚠️  {len(res.pontos_excedentes)} ponto(s) excedem P_adm = {res.p_adm_adotada_tf:.1f} tf:")
        for ex in res.pontos_excedentes:
            print(f"  - {ex.ponto.id}: {ex.observacao_auditoria}")
    else:
        print("\n✅ Nenhum ponto excede P_adm adotada.")

    if args.csv_out:
        exportar_auditoria_csv(res, args.csv_out)
        print(f"\nCSV exportado em: {args.csv_out}")
    return 0


def _cmd_sensibilidade(args: argparse.Namespace) -> int:
    pasta = _resolver_pasta_projeto(args.projeto)
    config, pontos = carregar_projeto(pasta)
    cargas = [float(x) for x in args.cargas.split(",")]
    cenarios = estudo_sensibilidade_carga_adm(pontos, cargas)

    print(f"=== SENSIBILIDADE P_adm — {config.nome} ===")
    print(f"{'P_adm (tf)':>10} | {'1 Est.':>6} | {'2 Est.':>6} | {'3+ Est.':>7} | {'Total Est.':>10} | {'Média/Est (tf)':>14}")
    print("-" * 68)
    for c in cenarios:
        print(
            f"{c['p_adm_tf']:>10.1f} | {c['blocos_1e']:>6} | {c['blocos_2e']:>6} | "
            f"{c['blocos_3e_ou_mais']:>7} | {c['total_estacas']:>10} | {c['carga_media_estaca_tf']:>14.1f}"
        )
    return 0


def _cmd_memorial(args: argparse.Namespace) -> int:
    pasta = _resolver_pasta_projeto(args.projeto)
    config, pontos = carregar_projeto(pasta)
    sondagem = carregar_sondagem_yaml(args.sondagem) if args.sondagem else None

    res = auditar_projeto(
        config=config,
        pontos=pontos,
        p_adm_tf=args.p_adm,
        sondagem=sondagem,
        criterio_geotecnico=args.criterio,
    )

    subp = None
    if args.cota_na is not None:
        cota_fundo_min = min(p.cota_topo_bloco_m for p in pontos)
        tracao_est = 0.0
        if res.dimensionamento_geotecnico_por_cota:
            tracoes = [v.rl_tracao_min_tf for v in res.dimensionamento_geotecnico_por_cota.values() if v is not None]
            tracao_est = min(tracoes) if tracoes else 0.0
        subp = verificar_subpressao_tanque(
            area_planta_m2=config.area_planta_aprox_m2,
            volume_concreto_total_m3=config.volume_concreto_total_pbes_m3,
            cota_fundo_laje_m=cota_fundo_min,
            cota_nivel_agua_m=args.cota_na,
            n_estacas=res.total_estacas_pbes,
            capacidade_tracao_estaca_tf=tracao_est,
        )

    cargas_sens = [45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0]
    md = gerar_memorial_markdown(res, subpressao=subp, cargas_sensibilidade_tf=cargas_sens)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(f"Memorial salvo em: {out_path}")

    if args.csv_out:
        exportar_auditoria_csv(res, args.csv_out)
        print(f"Tabela de auditoria CSV salva em: {args.csv_out}")
    return 0


def _cmd_geotecnia(args: argparse.Namespace) -> int:
    sondagem = carregar_sondagem_yaml(args.sondagem)
    cota_arr = sondagem.cota_boca_m if args.cota_arrasamento is None else args.cota_arrasamento
    comprimentos = [float(x) for x in args.comprimentos.split(",")]
    curva = curva_capacidade_por_comprimento(
        sondagem=sondagem,
        diametro_m=args.diametro_cm / 100.0,
        cota_arrasamento_m=cota_arr,
        comprimentos_m=comprimentos,
        fs=args.fs,
    )

    tag = " [PERFIL HIPOTÉTICO]" if sondagem.hipotetico else " [SONDAGEM REAL]"
    rocha_info = f" | Rocha={sondagem.prof_rocha_m:.2f} m (cota {sondagem.cota_rocha_m:.2f} m)" if sondagem.prof_rocha_m else ""
    print(f"=== CAPACIDADE GEOTÉCNICA — {sondagem.codigo}{tag}{rocha_info} ===")
    print(f"Ø{args.diametro_cm:.0f} cm | Arrasamento {cota_arr:.3f} m | N.A.={sondagem.nivel_agua_prof_m} m")
    print(f"{'L (m)':>6} | {'Cota Ponta':>10} | {'Aoki (tf)':>10} | {'Décourt (tf)':>12} | {'Antunes (tf)':>12} | {'Mín (tf)':>9} | {'Média (tf)':>10}")
    print("-" * 82)
    for item in curva:
        aoki, dec, ant = item.resultados[0].p_adm_tf, item.resultados[1].p_adm_tf, item.resultados[2].p_adm_tf
        print(
            f"{item.comprimento_m:>6.1f} | {item.cota_ponta_m:>10.3f} | {aoki:>10.1f} | "
            f"{dec:>12.1f} | {ant:>12.1f} | {item.p_adm_min_tf:>9.1f} | {item.p_adm_media_tf:>10.1f}"
        )
    return 0


def _cmd_tanque(args: argparse.Namespace) -> int:
    pasta = _resolver_pasta_projeto(args.projeto)
    config, pontos = carregar_projeto(pasta)
    with (pasta / "config.yaml").open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    est = raw["estrutura"]
    ref = raw["referencia_pbes"]
    vol_lastro_ench = float(ref.get("lastro_concreto_simples_m3", 0.0)) + float(ref.get("enchimento_m3", 0.0))

    res = calcular_cargas_tanque(
        nome=config.nome,
        volume_concreto_m3=config.volume_concreto_total_pbes_m3,
        volume_lastro_enchimento_m3=vol_lastro_ench,
        area_molhada_interna_m2=float(est["area_molhada_interna_m2"]),
        lamina_agua_m=float(est["lamina_agua_m"]),
        area_planta_total_m2=config.area_planta_aprox_m2,
        carga_total_pbes_tf=sum(p.nk_tf for p in pontos),
    )

    print(f"=== BALANÇO DE CARGAS DO TANQUE — {res.nome} ===")
    print(f"Concreto armado + lastro/enchimento (VAZIO) : {res.peso_vazio_total_tf:7.1f} tf  (q_méd = {res.tensao_media_vazio_kpa:.1f} kPa)")
    print(f"Volume de água (operação)                   : {res.volume_liquido_m3:7.1f} m³ -> {res.peso_agua_tf:.1f} tf")
    print(f"Microareia + lodo                           : {res.peso_microareia_lodo_tf:7.1f} tf")
    print(f"Equipamentos + passarelas + folga PBES      : {res.parcela_equip_passarelas_folga_tf:7.1f} tf")
    print(f"TOTAL CARACTERÍSTICO PBES                   : {res.carga_total_pbes_tf:7.1f} tf  (q_méd = {res.tensao_media_pbes_kpa:.1f} kPa)")
    print(f"Acréscimo dinâmico típico agitadores (~3%)  : +{res.acrescimo_dinamico_agitadores_tf:6.1f} tf (+{res.pct_dinamico_sobre_pbes:.2f}% do total)")
    return 0


def _cmd_direta(args: argparse.Namespace) -> int:
    pasta = _resolver_pasta_projeto(args.projeto)
    config, pontos = carregar_projeto(pasta)
    with (pasta / "config.yaml").open("r", encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    est = raw["estrutura"]
    b_m = float(est["largura_b_m"])
    l_m = float(est["comprimento_l_m"])
    z_base = float(est.get("z_base_laje_m", 1.5))
    z_mole = float(est.get("z_fim_argila_mole_m", 4.8))
    q_bruta_kpa = (sum(p.nk_tf for p in pontos) / config.area_planta_aprox_m2) * 9.80665

    amostras = carregar_ensaios_yaml(args.ensaios)
    solo = amostras[args.amostra]
    vesic = calcular_capacidade_vesic(solo, b_m=b_m, l_m=l_m, df_m=z_base, fs=3.0)
    trocas = [float(x) for x in args.trocas.split(",")]
    estudo = estudo_troca_solo(
        solo=solo,
        q_bruta_kpa=q_bruta_kpa,
        b_m=b_m,
        l_m=l_m,
        z_base_laje_m=z_base,
        z_fim_argila_mole_m=z_mole,
        espessuras_troca_m=trocas,
    )

    print(f"=== FUNDAÇÃO DIRETA (RADIER) E TROCA DE SOLO — {config.nome} ===")
    print(f"Amostra: {solo.nome} (c'={solo.coesao_kpa} kPa, φ'={solo.angulo_atrito_graus}°, e0={solo.e0}, σ'vm={solo.tensao_pre_adensamento_kpa} kPa, Cc={solo.cc})")
    print(f"Radier {b_m:.1f}×{l_m:.1f} m | q_bruta = {q_bruta_kpa:.1f} kPa | Vesic q_adm(FS=3) = {vesic.q_adm_kpa:.1f} kPa")
    print(f"\n{'Troca (m)':>9} | {'Mole Rem. (m)':>13} | {'Rec. Líq. (cm)':>14} | {'Rec. Bruto (cm)':>15} | {'ELS ≤ 3 cm':>10}")
    print("-" * 72)
    for r in estudo:
        ok = "SIM" if r.atende_limite_els else "NÃO"
        print(
            f"{r.espessura_troca_m:>9.1f} | {r.espessura_mole_remanescente_m:>13.1f} | "
            f"{r.recalque_total_liq_cm:>14.1f} | {r.recalque_total_bruto_cm:>15.1f} | {ok:>10}"
        )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fundacao",
        description="Cálculo e auditoria de fundações profundas e diretas (NBR 6122 / NBR 6118).",
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p_aud = sub.add_parser("auditar", help="Audita cargas, estacas e blocos de um projeto (ex.: actiflo_360, actiflo_600).")
    p_aud.add_argument("projeto", help="Nome em projetos/ (actiflo_360, actiflo_600) ou caminho.")
    p_aud.add_argument("--p-adm", type=float, default=None, help="Capacidade admissível por estaca (tf).")
    p_aud.add_argument("--sondagem", type=str, default=None, help="Caminho para YAML de sondagem SPT.")
    p_aud.add_argument("--criterio", choices=["media", "minimo"], default="media")
    p_aud.add_argument("--csv-out", type=str, default=None, help="Exporta tabela ponto a ponto em CSV.")
    p_aud.set_defaults(func=_cmd_auditar)

    p_sens = sub.add_parser("sensibilidade", help="Estudo paramétrico de P_adm vs. número de estacas.")
    p_sens.add_argument("projeto", help="Nome do projeto ou caminho.")
    p_sens.add_argument("--cargas", default="45,50,55,60,65,70,75", help="Lista de P_adm (tf) separadas por vírgula.")
    p_sens.set_defaults(func=_cmd_sensibilidade)

    p_mem = sub.add_parser("memorial", help="Gera memorial de cálculo em Markdown (e CSV opcional).")
    p_mem.add_argument("projeto", help="Nome do projeto ou caminho.")
    p_mem.add_argument("--out", required=True, help="Arquivo Markdown de saída.")
    p_mem.add_argument("--csv-out", default=None, help="Arquivo CSV de auditoria opcional.")
    p_mem.add_argument("--p-adm", type=float, default=None, help="P_adm por estaca (tf).")
    p_mem.add_argument("--sondagem", type=str, default=None, help="YAML de sondagem SPT.")
    p_mem.add_argument("--criterio", choices=["media", "minimo"], default="media")
    p_mem.add_argument("--cota-na", type=float, default=None, help="Cota do nível d'água (m) para verificação de subpressão.")
    p_mem.set_defaults(func=_cmd_memorial)

    p_geo = sub.add_parser("geotecnia", help="Calcula curva P_adm(L) pelos 3 métodos semi-empíricos.")
    p_geo.add_argument("sondagem", help="Caminho para arquivo YAML de sondagem SPT.")
    p_geo.add_argument("--diametro-cm", type=float, default=40.0, help="Diâmetro da estaca (cm).")
    p_geo.add_argument("--cota-arrasamento", type=float, default=None, help="Cota de arrasamento da estaca (m).")
    p_geo.add_argument("--comprimentos", default="6,8,10,12,14,16", help="Comprimentos L (m) separados por vírgula.")
    p_geo.add_argument("--fs", type=float, default=2.0, help="Fator de segurança global (NBR 6122).")
    p_geo.set_defaults(func=_cmd_geotecnia)

    p_tanq = sub.add_parser("tanque", help="Balanço de cargas do tanque (vazio vs. cheio estático vs. operação/agitadores).")
    p_tanq.add_argument("projeto", help="Nome do projeto ou caminho.")
    p_tanq.set_defaults(func=_cmd_tanque)

    p_dir = sub.add_parser("direta", help="Avalia fundação direta (radier), recalque por adensamento e troca de solo.")
    p_dir.add_argument("projeto", help="Nome do projeto ou caminho.")
    p_dir.add_argument(
        "--ensaios",
        default="projetos/sondagens/eta_vila_c_real/ensaios_laboratorio.yaml",
        help="YAML de ensaios de cisalhamento e adensamento.",
    )
    p_dir.add_argument("--amostra", default="AI-02", help="Nome da amostra (ex.: AI-01, AI-02).")
    p_dir.add_argument("--trocas", default="0,1.5,2.5,3.3", help="Espessuras de troca de solo (m) separadas por vírgula.")
    p_dir.set_defaults(func=_cmd_direta)

    p_ex = sub.add_parser(
        "exaustivo",
        help="Executa o estudo exaustivo determinístico (5 métodos SPT, confiabilidade FORM, vibração, capitéis e PDR).",
    )
    p_ex.add_argument("--out-md", default="saidas/estudo_exaustivo_actiflo_360_600.md", help="Memorial Markdown de saída.")
    p_ex.add_argument("--out-json", default="saidas/estudo_exaustivo_resultados.json", help="Resultados estruturados em JSON.")
    p_ex.set_defaults(func=_cmd_exaustivo)

    p_custo = sub.add_parser(
        "comparar-custos",
        help="Comparativo técnico-econômico determinístico entre PBGE original e soluções alternativas.",
    )
    p_custo.add_argument("--precos", default="projetos/precos_unitarios_sinapi_pr.yaml", help="YAML de preços unitários.")
    p_custo.add_argument("--out-md", default="saidas/comparativo_economico_actiflo_360_600.md", help="Relatório Markdown de saída.")
    p_custo.add_argument("--out-json", default="saidas/comparativo_economico_resultados.json", help="JSON estruturado de saída.")
    p_custo.set_defaults(func=_cmd_comparar_custos)

    return parser


def _cmd_exaustivo(args: argparse.Namespace) -> int:
    from fundacao.relatorios.estudo_exaustivo import executar_estudo_exaustivo

    executar_estudo_exaustivo(raiz_repo=".", out_md=args.out_md, out_json=args.out_json)
    print(f"Estudo exaustivo gerado em:\n  - {args.out_md}\n  - {args.out_json}")
    return 0


def _cmd_comparar_custos(args: argparse.Namespace) -> int:
    import json
    from fundacao.orcamento.comparativo_solucoes import (
        comparar_solucoes_actiflo,
        gerar_relatorio_comparativo_markdown,
    )

    dados = comparar_solucoes_actiflo(raiz_repo=".", caminho_precos=args.precos)
    md = gerar_relatorio_comparativo_markdown(dados)
    p_md = Path(args.out_md)
    p_md.parent.mkdir(parents=True, exist_ok=True)
    p_md.write_text(md, encoding="utf-8")

    p_json = Path(args.out_json)
    p_json.parent.mkdir(parents=True, exist_ok=True)
    p_json.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Comparativo econômico gerado em:\n  - {args.out_md}\n  - {args.out_json}")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
