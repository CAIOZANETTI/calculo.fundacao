"""Balanço de cargas de tanques de tratamento (vazio vs. cheio estático vs. operando com agitadores)."""

from __future__ import annotations

from dataclasses import dataclass

from fundacao.normas.nbr6118 import TF_PARA_KN


@dataclass(frozen=True)
class ResultadoCargasTanque:
    nome: str
    peso_concreto_armado_tf: float
    peso_lastro_enchimento_tf: float
    peso_vazio_total_tf: float
    volume_liquido_m3: float
    peso_agua_tf: float
    peso_microareia_lodo_tf: float
    acrescimo_dinamico_agitadores_tf: float
    carga_estatica_cheio_sem_equip_tf: float
    carga_operando_com_dinamico_tf: float
    carga_total_pbes_tf: float
    parcela_equip_passarelas_folga_tf: float
    tensao_media_vazio_kpa: float
    tensao_media_pbes_kpa: float
    pct_dinamico_sobre_pbes: float


def calcular_cargas_tanque(
    nome: str,
    volume_concreto_m3: float,
    volume_lastro_enchimento_m3: float,
    area_molhada_interna_m2: float,
    lamina_agua_m: float,
    area_planta_total_m2: float,
    carga_total_pbes_tf: float,
    concentracao_microareia_kg_m3: float = 8.0,
    fator_dinamico_agitadores: float = 0.03,
    gamma_concreto_tf_m3: float = 2.50,
    gamma_lastro_tf_m3: float = 2.30,
) -> ResultadoCargasTanque:
    """Calcula a decomposição das cargas verticais em cenários vazio, estático cheio e operação.

    Parâmetros típicos ACTIFLO:
      - concentracao_microareia_kg_m3: 8 kg/m³ (microareia em suspensão + leito de fundo)
      - fator_dinamico_agitadores: 0,03 (majoração conservadora de 3% sobre a massa líquida agitada)
    """
    w_conc = volume_concreto_m3 * gamma_concreto_tf_m3
    w_lastro = volume_lastro_enchimento_m3 * gamma_lastro_tf_m3
    w_vazio = w_conc + w_lastro

    v_liq = area_molhada_interna_m2 * lamina_agua_m
    w_agua = v_liq * 1.0  # 1,0 tf/m³
    w_areia = v_liq * (concentracao_microareia_kg_m3 / 1000.0)
    w_din = fator_dinamico_agitadores * w_agua

    w_cheio_est = w_vazio + w_agua
    w_oper = w_cheio_est + w_areia + w_din
    w_equip = carga_total_pbes_tf - (w_vazio + w_agua + w_areia)

    tensao_vazio_kpa = (w_vazio / area_planta_total_m2) * TF_PARA_KN
    tensao_pbes_kpa = (carga_total_pbes_tf / area_planta_total_m2) * TF_PARA_KN
    pct_din = (w_din / carga_total_pbes_tf) * 100.0 if carga_total_pbes_tf > 0 else 0.0

    return ResultadoCargasTanque(
        nome=nome,
        peso_concreto_armado_tf=round(w_conc, 1),
        peso_lastro_enchimento_tf=round(w_lastro, 1),
        peso_vazio_total_tf=round(w_vazio, 1),
        volume_liquido_m3=round(v_liq, 1),
        peso_agua_tf=round(w_agua, 1),
        peso_microareia_lodo_tf=round(w_areia, 1),
        acrescimo_dinamico_agitadores_tf=round(w_din, 1),
        carga_estatica_cheio_sem_equip_tf=round(w_cheio_est, 1),
        carga_operando_com_dinamico_tf=round(w_oper, 1),
        carga_total_pbes_tf=round(carga_total_pbes_tf, 1),
        parcela_equip_passarelas_folga_tf=round(w_equip, 1),
        tensao_media_vazio_kpa=round(tensao_vazio_kpa, 1),
        tensao_media_pbes_kpa=round(tensao_pbes_kpa, 1),
        pct_dinamico_sobre_pbes=round(pct_din, 2),
    )
