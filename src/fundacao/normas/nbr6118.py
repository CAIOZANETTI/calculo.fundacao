"""Parâmetros de concreto, aço, durabilidade e nós de bielas/tirantes (ABNT NBR 6118:2023)."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple

GRAVIDADE_M_S2 = 9.80665
TF_PARA_KN = 9.80665
KN_PARA_TF = 1.0 / TF_PARA_KN

# Bitolas comerciais usuais de aço CA-50 / CA-60 no Brasil (mm)
BITOLAS_COMERCIAIS_MM: Tuple[float, ...] = (5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0)

# Massa específica do aço carbono (kg/m³)
MASSA_ESPECIFICA_ACO_KG_M3 = 7850.0


class ClasseAgressividade(str, Enum):
    """Classes de Agressividade Ambiental (CAA) segundo NBR 6118 Tabela 6.1."""

    I = "I"
    II = "II"
    III = "III"
    IV = "IV"

    @property
    def fck_min_mpa(self) -> float:
        return {
            ClasseAgressividade.I: 20.0,
            ClasseAgressividade.II: 25.0,
            ClasseAgressividade.III: 30.0,
            ClasseAgressividade.IV: 40.0,
        }[self]

    @property
    def ac_max(self) -> float:
        return {
            ClasseAgressividade.I: 0.65,
            ClasseAgressividade.II: 0.60,
            ClasseAgressividade.III: 0.55,
            ClasseAgressividade.IV: 0.45,
        }[self]

    @property
    def cobrimento_nominal_pilar_viga_mm(self) -> float:
        """Cobrimento nominal mínimo para vigas/pilares/blocos (Tabela 7.2 NBR 6118)."""
        return {
            ClasseAgressividade.I: 25.0,
            ClasseAgressividade.II: 30.0,
            ClasseAgressividade.III: 40.0,
            ClasseAgressividade.IV: 50.0,  # Pode ser reduzido em 5 mm com controle rigoroso (45 mm no PBES)
        }[self]

    @property
    def cobrimento_nominal_controle_rigoroso_mm(self) -> float:
        """Cobrimento nominal com redução de 5 mm prevista na NBR 6118 item 7.4.7.4."""
        return self.cobrimento_nominal_pilar_viga_mm - 5.0


@dataclass(frozen=True)
class Concreto:
    """Propriedades mecânicas do concreto estrutural segundo NBR 6118:2023."""

    fck_mpa: float = 40.0
    gamma_c: float = 1.4
    alpha_e: float = 1.0  # 1.2 basalto/diabásio, 1.0 granito/gnaisse, 0.9 calcário, 0.7 arenito
    caa: ClasseAgressividade = ClasseAgressividade.IV

    @property
    def fcd_mpa(self) -> float:
        """Resistência de cálculo à compressão (MPa)."""
        return self.fck_mpa / self.gamma_c

    @property
    def fctm_mpa(self) -> float:
        """Resistência média à tração direta (MPa), NBR 6118 item 8.2.5."""
        if self.fck_mpa <= 50.0:
            return 0.3 * (self.fck_mpa ** (2.0 / 3.0))
        return 2.12 * math.log(1.0 + 0.11 * self.fck_mpa)

    @property
    def fctk_inf_mpa(self) -> float:
        return 0.7 * self.fctm_mpa

    @property
    def fctd_mpa(self) -> float:
        return self.fctk_inf_mpa / self.gamma_c

    @property
    def eci_mpa(self) -> float:
        """Módulo de elasticidade inicial (MPa), NBR 6118 item 8.2.8."""
        if self.fck_mpa <= 50.0:
            return self.alpha_e * 5600.0 * math.sqrt(self.fck_mpa)
        return 21500.0 * self.alpha_e * ((self.fck_mpa / 10.0 + 1.25) ** (1.0 / 3.0))

    @property
    def ecs_mpa(self) -> float:
        """Módulo de elasticidade secante (MPa)."""
        alpha_i = min(0.8 + 0.2 * self.fck_mpa / 80.0, 1.0)
        return alpha_i * self.eci_mpa

    @property
    def alpha_v2(self) -> float:
        """Parâmetro de redução da resistência do concreto fissurado (NBR 6118 item 22.3.3)."""
        return 1.0 - self.fck_mpa / 250.0

    @property
    def fcd1_mpa(self) -> float:
        """Tensão resistente em nó CCC (somente compressão, sob pilar/parede), NBR 6118:2023."""
        return 0.85 * self.alpha_v2 * self.fcd_mpa

    @property
    def fcd2_mpa(self) -> float:
        """Tensão resistente em nó CCT (com 1 tirante ancorado, sobre estaca), NBR 6118:2023."""
        return 0.60 * self.alpha_v2 * self.fcd_mpa

    @property
    def fcd3_mpa(self) -> float:
        """Tensão resistente em nó CTT (com 2+ tirantes ancorados), NBR 6118:2023."""
        return 0.72 * self.alpha_v2 * self.fcd_mpa

    def comprimento_ancoragem_basico_cm(
        self,
        bitola_mm: float,
        aco: "Aco",
        boa_aderencia: bool = True,
    ) -> float:
        """Comprimento de ancoragem básico lb (cm) segundo NBR 6118 item 9.4.2.4."""
        eta1 = 2.25 if aco.nervurado else 1.0
        eta2 = 1.0 if boa_aderencia else 0.7
        eta3 = 1.0 if bitola_mm <= 32.0 else (132.0 - bitola_mm) / 100.0
        fbd_mpa = eta1 * eta2 * eta3 * self.fctd_mpa
        phi_cm = bitola_mm / 10.0
        lb_cm = (phi_cm / 4.0) * (aco.fyd_mpa / fbd_mpa)
        return max(lb_cm, 25.0 * phi_cm)


@dataclass(frozen=True)
class Aco:
    """Propriedades mecânicas do aço para armadura passiva (NBR 6118)."""

    nome: str
    fyk_mpa: float
    gamma_s: float = 1.15
    es_mpa: float = 210_000.0
    nervurado: bool = True

    @property
    def fyd_mpa(self) -> float:
        return self.fyk_mpa / self.gamma_s


ACO_CA50 = Aco(nome="CA-50", fyk_mpa=500.0, nervurado=True)
ACO_CA60 = Aco(nome="CA-60", fyk_mpa=600.0, nervurado=False)


def area_barra_cm2(bitola_mm: float) -> float:
    """Área da seção transversal de uma barra de aço (cm²)."""
    phi_cm = bitola_mm / 10.0
    return math.pi * (phi_cm ** 2) / 4.0


def massa_linear_kg_m(bitola_mm: float) -> float:
    """Massa linear teórica de uma barra de aço (kg/m)."""
    area_m2 = area_barra_cm2(bitola_mm) * 1e-4
    return area_m2 * MASSA_ESPECIFICA_ACO_KG_M3


def selecionar_armadura(
    as_req_cm2: float,
    bitolas_mm: Tuple[float, ...] = (10.0, 12.5, 16.0, 20.0, 25.0),
    n_min: int = 2,
) -> List[Dict[str, float]]:
    """Retorna opções de arranjo (quantidade e bitola) que atendem As_req (cm²)."""
    opcoes: List[Dict[str, float]] = []
    for bitola in bitolas_mm:
        area_u = area_barra_cm2(bitola)
        n = max(n_min, math.ceil(as_req_cm2 / area_u))
        as_ef = n * area_u
        opcoes.append(
            {
                "bitola_mm": bitola,
                "quantidade": n,
                "as_efetiva_cm2": round(as_ef, 2),
                "folga_pct": round((as_ef / as_req_cm2 - 1.0) * 100.0, 1) if as_req_cm2 > 0 else 0.0,
                "massa_linear_total_kg_m": round(n * massa_linear_kg_m(bitola), 2),
            }
        )
    return opcoes
