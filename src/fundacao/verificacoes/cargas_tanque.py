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


@dataclass(frozen=True)
class ResultadoEnchimentoParcial:
    """Verificação de enchimento assimétrico/parcial (câmaras cheias ao lado de câmaras vazias)."""

    nome: str
    fracao_cheia: float
    carga_total_parcial_tf: float
    momento_assimetrico_tfm: float
    excentricidade_m: float
    n_estacas: int
    n_linhas_eixo_momento: int
    comprimento_eixo_m: float
    carga_media_estaca_tf: float
    carga_max_estaca_lado_cheio_tf: float
    carga_min_estaca_lado_vazio_tf: float
    ha_tracao_lado_vazio: bool
    recalque_lado_cheio_mm: float
    recalque_lado_vazio_mm: float
    recalque_diferencial_mm: float
    distorcao_angular: float
    inverso_distorcao_angular: int
    atende_limite_tanque_estanque_1_1000: bool
    atende_limite_nbr6122_1_500: bool
    recalque_diferencial_fundacao_direta_mm: float


def verificar_enchimento_parcial_camaras(
    nome: str,
    peso_vazio_com_equip_tf: float,
    peso_agua_e_areia_total_tf: float,
    comprimento_eixo_m: float,
    n_estacas: int,
    n_linhas_no_eixo: int,
    rigidez_combinada_kpr_kn_m: float,
    fracao_cheia: float = 0.50,
    recalque_direto_cheio_mm: float = 105.0,
) -> ResultadoEnchimentoParcial:
    """Calcula esforços e recalque diferencial quando apenas parte das câmaras está cheia em manutenção.

    Modelo físico (Velloso & Lopes / Cintra, Aoki & Albiero — Grupo de Estacas sob Flexão Composta):
      - Metade (ou fração f) do tanque cheia de líquido e a parcela adjacente (1 - f) vazia:
          W_liq,parc = f · W_liq,tot
          Braço da resultante líquida em relação ao centro geométrico do tanque: e_liq = (1 - f) · L / 2
          M_ass = W_liq,parc · e_liq  (máximo para f = 0,50 -> M_ass = 0,5 · W_liq · L / 4 = W_liq · L / 8)
      - Distribuição elástica nas linhas de estacas igualmente espaçadas ao longo de L_ef ≈ 0,88·L:
          N_max = N_parc / n + M_ass · x_max / Σ(x_i²)
          N_min = N_parc / n - M_ass · x_max / Σ(x_i²)
      - Rigidez axial efetiva por estaca no conjunto (PDR): k_est = K_pr / n
          Δs = (N_max - N_min) / k_est
          Distorção angular = Δs / L_eixos (limite ACI 350 / tanques estanques ≤ 1/1000; NBR 6122 ≤ 1/500)
    """
    w_liq_parc = fracao_cheia * peso_agua_e_areia_total_tf
    n_parc = peso_vazio_com_equip_tf + w_liq_parc
    braco_m = (1.0 - fracao_cheia) * (comprimento_eixo_m / 2.0)
    m_ass_tfm = w_liq_parc * braco_m
    exc_m = m_ass_tfm / n_parc if n_parc > 0 else 0.0

    # Posições simétricas das linhas de estacas (extremos a ±0,44·L do centro)
    l_eixos = 0.88 * comprimento_eixo_m
    estacas_por_linha = n_estacas / max(n_linhas_no_eixo, 2)
    if n_linhas_no_eixo <= 1:
        xs = [0.0]
    else:
        passo = l_eixos / (n_linhas_no_eixo - 1)
        xs = [-l_eixos / 2.0 + i * passo for i in range(n_linhas_no_eixo)]
    soma_x2 = sum(estacas_por_linha * (x ** 2) for x in xs)
    x_max = max(abs(x) for x in xs) if xs else 0.0

    n_med = n_parc / n_estacas
    delta_n = (m_ass_tfm * x_max / soma_x2) if soma_x2 > 0 else 0.0
    n_max = n_med + delta_n
    n_min = n_med - delta_n

    # Rigidez axial efetiva por estaca no grupo (kN/m -> tf/mm)
    k_est_kn_m = rigidez_combinada_kpr_kn_m / max(n_estacas, 1)
    s_cheio_mm = (n_max * TF_PARA_KN / k_est_kn_m) * 1000.0
    s_vazio_mm = (n_min * TF_PARA_KN / k_est_kn_m) * 1000.0
    delta_s_mm = max(0.0, s_cheio_mm - s_vazio_mm)
    distorcao = (delta_s_mm / 1000.0) / l_eixos if l_eixos > 0 else 0.0
    inv_dist = int(round(1.0 / distorcao)) if distorcao > 1e-9 else 999_999

    # Estimativa comparativa se fosse fundação direta sem estacas (diferença de recalque ~45% do total cheio)
    delta_s_direta = 0.45 * recalque_direto_cheio_mm

    return ResultadoEnchimentoParcial(
        nome=nome,
        fracao_cheia=fracao_cheia,
        carga_total_parcial_tf=round(n_parc, 1),
        momento_assimetrico_tfm=round(m_ass_tfm, 1),
        excentricidade_m=round(exc_m, 2),
        n_estacas=n_estacas,
        n_linhas_eixo_momento=n_linhas_no_eixo,
        comprimento_eixo_m=round(l_eixos, 2),
        carga_media_estaca_tf=round(n_med, 1),
        carga_max_estaca_lado_cheio_tf=round(n_max, 1),
        carga_min_estaca_lado_vazio_tf=round(n_min, 1),
        ha_tracao_lado_vazio=n_min < 0.0,
        recalque_lado_cheio_mm=round(s_cheio_mm, 2),
        recalque_lado_vazio_mm=round(s_vazio_mm, 2),
        recalque_diferencial_mm=round(delta_s_mm, 2),
        distorcao_angular=round(distorcao, 6),
        inverso_distorcao_angular=inv_dist,
        atende_limite_tanque_estanque_1_1000=distorcao <= (1.0 / 1000.0),
        atende_limite_nbr6122_1_500=distorcao <= (1.0 / 500.0),
        recalque_diferencial_fundacao_direta_mm=round(delta_s_direta, 1),
    )


