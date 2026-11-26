"""Modelo de dados para perfis de sondagem SPT com suporte a cotas de arrasamento."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple

import yaml


class TipoSolo(str, Enum):
    """Classificação de solos brasileiros compatível com Aoki-Velloso, Décourt-Quaresma e Antunes-Cabral."""

    AREIA = "areia"
    AREIA_SILTOSA = "areia_siltosa"
    AREIA_SILTO_ARGILOSA = "areia_silto_argilosa"
    AREIA_ARGILOSA = "areia_argilosa"
    AREIA_ARGILO_SILTOSA = "areia_argilo_siltosa"
    SILTE = "silte"
    SILTE_ARENOSO = "silte_arenoso"
    SILTE_ARENO_ARGILOSO = "silte_areno_argiloso"
    SILTE_ARGILOSO = "silte_argiloso"
    SILTE_ARGILO_ARENOSO = "silte_argilo_arenoso"
    ARGILA = "argila"
    ARGILA_ARENOSA = "argila_arenosa"
    ARGILA_ARENO_SILTOSA = "argila_areno_siltosa"
    ARGILA_SILTOSA = "argila_siltosa"
    ARGILA_SILTO_ARENOSA = "argila_silto_arenosa"

    @property
    def grupo_generico(self) -> str:
        """Agrupamento simplificado: 'areia', 'silte' ou 'argila'."""
        if self.value.startswith("areia"):
            return "areia"
        if self.value.startswith("silte"):
            return "silte"
        return "argila"


@dataclass(frozen=True)
class CamadaSPT:
    """Trecho de 1 m (ou espessura arbitrária) de ensaio SPT medido a partir da boca do furo."""

    profundidade_topo_m: float
    profundidade_base_m: float
    nspt: float
    tipo_solo: TipoSolo
    descricao: str = ""

    def __post_init__(self) -> None:
        if self.profundidade_base_m <= self.profundidade_topo_m:
            raise ValueError(
                f"Base ({self.profundidade_base_m}) deve ser maior que topo ({self.profundidade_topo_m})."
            )
        if self.nspt < 0:
            raise ValueError(f"NSPT não pode ser negativo: {self.nspt}")

    @property
    def espessura_m(self) -> float:
        return self.profundidade_base_m - self.profundidade_topo_m


@dataclass(frozen=True)
class Sondagem:
    """Perfil geotécnico de um furo de sondagem SPT."""

    codigo: str
    cota_boca_m: float
    camadas: Tuple[CamadaSPT, ...]
    nivel_agua_prof_m: Optional[float] = None
    hipotetico: bool = False
    observacoes: str = ""

    @property
    def profundidade_max_m(self) -> float:
        return max(c.profundidade_base_m for c in self.camadas)

    @property
    def cota_nivel_agua_m(self) -> Optional[float]:
        if self.nivel_agua_prof_m is None:
            return None
        return self.cota_boca_m - self.nivel_agua_prof_m

    def profundidade_por_cota(self, cota_m: float) -> float:
        """Converte cota absoluta (m) em profundidade relativa à boca da sondagem (m)."""
        return self.cota_boca_m - cota_m

    def camadas_no_trecho(
        self,
        prof_inicio_m: float,
        prof_fim_m: float,
    ) -> List[CamadaSPT]:
        """Recorta as camadas do perfil no intervalo [prof_inicio_m, prof_fim_m] relativo à boca."""
        if prof_fim_m <= prof_inicio_m:
            raise ValueError("prof_fim_m deve ser maior que prof_inicio_m.")
        if prof_fim_m > self.profundidade_max_m + 1e-6:
            raise ValueError(
                f"Profundidade solicitada ({prof_fim_m:.2f} m) excede o limite da sondagem "
                f"{self.codigo} ({self.profundidade_max_m:.2f} m)."
            )

        recorte: List[CamadaSPT] = []
        for camada in self.camadas:
            topo = max(camada.profundidade_topo_m, prof_inicio_m)
            base = min(camada.profundidade_base_m, prof_fim_m)
            if base > topo + 1e-9:
                recorte.append(
                    CamadaSPT(
                        profundidade_topo_m=topo,
                        profundidade_base_m=base,
                        nspt=camada.nspt,
                        tipo_solo=camada.tipo_solo,
                        descricao=camada.descricao,
                    )
                )
        return recorte

    def nspt_na_profundidade(self, prof_m: float) -> Tuple[float, TipoSolo]:
        """Retorna (NSPT, TipoSolo) exatamente na profundidade prof_m (m)."""
        for camada in self.camadas:
            if camada.profundidade_topo_m - 1e-9 <= prof_m <= camada.profundidade_base_m + 1e-9:
                return camada.nspt, camada.tipo_solo
        raise ValueError(
            f"Profundidade {prof_m:.2f} m fora do domínio da sondagem {self.codigo} "
            f"(0 a {self.profundidade_max_m:.2f} m)."
        )


def carregar_sondagem_yaml(caminho: str | Path) -> Sondagem:
    """Carrega um perfil de sondagem SPT a partir de arquivo YAML."""
    path = Path(caminho)
    with path.open("r", encoding="utf-8") as fh:
        dados = yaml.safe_load(fh)

    camadas: List[CamadaSPT] = []
    for item in dados["camadas"]:
        camadas.append(
            CamadaSPT(
                profundidade_topo_m=float(item["topo_m"]),
                profundidade_base_m=float(item["base_m"]),
                nspt=float(item["nspt"]),
                tipo_solo=TipoSolo(item["tipo_solo"]),
                descricao=str(item.get("descricao", "")),
            )
        )

    return Sondagem(
        codigo=str(dados["codigo"]),
        cota_boca_m=float(dados["cota_boca_m"]),
        camadas=tuple(camadas),
        nivel_agua_prof_m=(
            float(dados["nivel_agua_prof_m"]) if dados.get("nivel_agua_prof_m") is not None else None
        ),
        hipotetico=bool(dados.get("hipotetico", False)),
        observacoes=str(dados.get("observacoes", "")),
    )
