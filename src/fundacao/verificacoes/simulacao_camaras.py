"""Simulação matricial vetorizada em NumPy (Monte Carlo + combinatória exata 2^K)
de enchimento multicâmaras com flexão composta oblíqua (N, Mx, My) em grupos de estacas.

Referências técnicas:
  - ACI 350-20 (Seção 9.2 / R9.2): verificação de todas as combinações plausíveis de
    câmaras cheias e vazias adjacentes em tanques estanques de saneamento.
  - ABNT NBR 8681:2003 & NBR 6122:2022: arranjo espacial mais desfavorável de ações variáveis.
  - Velloso & Lopes (Vol. 2) / Cintra, Aoki & Albiero: reação de estacas sob flexão composta oblíqua.
  - Phoon & Kulhawy (1999) / ISO 2394:2015: Simulação de Monte Carlo (Nível III) para envoltórias
    estocásticas e verificação de probabilidade de excedência.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass
from typing import List, Tuple

import numpy as np

from fundacao.normas.nbr6118 import TF_PARA_KN


@dataclass(frozen=True)
class CamaraHidraulica:
    codigo: str
    nome: str
    xc_m: float
    yc_m: float
    area_molhada_m2: float


@dataclass(frozen=True)
class ResultadoSimulacaoCamaras:
    unidade: str
    n_camaras: int
    n_estacas: int
    n_combinacoes_binarias: int
    n_monte_carlo: int
    n_cenarios_totais: int
    seed: int
    carga_media_cheio_tf: float
    carga_projeto_estaca_tf: float
    # Envoltória estatística das reações máximas na estaca crítica (tf)
    n_max_absoluto_tf: float
    n_max_p99_tf: float
    n_max_p95_tf: float
    n_max_p50_tf: float
    n_min_absoluto_tf: float
    ha_tracao_em_algum_cenario: bool
    pct_cenarios_acima_cheio_simetrico: float
    pct_cenarios_acima_carga_projeto: float
    # Pior cenário identificado (combinação exata de níveis)
    pior_cenario_origem: str
    pior_cenario_carga_total_tf: float
    pior_cenario_mx_tfm: float
    pior_cenario_my_tfm: float
    pior_cenario_niveis_m: List[float]
    pior_cenario_descricao: str
    # Recalques diferenciais 2D (ELS)
    delta_s_max_mm: float
    delta_s_p95_mm: float
    distorcao_angular_max: float
    inverso_distorcao_max: int
    atende_limite_estanque_1_1000: bool
    atende_limite_nbr6122_1_500: bool
    # Dados prontos para visualização gráfica (histograma, scatter e mapa 2D de estacas)
    hist_bins_tf: List[float]
    hist_counts: List[int]
    scatter_amostra: List[Tuple[float, float, float]]  # (N_total_tf, N_max_estaca_tf, frac_cheia)
    mapa_estacas_xy_pico: List[Tuple[float, float, float, float]]  # (x_m, y_m, N_max_tf, N_min_tf)


def gerar_malha_estacas_2d(
    b_m: float,
    l_m: float,
    n_linhas_y: int,
    n_colunas_x: int,
    n_estacas_alvo: int,
    fator_borda: float = 0.88,
) -> np.ndarray:
    """Gera matriz (n_estacas, 2) de coordenadas (x, y) centradas na origem da malha de estacas."""
    lx = fator_borda * l_m
    ly = fator_borda * b_m
    xs = np.linspace(-lx / 2.0, lx / 2.0, n_colunas_x)
    ys = np.linspace(-ly / 2.0, ly / 2.0, n_linhas_y)
    coords = [(float(x), float(y)) for y in ys for x in xs]

    # Se a grade retangular tiver excedente (ex.: 4x6=24 para 22 estacas), remove posições internas simétricas
    if len(coords) > n_estacas_alvo:
        excesso = len(coords) - n_estacas_alvo
        # Ordena por distância ao centro (remove as mais centrais mantendo perímetro intacto)
        coords_ordenados = sorted(coords, key=lambda pt: (pt[0] ** 2 + pt[1] ** 2))
        coords = coords_ordenados[excesso:]

    return np.array(coords, dtype=np.float64)


def gerar_camaras_padrao(
    b_m: float,
    l_m: float,
    area_molhada_total_m2: float,
    n_div_x: int,
    n_div_y: int,
    prefixos: List[str] | None = None,
) -> List[CamaraHidraulica]:
    """Divide o tanque em grade 2D (n_div_x × n_div_y) de câmaras hidráulicas independentes."""
    dx = l_m / n_div_x
    dy = b_m / n_div_y
    area_cam = area_molhada_total_m2 / (n_div_x * n_div_y)
    camaras: List[CamaraHidraulica] = []
    idx = 0
    for iy in range(n_div_y):
        yc = -b_m / 2.0 + (iy + 0.5) * dy
        for ix in range(n_div_x):
            xc = -l_m / 2.0 + (ix + 0.5) * dx
            idx += 1
            cod = f"C{idx}"
            nome = prefixos[idx - 1] if (prefixos and idx - 1 < len(prefixos)) else f"Câmara {idx}"
            camaras.append(
                CamaraHidraulica(
                    codigo=cod,
                    nome=nome,
                    xc_m=round(xc, 2),
                    yc_m=round(yc, 2),
                    area_molhada_m2=round(area_cam, 2),
                )
            )
    return camaras


def simular_enchimento_multicamaras_mc(
    unidade: str,
    b_m: float,
    l_m: float,
    area_planta_m2: float,
    peso_vazio_com_equip_tf: float,
    camaras: List[CamaraHidraulica],
    coords_estacas_xy: np.ndarray,
    rigidez_combinada_kpr_kn_m: float,
    carga_projeto_estaca_tf: float,
    lamina_nominal_m: float = 5.0,
    lamina_max_extrema_m: float = 5.2,
    n_monte_carlo: int = 5_000,
    seed: int = 42,
) -> ResultadoSimulacaoCamaras:
    """Executa simulação matricial vetorizada em NumPy combinando:
      1) Todas as 2^K combinações binárias extremas (cada câmara 0 m ou lâmina nominal);
      2) N cenários estocásticos Monte Carlo com níveis contínuos independentes por câmara,
         variação de fator dinâmico dos agitadores (0–4%), microareia (0–12 kg/m³) e acidental (0–3 kPa).

    Equação matricial de Navier (flexão composta oblíqua no grupo de estacas):
        R[k, i] = N_tot[k] / n  +  Mx[k] * y_i / Σ(y²)  +  My[k] * x_i / Σ(x²)
    """
    rng = np.random.default_rng(seed)
    n_cam = len(camaras)
    n_est = coords_estacas_xy.shape[0]

    xc = np.array([c.xc_m for c in camaras], dtype=np.float64)
    yc = np.array([c.yc_m for c in camaras], dtype=np.float64)
    ac = np.array([c.area_molhada_m2 for c in camaras], dtype=np.float64)

    xp = coords_estacas_xy[:, 0]
    yp = coords_estacas_xy[:, 1]
    soma_x2 = float(np.sum(xp ** 2))
    soma_y2 = float(np.sum(yp ** 2))
    diag_eixos_m = math.hypot(float(np.ptp(xp)), float(np.ptp(yp)))

    # 1) Matriz exata 2^K de combinações binárias extremas (cheio nominal vs. vazio)
    bin_states = np.array(list(itertools.product([0.0, lamina_nominal_m], repeat=n_cam)), dtype=np.float64)
    n_bin = bin_states.shape[0]
    din_bin = np.full((n_bin, n_cam), 0.03, dtype=np.float64)
    areia_bin = np.full((n_bin, n_cam), 0.008, dtype=np.float64)  # 8 kg/m³ -> 0,008 tf/m³
    acid_bin = np.full(n_bin, (2.5 * area_planta_m2) / TF_PARA_KN, dtype=np.float64)

    # 2) Matriz Monte Carlo (N × K): mistura níveis contínuos e estados discretos de manutenção
    # 35% chance de câmara vazia (manutenção), 35% próxima de cheia, 30% nível intermediário aleatório
    u_mode = rng.random((n_monte_carlo, n_cam))
    h_mc = np.where(
        u_mode < 0.35,
        0.0,
        np.where(
            u_mode < 0.70,
            rng.uniform(0.85 * lamina_nominal_m, lamina_max_extrema_m, size=(n_monte_carlo, n_cam)),
            rng.uniform(0.0, lamina_max_extrema_m, size=(n_monte_carlo, n_cam)),
        ),
    )
    din_mc = rng.uniform(0.0, 0.04, size=(n_monte_carlo, n_cam))
    areia_mc = rng.uniform(0.0, 0.012, size=(n_monte_carlo, n_cam))
    acid_mc = (rng.uniform(0.0, 3.0, size=n_monte_carlo) * area_planta_m2) / TF_PARA_KN

    # Concatena binários exatos + Monte Carlo em uma única matriz (N_tot × K)
    H = np.vstack([bin_states, h_mc])
    DIN = np.vstack([din_bin, din_mc])
    AREIA = np.vstack([areia_bin, areia_mc])
    ACID = np.concatenate([acid_bin, acid_mc])
    n_tot = H.shape[0]

    # Agitador só atua em câmaras com lâmina > 0,5 m
    agit_ativo = (H > 0.5).astype(np.float64)
    # Peso líquido efetivo em cada câmara: W_c = H * A_c * (1,0 + areia + din * agit_ativo)  [tf]
    W_cam = H * ac[None, :] * (1.0 + AREIA + DIN * agit_ativo)

    # Esforços globais por cenário (vetores de tamanho N_tot)
    N_tot = peso_vazio_com_equip_tf + ACID + np.sum(W_cam, axis=1)
    # Momentos em relação ao centro geométrico (Mx gira em torno de X -> braço yc; My gira em torno de Y -> braço xc)
    Mx = W_cam @ yc  # tf·m
    My = W_cam @ xc  # tf·m

    # Matriz completa de reações em TODAS as estacas para TODOS os cenários: R (N_tot × n_est)
    R = (
        (N_tot[:, None] / n_est)
        + np.outer(Mx, yp / soma_y2)
        + np.outer(My, xp / soma_x2)
    )

    n_max_por_cenario = np.max(R, axis=1)
    n_min_por_cenario = np.min(R, axis=1)

    # Recalque por estaca via rigidez acoplada PDR (k_est = K_pr / n_est)
    k_est_kn_m = rigidez_combinada_kpr_kn_m / n_est
    S_mm = (R * TF_PARA_KN / k_est_kn_m) * 1000.0
    delta_s_por_cenario = np.max(S_mm, axis=1) - np.min(S_mm, axis=1)

    # Referência estática 100% cheia (sem assimetria)
    w_liq_cheio = float(np.sum(ac) * lamina_nominal_m * (1.0 + 0.008))
    carga_med_cheio = (peso_vazio_com_equip_tf + w_liq_cheio) / n_est

    # Estatísticas globais
    idx_pior = int(np.argmax(n_max_por_cenario))
    n_max_abs = float(n_max_por_cenario[idx_pior])
    n_min_abs = float(np.min(n_min_por_cenario))
    p99 = float(np.percentile(n_max_por_cenario, 99))
    p95 = float(np.percentile(n_max_por_cenario, 95))
    p50 = float(np.percentile(n_max_por_cenario, 50))
    pct_acima_cheio = float(np.mean(n_max_por_cenario > carga_med_cheio) * 100.0)
    pct_acima_proj = float(np.mean(n_max_por_cenario > carga_projeto_estaca_tf) * 100.0)

    delta_s_max = float(np.max(delta_s_por_cenario))
    delta_s_p95 = float(np.percentile(delta_s_por_cenario, 95))
    dist_max = (delta_s_max / 1000.0) / diag_eixos_m if diag_eixos_m > 0 else 0.0
    inv_dist_max = int(round(1.0 / dist_max)) if dist_max > 1e-9 else 999_999

    # Descrição legível do pior cenário
    origem_pior = "Combinatória Exata (2^K)" if idx_pior < n_bin else f"Monte Carlo (#{idx_pior - n_bin + 1})"
    niveis_pior = [round(float(v), 2) for v in H[idx_pior]]
    cheias_cod = [camaras[i].codigo for i, h in enumerate(niveis_pior) if h >= 3.0]
    vazias_cod = [camaras[i].codigo for i, h in enumerate(niveis_pior) if h < 1.0]
    desc_pior = (
        f"Cheias ({len(cheias_cod)}/{n_cam}): {', '.join(cheias_cod) or 'nenhuma'} | "
        f"Vazias: {', '.join(vazias_cod) or 'nenhuma'}"
    )

    # Histograma (16 faixas) para gráfico
    counts, edges = np.histogram(n_max_por_cenario, bins=16)
    bins_centros = [round(float((edges[i] + edges[i + 1]) / 2.0), 1) for i in range(len(counts))]

    # Amostra estratificada de 220 pontos para gráfico de dispersão (inclui o pior cenário!)
    frac_cheia_vec = np.mean(H / lamina_nominal_m, axis=1)
    idxs_sample = np.unique(np.concatenate([np.linspace(0, n_tot - 1, 219, dtype=int), np.array([idx_pior])]))
    scatter = [
        (round(float(N_tot[i]), 1), round(float(n_max_por_cenario[i]), 1), round(float(frac_cheia_vec[i]), 2))
        for i in idxs_sample
    ]

    # Mapa 2D de pico por estaca (para heatmap na planta)
    pico_est = np.max(R, axis=0)
    min_est = np.min(R, axis=0)
    mapa_est = [
        (round(float(xp[i]), 2), round(float(yp[i]), 2), round(float(pico_est[i]), 1), round(float(min_est[i]), 1))
        for i in range(n_est)
    ]

    return ResultadoSimulacaoCamaras(
        unidade=unidade,
        n_camaras=n_cam,
        n_estacas=n_est,
        n_combinacoes_binarias=n_bin,
        n_monte_carlo=n_monte_carlo,
        n_cenarios_totais=n_tot,
        seed=seed,
        carga_media_cheio_tf=round(carga_med_cheio, 1),
        carga_projeto_estaca_tf=carga_projeto_estaca_tf,
        n_max_absoluto_tf=round(n_max_abs, 1),
        n_max_p99_tf=round(p99, 1),
        n_max_p95_tf=round(p95, 1),
        n_max_p50_tf=round(p50, 1),
        n_min_absoluto_tf=round(n_min_abs, 1),
        ha_tracao_em_algum_cenario=n_min_abs < 0.0,
        pct_cenarios_acima_cheio_simetrico=round(pct_acima_cheio, 1),
        pct_cenarios_acima_carga_projeto=round(pct_acima_proj, 1),
        pior_cenario_origem=origem_pior,
        pior_cenario_carga_total_tf=round(float(N_tot[idx_pior]), 1),
        pior_cenario_mx_tfm=round(float(Mx[idx_pior]), 1),
        pior_cenario_my_tfm=round(float(My[idx_pior]), 1),
        pior_cenario_niveis_m=niveis_pior,
        pior_cenario_descricao=desc_pior,
        delta_s_max_mm=round(delta_s_max, 2),
        delta_s_p95_mm=round(delta_s_p95, 2),
        distorcao_angular_max=round(dist_max, 6),
        inverso_distorcao_max=inv_dist_max,
        atende_limite_estanque_1_1000=dist_max <= (1.0 / 1000.0),
        atende_limite_nbr6122_1_500=dist_max <= (1.0 / 500.0),
        hist_bins_tf=bins_centros,
        hist_counts=[int(c) for c in counts],
        scatter_amostra=scatter,
        mapa_estacas_xy_pico=mapa_est,
    )