@dataclass(frozen=True)
class CasoCarregamento:
    codigo: str
    descricao: str
    tipo_estado_limite: str
    carga_vertical_total_tf: float
    tensao_media_base_kpa: float
    carga_estaca_ref_tf: float
    observacao_normativa: str


def gerar_envoltoria_acoes_tanque(
    cargas: ResultadoCargasTanque,
    area_planta_m2: float,
    n_estacas: int,
    parcial: ResultadoEnchimentoParcial,
    sobrecarga_acidental_passarelas_kpa: float = 2.5,
    empuxo_subpressao_real_tf: float = 0.0,
) -> list[CasoCarregamento]:
    """Monta a envoltória completa de ações (NBR 8681 / NBR 6118 / ACI 350) do tanque."""
    w_acid_tf = (sobrecarga_acidental_passarelas_kpa * area_planta_m2) / TF_PARA_KN
    w_equip = max(0.0, cargas.parcela_equip_passarelas_folga_tf)
    w_cheio_est = cargas.carga_estatica_cheio_sem_equip_tf + cargas.peso_microareia_lodo_tf + w_equip
    w_oper_tot = w_cheio_est + cargas.acrescimo_dinamico_agitadores_tf + w_acid_tf
    # Combinação ELU NBR 6118/8681: 1,4·G + 1,4·Q_agua + 1,4·0,7·(Q_din + Q_acid)
    w_elu = (
        1.4 * (cargas.peso_vazio_total_tf + w_equip)
        + 1.4 * (cargas.peso_agua_tf + cargas.peso_microareia_lodo_tf)
        + 1.4 * 0.7 * (cargas.acrescimo_dinamico_agitadores_tf + w_acid_tf)
    )
    w_flut_liq = cargas.peso_vazio_total_tf - empuxo_subpressao_real_tf

    def _kpa(tf: float) -> float:
        return round((tf / area_planta_m2) * TF_PARA_KN, 1)

    return [
        CasoCarregamento(
            codigo="C1",
            descricao="Peso Próprio (Tanque Vazio / Construção)",
            tipo_estado_limite="ELS / Permanente (G)",
            carga_vertical_total_tf=round(cargas.peso_vazio_total_tf, 1),
            tensao_media_base_kpa=_kpa(cargas.peso_vazio_total_tf),
            carga_estaca_ref_tf=round(cargas.peso_vazio_total_tf / n_estacas, 1),
            observacao_normativa="Concreto armado (25 kN/m³) + enchimentos; base para verificação de flutuação.",
        ),
        CasoCarregamento(
            codigo="C2",
            descricao="Estático Cheio (Água + Microareia + Equipamentos)",
            tipo_estado_limite="ELS Quase-Permanente",
            carga_vertical_total_tf=round(w_cheio_est, 1),
            tensao_media_base_kpa=_kpa(w_cheio_est),
            carga_estaca_ref_tf=round(w_cheio_est / n_estacas, 1),
            observacao_normativa="Referência PBES de operação plena sem vibração; rege recalques de longo prazo.",
        ),
        CasoCarregamento(
            codigo="C3",
            descricao="Operação Dinâmica (Cheio + Agitadores + Sobrecarga Acidental)",
            tipo_estado_limite="ELS Frequente / Combinação Característica",
            carga_vertical_total_tf=round(w_oper_tot, 1),
            tensao_media_base_kpa=_kpa(w_oper_tot),
            carga_estaca_ref_tf=round(w_oper_tot / n_estacas, 1),
            observacao_normativa="Inclui +3% hidrodinâmico (agitadores/sloshing) + 2,5 kPa acidental de passarelas.",
        ),
        CasoCarregamento(
            codigo="C4",
            descricao=f"Manutenção / Enchimento Parcial ({int(parcial.fracao_cheia * 100)}% Cheio × {int((1 - parcial.fracao_cheia) * 100)}% Vazio)",
            tipo_estado_limite="ELS Diferencial + Flexão Composta de Grupo",
            carga_vertical_total_tf=parcial.carga_total_parcial_tf,
            tensao_media_base_kpa=_kpa(parcial.carga_total_parcial_tf),
            carga_estaca_ref_tf=parcial.carga_max_estaca_lado_cheio_tf,
            observacao_normativa=(
                f"M_ass={parcial.momento_assimetrico_tfm:.0f} tf·m; N_est={parcial.carga_min_estaca_lado_vazio_tf:.1f} a "
                f"{parcial.carga_max_estaca_lado_cheio_tf:.1f} tf; Δs={parcial.recalque_diferencial_mm:.1f} mm (1/{parcial.inverso_distorcao_angular})."
            ),
        ),
        CasoCarregamento(
            codigo="C5",
            descricao="Flutuação / Subpressão (Tanque Vazio sob Lençol Freático)",
            tipo_estado_limite="ELU-EQU (NBR 8681 / NBR 6122)",
            carga_vertical_total_tf=round(w_flut_liq, 1),
            tensao_media_base_kpa=_kpa(w_flut_liq),
            carga_estaca_ref_tf=round(w_flut_liq / n_estacas, 1),
            observacao_normativa="N.A. real a ~6–7 m abaixo da laje (empuxo = 0); dreno de fundo recomendado contra água empoleirada.",
        ),
        CasoCarregamento(
            codigo="C6",
            descricao="Combinação Última Majorada (ELU — NBR 6118 / NBR 8681)",
            tipo_estado_limite="ELU Estrutural (γg=1,4; γq=1,4; ψ0=0,7)",
            carga_vertical_total_tf=round(w_elu, 1),
            tensao_media_base_kpa=_kpa(w_elu),
            carga_estaca_ref_tf=round(w_elu / n_estacas, 1),
            observacao_normativa="Rege dimensionamento estrutural da estaca, punção nos capitéis e flexão da laje.",
        ),
    ]

