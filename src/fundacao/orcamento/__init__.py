"""Módulo determinístico de quantificação e comparativo técnico-econômico de soluções de fundação."""

from fundacao.orcamento.comparativo_solucoes import (
    CenarioEconomico,
    comparar_solucoes_actiflo,
    gerar_relatorio_comparativo_markdown,
)

__all__ = [
    "CenarioEconomico",
    "comparar_solucoes_actiflo",
    "gerar_relatorio_comparativo_markdown",
]
