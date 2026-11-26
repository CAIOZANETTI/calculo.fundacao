"""Envelope geotécnico consolidado (Aoki-Velloso, Décourt-Quaresma e Antunes-Cabral)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from fundacao.geotecnia.antunes_cabral import calcular_antunes_cabral
from fundacao.geotecnia.aoki_velloso import calcular_aoki_velloso
from fundacao.geotecnia.decourt_quaresma import calcular_decourt_quaresma
from fundacao.geotecnia.sondagem import Sondagem


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
) -> ResumoCapacidadeGeotecnica:
    """Executa os três métodos semi-empíricos e retorna o envelope conservador e médio."""
    cota_arr = sondagem.cota_boca_m if cota_arrasamento_m is None else cota_arrasamento_m
    raw_results = [
        calcular_aoki_velloso(sondagem, diametro_m, comprimento_m, cota_arr, fs=fs),
        calcular_decourt_quaresma(sondagem, diametro_m, comprimento_m, cota_arr, fs=fs),
        calcular_antunes_cabral(sondagem, diametro_m, comprimento_m, cota_arr, fs=fs),
    ]
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
