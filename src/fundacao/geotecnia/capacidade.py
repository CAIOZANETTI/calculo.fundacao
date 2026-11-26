"""Envelope geotécnico consolidado (Aoki-Velloso, Décourt-Quaresma e Antunes-Cabral)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from fundacao.geotecnia.alonso import calcular_alonso
from fundacao.geotecnia.antunes_cabral import calcular_antunes_cabral
from fundacao.geotecnia.aoki_velloso import calcular_aoki_velloso
from fundacao.geotecnia.decourt_quaresma import calcular_decourt_quaresma
from fundacao.geotecnia.sondagem import Sondagem
from fundacao.geotecnia.teixeira import calcular_teixeira


@dataclass(frozen=True)
class ResultadoMetodoGeotecnico:
    metodo: str
    rp_kn: float
    rl_kn: float
    r_ult_kn: float
    p_adm_kn: float
    p_adm_tf: float
    rl_tracao_adm_tf: float


@dataclass(frozen=True)
class ResumoCapacidadeGeotecnica:
    sondagem_codigo: str
    diametro_m: float
    comprimento_m: float
    cota_arrasamento_m: float
    cota_ponta_m: float
    resultados: List[ResultadoMetodoGeotecnico]
    p_adm_min_tf: float
    p_adm_media_tf: float
    rl_tracao_min_tf: float
    hipotetico: bool


def calcular_capacidade_todos_metodos(
    sondagem: Sondagem,
    diametro_m: float,
    comprimento_m: float,
    cota_arrasamento_m: float | None = None,
    fs: float = 2.0,
    incluir_todos_5: bool = False,
) -> ResumoCapacidadeGeotecnica:
    """Executa os 3 métodos clássicos (ou todos os 5 métodos brasileiros) e retorna o envelope."""
    cota_arr = sondagem.cota_boca_m if cota_arrasamento_m is None else cota_arrasamento_m
    raw_results = [
        calcular_aoki_velloso(sondagem, diametro_m, comprimento_m, cota_arr, fs=fs),
        calcular_decourt_quaresma(sondagem, diametro_m, comprimento_m, cota_arr, fs=fs),
        calcular_antunes_cabral(sondagem, diametro_m, comprimento_m, cota_arr, fs=fs),
    ]
    if incluir_todos_5:
        raw_results.extend(
            [
                calcular_teixeira(sondagem, diametro_m, comprimento_m, cota_arr, fs=fs),
                calcular_alonso(sondagem, diametro_m, comprimento_m, cota_arr, fs=fs),
            ]
        )
    resultados = [
        ResultadoMetodoGeotecnico(
            metodo=str(r["metodo"]),
            rp_kn=float(r["rp_kn"]),
            rl_kn=float(r["rl_kn"]),
            r_ult_kn=float(r["r_ult_kn"]),
            p_adm_kn=float(r["p_adm_kn"]),
            p_adm_tf=float(r["p_adm_tf"]),
            rl_tracao_adm_tf=float(r["rl_tracao_adm_tf"]),
        )
        for r in raw_results
    ]
    p_min = min(r.p_adm_tf for r in resultados)
    p_med = sum(r.p_adm_tf for r in resultados) / len(resultados)
    t_min = min(r.rl_tracao_adm_tf for r in resultados)

    return ResumoCapacidadeGeotecnica(
        sondagem_codigo=sondagem.codigo,
        diametro_m=diametro_m,
        comprimento_m=comprimento_m,
        cota_arrasamento_m=round(cota_arr, 3),
        cota_ponta_m=round(cota_arr - comprimento_m, 3),
        resultados=resultados,
        p_adm_min_tf=round(p_min, 2),
        p_adm_media_tf=round(p_med, 2),
        rl_tracao_min_tf=round(t_min, 2),
        hipotetico=sondagem.hipotetico,
    )


def curva_capacidade_por_comprimento(
    sondagem: Sondagem,
    diametro_m: float,
    cota_arrasamento_m: float,
    comprimentos_m: List[float],
    fs: float = 2.0,
) -> List[ResumoCapacidadeGeotecnica]:
    """Gera a curva P_adm(L) para uma lista de comprimentos válidos dentro da sondagem."""
    prof_ini = max(0.0, sondagem.profundidade_por_cota(cota_arrasamento_m))
    curva: List[ResumoCapacidadeGeotecnica] = []
    for comp in comprimentos_m:
        if prof_ini + comp <= sondagem.profundidade_max_m + 1e-6:
            curva.append(
                calcular_capacidade_todos_metodos(
                    sondagem=sondagem,
                    diametro_m=diametro_m,
                    comprimento_m=comp,
                    cota_arrasamento_m=cota_arrasamento_m,
                    fs=fs,
                )
            )
    return curva


def dimensionar_comprimento_estaca(
    sondagem: Sondagem,
    diametro_m: float,
    cota_arrasamento_m: float,
    carga_alvo_tf: float,
    criterio: str = "media",
    l_min_m: float = 6.0,
    passo_m: float = 1.0,
    fs: float = 2.0,
) -> Optional[ResumoCapacidadeGeotecnica]:
    """Encontra o menor comprimento L >= l_min_m cuja P_adm atinge carga_alvo_tf."""
    prof_ini = max(0.0, sondagem.profundidade_por_cota(cota_arrasamento_m))
    l_max = sondagem.profundidade_max_m - prof_ini
    comp = l_min_m
    while comp <= l_max + 1e-6:
        res = calcular_capacidade_todos_metodos(
            sondagem=sondagem,
            diametro_m=diametro_m,
            comprimento_m=comp,
            cota_arrasamento_m=cota_arrasamento_m,
            fs=fs,
        )
        valor = res.p_adm_min_tf if criterio == "minimo" else res.p_adm_media_tf
        if valor >= carga_alvo_tf:
            return res
        comp += passo_m
    return None


@dataclass(frozen=True)
class ComparativoFSPCE:
    """Impacto normativo da realização de Prova de Carga Estática prévia (NBR 6122:2022 item 6.2.1.2.2)."""

    sondagem_codigo: str
    diametro_cm: float
    comprimento_m: float
    carga_solicitante_tf: float
    rl_medio_5_metodos_tf: float
    r_ult_medio_5_metodos_tf: float
    p_adm_fs_20_sem_pce_tf: float
    p_adm_fs_16_com_pce_tf: float
    ganho_capacidade_pct: float
    atende_em_solo_fs_20: bool
    atende_em_solo_fs_16: bool
    qp_rocha_req_fs_20_mpa: float
    qp_rocha_req_fs_16_mpa: float


def comparar_fs_com_e_sem_pce(
    sondagem: Sondagem,
    diametro_cm: float,
    comprimento_m: float,
    cota_arrasamento_m: float,
    carga_solicitante_tf: float,
    fs_sem_pce: float = 2.0,
    fs_com_pce: float = 1.6,
) -> ComparativoFSPCE:
    """Compara a capacidade admissível em solo pelos 5 métodos SPT com FS=2,0 (sem PCE) vs. FS=1,6 (com PCE).

    Fundamentação normativa: ABNT NBR 6122:2022, Tabela 1 e item 6.2.1.2.2:
      - Sem PCE prévia: FS global = 2,0 (maior incerteza de correlação SPT → resistência real);
      - Com PCE prévia executada até 2× carga de trabalho ou ruptura: FS global = 1,6 (+25% em P_adm).
    """
    from fundacao.geotecnia.fundacao_direta import tensao_ponta_rocha_necessaria_mpa
    from fundacao.normas.nbr6118 import KN_PARA_TF

    res20 = calcular_capacidade_todos_metodos(
        sondagem=sondagem,
        diametro_m=diametro_cm / 100.0,
        comprimento_m=comprimento_m,
        cota_arrasamento_m=cota_arrasamento_m,
        fs=fs_sem_pce,
        incluir_todos_5=True,
    )
    rl_med = sum(r.rl_kn * KN_PARA_TF for r in res20.resultados) / len(res20.resultados)
    r_ult_med = sum(r.r_ult_kn * KN_PARA_TF for r in res20.resultados) / len(res20.resultados)
    p_adm_20 = r_ult_med / fs_sem_pce
    p_adm_16 = r_ult_med / fs_com_pce
    ganho_pct = ((p_adm_16 / p_adm_20) - 1.0) * 100.0 if p_adm_20 > 0 else 0.0

    qp_20 = tensao_ponta_rocha_necessaria_mpa(carga_solicitante_tf, rl_med, diametro_cm, fs=fs_sem_pce)
    qp_16 = tensao_ponta_rocha_necessaria_mpa(carga_solicitante_tf, rl_med, diametro_cm, fs=fs_com_pce)

    return ComparativoFSPCE(
        sondagem_codigo=sondagem.codigo,
        diametro_cm=diametro_cm,
        comprimento_m=comprimento_m,
        carga_solicitante_tf=carga_solicitante_tf,
        rl_medio_5_metodos_tf=round(rl_med, 1),
        r_ult_medio_5_metodos_tf=round(r_ult_med, 1),
        p_adm_fs_20_sem_pce_tf=round(p_adm_20, 1),
        p_adm_fs_16_com_pce_tf=round(p_adm_16, 1),
        ganho_capacidade_pct=round(ganho_pct, 1),
        atende_em_solo_fs_20=p_adm_20 >= carga_solicitante_tf,
        atende_em_solo_fs_16=p_adm_16 >= carga_solicitante_tf,
        qp_rocha_req_fs_20_mpa=qp_20,
        qp_rocha_req_fs_16_mpa=qp_16,
    )

