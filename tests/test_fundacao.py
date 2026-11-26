"""Testes unitários e de integração do pacote calculo.fundacao (ACTIFLO 360 e 600)."""

from __future__ import annotations

import math
import unittest
from pathlib import Path

from fundacao.estrutural.bloco_1_estaca import GeometriaBloco1Estaca, verificar_bloco_1_estaca
from fundacao.estrutural.bloco_2_estacas import GeometriaBloco2Estacas, verificar_bloco_2_estacas
from fundacao.estrutural.estaca import verificar_estaca_helice_continua
from fundacao.geotecnia.antunes_cabral import calcular_antunes_cabral
from fundacao.geotecnia.aoki_velloso import calcular_aoki_velloso
from fundacao.geotecnia.capacidade import calcular_capacidade_todos_metodos
from fundacao.geotecnia.decourt_quaresma import calcular_decourt_quaresma
from fundacao.geotecnia.sondagem import carregar_sondagem_yaml
from fundacao.normas.nbr6118 import ACO_CA50, ClasseAgressividade, Concreto, area_barra_cm2
from fundacao.relatorios.memorial import gerar_memorial_markdown
from fundacao.relatorios.quantitativos import calcular_quantitativos_blocos
from fundacao.verificacoes.auditoria import auditar_projeto, carregar_projeto
from fundacao.verificacoes.subpressao import verificar_subpressao_tanque

REPO_ROOT = Path(__file__).resolve().parent.parent


class TestNormas(unittest.TestCase):
    def test_concreto_c40_caa_iv(self) -> None:
        c40 = Concreto(fck_mpa=40.0, caa=ClasseAgressividade.IV)
        self.assertAlmostEqual(c40.fcd_mpa, 40.0 / 1.4, places=3)
        self.assertAlmostEqual(c40.alpha_v2, 0.84, places=3)
        self.assertAlmostEqual(c40.fcd1_mpa, 0.85 * 0.84 * (40.0 / 1.4), places=3)
        self.assertAlmostEqual(c40.fcd2_mpa, 0.60 * 0.84 * (40.0 / 1.4), places=3)
        # 12 Ø 16 mm = 24,13 cm²
        self.assertAlmostEqual(12 * area_barra_cm2(16.0), 24.13, places=2)


class TestGeotecnia(unittest.TestCase):
    def setUp(self) -> None:
        self.sondagem = carregar_sondagem_yaml(
            REPO_ROOT / "projetos" / "sondagens" / "exemplo_hipotetico_basalto.yaml"
        )

    def test_metodos_semi_empiricos_monotonicos(self) -> None:
        c8 = calcular_capacidade_todos_metodos(self.sondagem, 0.40, 8.0, cota_arrasamento_m=237.650)
        c12 = calcular_capacidade_todos_metodos(self.sondagem, 0.40, 12.0, cota_arrasamento_m=237.650)
        self.assertGreater(c12.p_adm_media_tf, c8.p_adm_media_tf)
        self.assertGreater(c12.p_adm_min_tf, c8.p_adm_min_tf)

        # Confere os 3 métodos individualmente
        r_aoki = calcular_aoki_velloso(self.sondagem, 0.40, 12.0, cota_arrasamento_m=237.650)
        r_dec = calcular_decourt_quaresma(self.sondagem, 0.40, 12.0, cota_arrasamento_m=237.650)
        r_ant = calcular_antunes_cabral(self.sondagem, 0.40, 12.0, cota_arrasamento_m=237.650)
        self.assertGreater(float(r_aoki["p_adm_tf"]), 20.0)
        self.assertGreater(float(r_dec["p_adm_tf"]), 20.0)
        self.assertGreater(float(r_ant["p_adm_tf"]), 20.0)

    def test_desconto_escavacao_por_cota(self) -> None:
        # Cota mais profunda (235.562 m) encontra solo mais resistente para o mesmo comprimento L=10 m
        raso = calcular_aoki_velloso(self.sondagem, 0.40, 10.0, cota_arrasamento_m=239.150)
        fundo = calcular_aoki_velloso(self.sondagem, 0.40, 10.0, cota_arrasamento_m=235.562)
        self.assertGreater(float(fundo["p_adm_tf"]), float(raso["p_adm_tf"]))


