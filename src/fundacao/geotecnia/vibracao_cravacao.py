"""Avaliação de vibração por cravação de estacas (Wiss 1981 / Woods & Jedele 1985 / DIN 4150-3 / NBR 9653)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoVibracaoCravacao:
    estrutura_vizinha: str
    distancia_m: float
    energia_martelo_kj: float
    classe_solo: str
    ppv_estimado_mm_s: float
    limite_din4150_hidraulica_mm_s: float
    limite_nbr9653_baixa_freq_mm_s: float
    distancia_segura_din_5mms_m: float
    distancia_segura_nbr_15mms_m: float
    risco_fissuracao: str
    aprovado_sem_restricao: bool


# Constantes empíricas de Woods & Jedele (1985) / FHWA GEC-12 para PPV = k * (d / sqrt(E_J))^(-n)
# Solo Classe II (argila siltosa mole a média / silte — típico ETA Vila C): n = 1.5, k ≈ 0.35–0.75 (em m, J -> mm/s)
# Equivalente à formulação de Wiss (1981) com D_s = d / sqrt(E_J) em m/J^0.5:
#   PPV (mm/s) = k_mm * (d / sqrt(E_J))^(-n)
# Para E = 45.000 J (martelo queda livre/hidráulico 4,5 tf·m) e d = 5 m:
#   D_s = 5 / 212.13 = 0.02357 -> (0.02357)^(-1.5) = 276.4 -> com k_mm = 0.085 -> PPV = 23.5 mm/s (compatível com FHWA/Caltrans!)
CLASSES_SOLO_WOODS = {
    "classe_I_mole": (0.065, 1.5),       # Solo muito mole (NSPT < 5): maior amortecimento geométrico
    "classe_II_argila_silte": (0.095, 1.5),  # Argila siltosa/silte (NSPT 5–15 — ETA Vila C)
    "classe_III_rijo": (0.140, 1.5),     # Solo rijo / areia compacta (NSPT 15–50)
    "classe_IV_rocha": (0.220, 1.5),     # Rocha / nega no basalto (transmissão elevada!)
}


def avaliar_vibracao_cravacao(
    estrutura_vizinha: str,
    distancia_m: float,
    energia_martelo_kj: float = 45.0,
    classe_solo: str = "classe_II_argila_silte",
    limite_din_mm_s: float = 5.0,
    limite_nbr9653_mm_s: float = 15.0,
) -> ResultadoVibracaoCravacao:
    """Calcula a Velocidade de Partícula de Pico (PPV, mm/s) na cravação de estacas.

    Fórmula de atenuação (Wiss 1981 / Woods & Jedele 1985 / FHWA):
      PPV = k · (d / √E)^(-n)    [mm/s], com E em Joules e d em metros.

    Referências de limite de dano:
      - DIN 4150-3 (estruturas sensíveis / tanques estanques existentes): 3 a 5 mm/s (contínuo)
      - ABNT NBR 9653 (baixas frequências 4–15 Hz): 15 mm/s
    """
    if distancia_m <= 0:
        raise ValueError("Distância deve ser positiva.")
    if classe_solo not in CLASSES_SOLO_WOODS:
        raise ValueError(f"Classe de solo inválida: {classe_solo}")

    k_mm, n = CLASSES_SOLO_WOODS[classe_solo]
    e_joules = energia_martelo_kj * 1000.0
    sqrt_e = e_joules ** 0.5
    ds = distancia_m / sqrt_e
    ppv = k_mm * (ds ** (-n))

    d_seg_din = sqrt_e * ((limite_din_mm_s / k_mm) ** (-1.0 / n))
    d_seg_nbr = sqrt_e * ((limite_nbr9653_mm_s / k_mm) ** (-1.0 / n))

    if ppv > limite_nbr9653_mm_s:
        risco = "ALTO — Excede DIN 4150-3 e NBR 9653 (alto risco de fissuração em tanques existentes)"
    elif ppv > limite_din_mm_s:
        risco = "MODERADO/ALTO — Excede DIN 4150-3 para estruturas hidráulicas estanques"
    else:
        risco = "BAIXO — Abaixo dos limites DIN 4150-3 e NBR 9653"

    return ResultadoVibracaoCravacao(
        estrutura_vizinha=estrutura_vizinha,
        distancia_m=round(distancia_m, 2),
        energia_martelo_kj=energia_martelo_kj,
        classe_solo=classe_solo,
        ppv_estimado_mm_s=round(ppv, 1),
        limite_din4150_hidraulica_mm_s=limite_din_mm_s,
        limite_nbr9653_baixa_freq_mm_s=limite_nbr9653_mm_s,
        distancia_segura_din_5mms_m=round(d_seg_din, 1),
        distancia_segura_nbr_15mms_m=round(d_seg_nbr, 1),
        risco_fissuracao=risco,
        aprovado_sem_restricao=ppv <= limite_din_mm_s,
    )
