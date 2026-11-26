"""Verificação de estabilidade global à subpressão / flutuação de tanques enterrados."""

from __future__ import annotations

from dataclasses import dataclass

from fundacao.normas.nbr6122 import FatoresSegurancaNBR6122


@dataclass(frozen=True)
class ResultadoSubpressao:
    area_planta_m2: float
    cota_fundo_laje_m: float
    cota_nivel_agua_m: float
    lamina_subpressao_m: float
    empuxo_subpressao_tf: float
    peso_proprio_estrutura_tf: float
    tracao_disponivel_estacas_tf: float
    fs_somente_peso: float
    fs_com_estacas: float
    fs_minimo: float
    necessita_estacas_tracao: bool
    tracao_por_estaca_tf: float
    aprovado: bool


def verificar_subpressao_tanque(
    area_planta_m2: float,
    volume_concreto_total_m3: float,
    cota_fundo_laje_m: float,
    cota_nivel_agua_m: float,
    n_estacas: int = 0,
    capacidade_tracao_estaca_tf: float = 0.0,
    peso_especifico_concreto_tf_m3: float = 2.5,
    peso_especifico_agua_tf_m3: float = 1.0,
    sobrecarga_aterro_tf: float = 0.0,
    fs_minimo: float = FatoresSegurancaNBR6122().fs_flutuacao_min,
) -> ResultadoSubpressao:
    """Verifica flutuação do tanque vazio sob nível d'água externo elevado.

    Fórmulas:
      h_sub  = max(0, NA - cota_fundo_laje)
      U      = γ_w · h_sub · A_planta
      W_estr = γ_c · V_concreto + W_aterro
      FS_peso = W_estr / U
      FS_tot  = (W_estr + n_estacas · T_adm) / U
    """
    lamina = max(0.0, cota_nivel_agua_m - cota_fundo_laje_m)
    empuxo_tf = peso_especifico_agua_tf_m3 * lamina * area_planta_m2
    peso_estr_tf = peso_especifico_concreto_tf_m3 * volume_concreto_total_m3 + sobrecarga_aterro_tf
    tracao_total_tf = n_estacas * capacidade_tracao_estaca_tf

    if empuxo_tf <= 1e-6:
        fs_peso = float("inf")
        fs_total = float("inf")
        necessita_tracao = False
        tracao_por_estaca = 0.0
        aprovado = True
    else:
        fs_peso = peso_estr_tf / empuxo_tf
        fs_total = (peso_estr_tf + tracao_total_tf) / empuxo_tf
        necessita_tracao = fs_peso < fs_minimo
        deficit_tf = max(0.0, fs_minimo * empuxo_tf - peso_estr_tf)
        tracao_por_estaca = (deficit_tf / n_estacas) if n_estacas > 0 else float("inf")
        aprovado = fs_total >= fs_minimo

    return ResultadoSubpressao(
        area_planta_m2=round(area_planta_m2, 2),
        cota_fundo_laje_m=round(cota_fundo_laje_m, 3),
        cota_nivel_agua_m=round(cota_nivel_agua_m, 3),
        lamina_subpressao_m=round(lamina, 3),
        empuxo_subpressao_tf=round(empuxo_tf, 2),
        peso_proprio_estrutura_tf=round(peso_estr_tf, 2),
        tracao_disponivel_estacas_tf=round(tracao_total_tf, 2),
        fs_somente_peso=round(fs_peso, 2) if fs_peso != float("inf") else float("inf"),
        fs_com_estacas=round(fs_total, 2) if fs_total != float("inf") else float("inf"),
        fs_minimo=fs_minimo,
        necessita_estacas_tracao=necessita_tracao,
        tracao_por_estaca_tf=round(tracao_por_estaca, 2) if tracao_por_estaca != float("inf") else float("inf"),
        aprovado=aprovado,
    )