class TestEstrutural(unittest.TestCase):
    def test_estaca_helice_40cm(self) -> None:
        c40 = Concreto(fck_mpa=40.0, caa=ClasseAgressividade.IV)
        res = verificar_estaca_helice_continua(40.0, 55.0, concreto=c40)
        self.assertTrue(res.atende_durabilidade)
        self.assertTrue(res.atende_compressao)
        self.assertAlmostEqual(res.area_concreto_cm2, math.pi * 40.0 ** 2 / 4.0, places=1)
        self.assertGreater(res.as_min_cm2, 5.0)

    def test_bloco_1_estaca_pbes(self) -> None:
        res = verificar_bloco_1_estaca(nk_tf=55.0, geometria=GeometriaBloco1Estaca())
        self.assertTrue(res.atende_geometria)
        self.assertTrue(res.atende_esmagamento)
        self.assertTrue(res.atende_fendimento)
        self.assertTrue(res.aprovado)

    def test_bloco_2_estacas_pbes_71tf_e_110tf(self) -> None:
        # Caso crítico real PBES (PC22/PC23 = 71 tf)
        res71 = verificar_bloco_2_estacas(nk_tf=71.0, geometria=GeometriaBloco2Estacas())
        self.assertTrue(res71.aprovado)
        self.assertTrue(res71.bloco_rigido)
        self.assertAlmostEqual(res71.as_tirante_adotada_cm2, 24.13, places=2)
        self.assertLess(res71.as_tirante_blevot_cm2, res71.as_tirante_adotada_cm2)

        # Capacidade nominal cheia de 2 estacas (2 x 55 tf = 110 tf) também deve atender com 12 Ø 16
        res110 = verificar_bloco_2_estacas(nk_tf=110.0, geometria=GeometriaBloco2Estacas())
        self.assertTrue(res110.aprovado)
        self.assertTrue(res110.atende_tirante)
        self.assertTrue(res110.atende_no_estaca_nbr6118)
        self.assertTrue(res110.atende_ancoragem)

        # Pilar isolado muito pequeno (20x25 cm) sob 71 tf deve acusar esmagamento do nó CCC (NBR 6118)
        res_esmag = verificar_bloco_2_estacas(
            nk_tf=71.0,
            geometria=GeometriaBloco2Estacas(pilar_ap_cm=20.0, pilar_bp_cm=25.0),
        )
        self.assertFalse(res_esmag.atende_no_pilar_nbr6118)
        self.assertFalse(res_esmag.aprovado)


