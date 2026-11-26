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


if __name__ == "__main__":
    unittest.main()