class TestProjetosActiflo(unittest.TestCase):
    def test_actiflo_360_integridade_e_auditoria(self) -> None:
        cfg, pontos = carregar_projeto(REPO_ROOT / "projetos" / "actiflo_360")
        self.assertEqual(len(pontos), 30)
        res = auditar_projeto(cfg, pontos, p_adm_tf=55.0)
        self.assertEqual(res.n_blocos_1e_pbes, 21)
        self.assertEqual(res.n_blocos_2e_pbes, 9)
        self.assertEqual(res.total_estacas_pbes, 39)
        self.assertAlmostEqual(res.carga_total_tf, 1270.0, places=1)
        # Com P_adm = 55 tf, nenhum ponto do 360 L/s excede
        self.assertEqual(len(res.pontos_excedentes), 0)
        self.assertEqual(res.total_estacas_otimizado, 39)

        quant = calcular_quantitativos_blocos(21, 9)
        # Volume teórico dos 21 blocos (70x70x70) + 9 blocos (70x190x70) = 15,58 m³ (PBES: 15,60 m³)
        self.assertAlmostEqual(quant.volume_concreto_blocos_m3, 15.58, places=2)

    def test_actiflo_600_integridade_e_deteccao_pc59(self) -> None:
        cfg, pontos = carregar_projeto(REPO_ROOT / "projetos" / "actiflo_600")
        self.assertEqual(len(pontos), 85)
        res = auditar_projeto(cfg, pontos, p_adm_tf=55.0)
        self.assertEqual(res.n_blocos_1e_pbes, 83)
        self.assertEqual(res.n_blocos_2e_pbes, 2)
        self.assertEqual(res.total_estacas_pbes, 87)
        self.assertAlmostEqual(res.carga_total_tf, 3023.0, places=1)

        # Com P_adm = 55 tf, PC59 (61 tf em 1 estaca) DEVE ser sinalizado como EXCEDE
        ids_exc = [e.ponto.id for e in res.pontos_excedentes]
        self.assertEqual(ids_exc, ["PC59"])
        self.assertEqual(res.total_estacas_otimizado, 88)

        # Memorial deve gerar corretamente
        md = gerar_memorial_markdown(res, cargas_sensibilidade_tf=[50.0, 55.0, 60.0])
        self.assertIn("ACTIFLO 600 L/s", md)
        self.assertIn("PC59", md)

    def test_subpressao_tanque(self) -> None:
        sub = verificar_subpressao_tanque(
            area_planta_m2=145.0,
            volume_concreto_total_m3=202.2,
            cota_fundo_laje_m=237.8,
            cota_nivel_agua_m=240.0,
            n_estacas=39,
            capacidade_tracao_estaca_tf=15.0,
        )
        self.assertTrue(sub.aprovado)
        self.assertGreater(sub.fs_somente_peso, 1.1)

    def test_sondagens_reais_eta_vila_c_e_fundacao_direta(self) -> None:
        from fundacao.geotecnia.fundacao_direta import (
            calcular_capacidade_vesic,
            carregar_ensaios_yaml,
            estudo_troca_solo,
        )
        from fundacao.verificacoes.cargas_tanque import calcular_cargas_tanque

        sp01 = carregar_sondagem_yaml(REPO_ROOT / "projetos" / "sondagens" / "eta_vila_c_real" / "sp01.yaml")
        sp08 = carregar_sondagem_yaml(REPO_ROOT / "projetos" / "sondagens" / "eta_vila_c_real" / "sp08.yaml")
        self.assertFalse(sp01.hipotetico)
        self.assertAlmostEqual(sp01.cota_rocha_m or 0.0, 226.18, places=2)
        self.assertAlmostEqual(sp08.cota_rocha_m or 0.0, 223.11, places=2)

        # Capacidade em SP-08 (600 L/s) deve superar SP-01 (360 L/s)
        cap_360 = calcular_capacidade_todos_metodos(sp01, 0.40, 11.5, cota_arrasamento_m=237.65)
        cap_600 = calcular_capacidade_todos_metodos(sp08, 0.40, 13.5, cota_arrasamento_m=237.66)
        self.assertGreater(cap_600.p_adm_media_tf, cap_360.p_adm_media_tf)

        # Ensaios reais AI-02 + fundação direta: não rompe por Vesic, mas falha em ELS sem troca
        amostras = carregar_ensaios_yaml(
            REPO_ROOT / "projetos" / "sondagens" / "eta_vila_c_real" / "ensaios_laboratorio.yaml"
        )
        ai02 = amostras["AI-02"]
        vesic = calcular_capacidade_vesic(ai02, b_m=8.4, l_m=20.4, df_m=1.5, fs=3.0)
        self.assertGreater(vesic.q_adm_kpa, 100.0)

        estudo_360 = estudo_troca_solo(
            solo=ai02,
            q_bruta_kpa=86.0,
            b_m=8.4,
            l_m=20.4,
            z_base_laje_m=1.5,
            z_fim_argila_mole_m=4.8,
            espessuras_troca_m=[0.0, 3.3],
        )
        self.assertFalse(estudo_360[0].atende_limite_els)
        self.assertTrue(estudo_360[1].atende_limite_els)

        # Balanço de cargas ACTIFLO 360
        tanque = calcular_cargas_tanque(
            nome="ACTIFLO 360",
            volume_concreto_m3=202.2,
            volume_lastro_enchimento_m3=13.26,
            area_molhada_interna_m2=112.0,
            lamina_agua_m=4.85,
            area_planta_total_m2=145.0,
            carga_total_pbes_tf=1270.0,
        )
        self.assertAlmostEqual(tanque.peso_vazio_total_tf, 536.0, places=0)
        self.assertLess(tanque.pct_dinamico_sobre_pbes, 3.0)

    def test_estudo_exaustivo_e_novos_metodos(self) -> None:
        from fundacao.estrutural.puncao_capitel import dimensionar_capitel_minimo
        from fundacao.geotecnia.grupo_radier_estaqueado import calcular_radier_estaqueado_pdr
        from fundacao.geotecnia.vibracao_cravacao import avaliar_vibracao_cravacao
        from fundacao.verificacoes.confiabilidade import calcular_confiabilidade_lognormal

        # 5 métodos SPT simultâneos em SP-01 real
        sp01 = carregar_sondagem_yaml(REPO_ROOT / "projetos" / "sondagens" / "eta_vila_c_real" / "sp01.yaml")
        res5 = calcular_capacidade_todos_metodos(sp01, 0.70, 11.5, cota_arrasamento_m=237.65, incluir_todos_5=True)
        self.assertEqual(len(res5.resultados), 5)
        self.assertGreater(res5.p_adm_media_tf, 45.0)

        # Vibração de cravação a 4 m do Filtro Velho deve exceder DIN 4150-3 (5 mm/s)
        vib = avaliar_vibracao_cravacao("Filtro Velho", distancia_m=4.0, energia_martelo_kj=45.0)
        self.assertFalse(vib.aprovado_sem_restricao)
        self.assertGreater(vib.ppv_estimado_mm_s, 15.0)

        # Capitel mínimo para estaca Ø70 cm com 95 tf sobre laje de 30 cm deve dispensar punção
        cap = dimensionar_capitel_minimo(nk_tf=95.0, diametro_estaca_cm=70.0, h_laje_cm=30.0)
        self.assertTrue(cap.tem_capitel)
        self.assertTrue(cap.dispensa_armadura_puncao)

        # Radier estaqueado PDR no ACTIFLO 600 com 34 estacas Ø70 deve reduzir recalque em > 65%
        pdr = calcular_radier_estaqueado_pdr(16.9, 23.7, 3023.0, 34, 0.70, 13.5, 4000.0, 45000.0)
        self.assertGreater(pdr.reducao_recalque_pct, 65.0)
        self.assertTrue(pdr.atende_recalque_els)

        # Confiabilidade FORM: com PCE (COV menor), β deve aumentar
        c_sem = calcular_confiabilidade_lognormal("sem PCE", [150.0, 160.0, 155.0], 55.0, cov_modelo=0.22)
        c_com = calcular_confiabilidade_lognormal("com PCE", [150.0, 160.0, 155.0], 55.0, cov_modelo=0.12)
        self.assertGreater(c_com.beta_form, c_sem.beta_form)

    def test_comparativo_economico_solucoes(self) -> None:
        from fundacao.orcamento.comparativo_solucoes import (
            comparar_solucoes_actiflo,
            gerar_relatorio_comparativo_markdown,
        )

        dados = comparar_solucoes_actiflo(raiz_repo=REPO_ROOT)
        self.assertEqual(len(dados["actiflo_360"]), 6)
        self.assertEqual(len(dados["actiflo_600"]), 6)
        # Base original 360 tem exatamente 39 estacas e 523 m perfurados
        s0_360 = dados["actiflo_360"][0]
        self.assertEqual(s0_360["n_estacas"], 39)
        self.assertAlmostEqual(s0_360["metragem_perfurada_m"], 523.0, places=0)
        # Base original 600 tem exatamente 87 estacas e 1.111 m perfurados
        s0_600 = dados["actiflo_600"][0]
        self.assertEqual(s0_600["n_estacas"], 87)
        self.assertAlmostEqual(s0_600["metragem_perfurada_m"], 1111.0, places=0)
        md = gerar_relatorio_comparativo_markdown(dados)
        self.assertIn("ACTIFLO 360", md)
        self.assertIn("ACTIFLO 600", md)

    def test_refinamentos_deterministicos(self) -> None:
        from fundacao.estrutural.estaca import calcular_comprimento_elastico_estaca
        from fundacao.estrutural.laje_fundo import verificar_flexao_laje_fundo
        from fundacao.geotecnia.fundacao_direta import (
            calcular_tempo_adensamento,
            tensao_ponta_rocha_necessaria_mpa,
        )

        # Gaiola de 6 m atende até Ø60 em C40 (CAA IV - ACTIFLO 360), mas Ø70 exige 6,5 m
        c40 = Concreto(fck_mpa=40.0, caa=ClasseAgressividade.IV)
        e60 = calcular_comprimento_elastico_estaca(60.0, concreto=c40)
        e70_c40 = calcular_comprimento_elastico_estaca(70.0, concreto=c40)
        e80_c30 = calcular_comprimento_elastico_estaca(80.0)
        self.assertTrue(e60.atende_gaiola_6m_pbge)
        self.assertFalse(e70_c40.atende_gaiola_6m_pbge)
        self.assertEqual(e70_c40.comprimento_armado_recomendado_m, 6.5)
        self.assertFalse(e80_c30.atende_gaiola_6m_pbge)

        # Flexão da laje de 30 cm em 360-S3 (vão 2,60 m, q=66 kPa) já passa na malha PBES 6,54 cm²/m
        flex_360 = verificar_flexao_laje_fundo(2.60, 66.0, 145.0, as_existente_pbes_cm2_m=6.54)
        self.assertTrue(flex_360.atende_malha_existente)
        self.assertEqual(flex_360.delta_aco_total_kg, 0.0)

        # Tempo de adensamento t90 com cv=0,0085 cm²/s
        tempo_600 = calcular_tempo_adensamento(6.3, 21.3, cv_cm2_s=0.0085)
        self.assertGreater(tempo_600.t90_dias, 90.0)
        self.assertAlmostEqual(tempo_600.recalque_corrigido_sb_cm, 21.3 * 0.80, places=1)

        # Tensão de ponta na rocha em SP-03 (Ø50, 55 tf, RL=56,7 tf) > 2,0 MPa
        qp = tensao_ponta_rocha_necessaria_mpa(55.0, 56.7, 50.0, fs=2.0)
        self.assertGreater(qp, 2.0)

    def test_enchimento_parcial_camaras_e_envoltoria_acoes(self) -> None:
        from fundacao.geotecnia.grupo_radier_estaqueado import calcular_radier_estaqueado_pdr
        from fundacao.verificacoes.cargas_tanque import (
            calcular_cargas_tanque,
            gerar_envoltoria_acoes_tanque,
            verificar_enchimento_parcial_camaras,
        )

        # ACTIFLO 360 (360-S3: 22xØ60) e ACTIFLO 600 (600-S2: 52xØ50)
        c360 = calcular_cargas_tanque("ACTIFLO 360", 205.0, 20.0, 128.0, 5.0, 145.0, 1270.0)
        pdr360 = calcular_radier_estaqueado_pdr(11.4, 12.7, 1270.0, 22, 0.60, 11.5)
        parc360 = verificar_enchimento_parcial_camaras(
            "360-S3",
            c360.peso_vazio_total_tf + max(0.0, c360.parcela_equip_passarelas_folga_tf),
            c360.peso_agua_tf + c360.peso_microareia_lodo_tf,
            12.7,
            22,
            5,
            pdr360.rigidez_radier_estaqueado_kpr_kn_m,
            recalque_direto_cheio_mm=104.8,
        )
        self.assertFalse(parc360.ha_tracao_lado_vazio)
        self.assertTrue(parc360.atende_limite_tanque_estanque_1_1000)
        self.assertLess(parc360.recalque_diferencial_mm, 10.0)
        env360 = gerar_envoltoria_acoes_tanque(c360, 145.0, 22, parc360)
        self.assertEqual(len(env360), 6)
        self.assertGreater(env360[5].carga_vertical_total_tf, env360[2].carga_vertical_total_tf)

        c600 = calcular_cargas_tanque("ACTIFLO 600", 510.0, 45.0, 325.0, 5.0, 365.0, 3023.0)
        pdr600 = calcular_radier_estaqueado_pdr(12.7, 28.4, 3023.0, 52, 0.50, 13.0)
        parc600 = verificar_enchimento_parcial_camaras(
            "600-S2",
            c600.peso_vazio_total_tf + max(0.0, c600.parcela_equip_passarelas_folga_tf),
            c600.peso_agua_tf + c600.peso_microareia_lodo_tf,
            28.4,
            52,
            13,
            pdr600.rigidez_radier_estaqueado_kpr_kn_m,
            recalque_direto_cheio_mm=170.4,
        )
        self.assertFalse(parc600.ha_tracao_lado_vazio)
        self.assertTrue(parc600.atende_limite_tanque_estanque_1_1000)
        self.assertGreater(parc600.recalque_diferencial_fundacao_direta_mm, 50.0)

    def test_reducao_fs_norma_com_pce_nbr6122(self) -> None:
        from fundacao.geotecnia.capacidade import comparar_fs_com_e_sem_pce
        from fundacao.geotecnia.sondagem import carregar_sondagem_yaml

        sp03 = carregar_sondagem_yaml(REPO_ROOT / "projetos" / "sondagens" / "eta_vila_c_real" / "sp03.yaml")
        # Em SP-03 (furo mais raso: L_ef=9,6 m), reduzir FS 2,0 -> 1,6 aumenta P_adm em +25%
        comp_50 = comparar_fs_com_e_sem_pce(sp03, 50.0, 9.6, 237.650, 55.0)
        comp_60 = comparar_fs_com_e_sem_pce(sp03, 60.0, 9.6, 237.650, 58.0)
        self.assertAlmostEqual(comp_50.ganho_capacidade_pct, 25.0, places=0)
        # Mesmo com FS=1,6, Ø50 em SP-03 ainda fica abaixo de 55 tf em solo puro; já Ø60 atende 100% em solo!
        self.assertFalse(comp_50.atende_em_solo_fs_16)
        self.assertTrue(comp_60.atende_em_solo_fs_16)
        self.assertLess(comp_60.qp_rocha_req_fs_16_mpa, comp_50.qp_rocha_req_fs_20_mpa)

    def test_interferencia_elemento_isolado_vs_conjunto(self) -> None:
        from fundacao.geotecnia.grupo_radier_estaqueado import comparar_isolada_vs_conjunto

        comp_360 = comparar_isolada_vs_conjunto("360-S3", 11.4, 12.7, 1270.0, 4, 6, 22, 0.60, 11.5, 2.60)
        comp_600 = comparar_isolada_vs_conjunto("600-S2", 12.7, 28.4, 3023.0, 4, 13, 52, 0.50, 13.0, 2.65)
        self.assertGreater(comp_360.recalque_conjunto_pdr_mm, comp_360.recalque_estaca_isolada_mm)
        self.assertGreater(comp_360.fator_amplificacao_recalque_rs, 2.0)
        self.assertGreater(comp_600.fator_amplificacao_recalque_rs, comp_360.fator_amplificacao_recalque_rs)
        self.assertGreaterEqual(comp_600.espacamento_sobre_d, 4.5)

    def test_simulacao_matricial_monte_carlo_camaras(self) -> None:
        from fundacao.geotecnia.grupo_radier_estaqueado import calcular_radier_estaqueado_pdr
        from fundacao.verificacoes.simulacao_camaras import (
            gerar_camaras_padrao,
            gerar_malha_estacas_2d,
            simular_enchimento_multicamaras_mc,
        )

        pdr360 = calcular_radier_estaqueado_pdr(11.4, 12.7, 1270.0, 22, 0.60, 11.5)
        cam360 = gerar_camaras_padrao(11.4, 12.7, 128.0, 3, 2)
        est360 = gerar_malha_estacas_2d(11.4, 12.7, 4, 6, 22)
        r360 = simular_enchimento_multicamaras_mc(
            "360-S3", 11.4, 12.7, 145.0, 558.5 + 66.4, cam360, est360,
            pdr360.rigidez_radier_estaqueado_kpr_kn_m, 58.0, n_monte_carlo=2000, seed=42,
        )
        # 2^6 = 64 binárias + 2000 MC = 2064 cenários reprodutíveis
        self.assertEqual(r360.n_cenarios_totais, 2064)
        self.assertEqual(r360.n_estacas, 22)
        self.assertFalse(r360.ha_tracao_em_algum_cenario)
        self.assertTrue(r360.atende_limite_estanque_1_1000)
        # Flexão composta oblíqua (2D) supera o caso cheio simétrico (57,7 tf)
        self.assertGreater(r360.n_max_absoluto_tf, r360.carga_media_cheio_tf)
        self.assertEqual(len(r360.mapa_estacas_xy_pico), 22)

        # Reprodutibilidade determinística com mesma seed
        r360_dup = simular_enchimento_multicamaras_mc(
            "360-S3", 11.4, 12.7, 145.0, 558.5 + 66.4, cam360, est360,
            pdr360.rigidez_radier_estaqueado_kpr_kn_m, 58.0, n_monte_carlo=2000, seed=42,
        )
        self.assertEqual(r360.n_max_absoluto_tf, r360_dup.n_max_absoluto_tf)


if __name__ == "__main__":
    unittest.main()
