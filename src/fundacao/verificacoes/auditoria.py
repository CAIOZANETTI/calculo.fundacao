"""Carregamento e auditoria completa de projetos de fundação (ACTIFLO 360, 600 e genéricos)."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from fundacao.estrutural.bloco_1_estaca import (
    GeometriaBloco1Estaca,
    ResultadoBloco1Estaca,
    verificar_bloco_1_estaca,
)
from fundacao.estrutural.bloco_2_estacas import (
    GeometriaBloco2Estacas,
    ResultadoBloco2Estacas,
    verificar_bloco_2_estacas,
)
from fundacao.estrutural.estaca import ResultadoEstacaEstrutural, verificar_estaca_helice_continua
from fundacao.geotecnia.capacidade import ResumoCapacidadeGeotecnica, dimensionar_comprimento_estaca
from fundacao.geotecnia.sondagem import Sondagem
from fundacao.normas.nbr6118 import ClasseAgressividade, Concreto


@dataclass(frozen=True)
class PontoCarga:
    """Um ponto de carga (pilar ou ponto de carga sob parede/laje) da planta de locação."""

    id: str
    nk_tf: float
    n_estacas_pbes: int
    cota_topo_bloco_m: float
    cota_arrasamento_m: float
    tipo_elemento: str = "parede"
    orientacao_bloco_2e: str = ""
    observacao: str = ""

    @property
    def carga_por_estaca_pbes_tf(self) -> float:
        return self.nk_tf / self.n_estacas_pbes


@dataclass(frozen=True)
class ConfiguracaoProjeto:
    """Configuração estrutural e geométrica carregada de projetos/<nome>/config.yaml."""

    nome: str
    codigo_pbes: str
    empreendimento: str
    fck_mpa: float
    caa: ClasseAgressividade
    cobrimento_cm: float
    diametro_estaca_cm: float
    embutimento_cm: float
    p_adm_referencia_tf: float
    area_planta_aprox_m2: float
    volume_concreto_total_pbes_m3: float
    volume_blocos_pbes_m3: float
    area_forma_blocos_pbes_m2: float
    geometria_bloco_1e: GeometriaBloco1Estaca
    geometria_bloco_2e: GeometriaBloco2Estacas
    n_barras_tirante_2e: int = 12
    bitola_tirante_2e_mm: float = 16.0
    dobra_vertical_2e_cm: float = 60.0
    armada_compressao_estaca: bool = False


@dataclass(frozen=True)
class AuditoriaPonto:
    ponto: PontoCarga
    carga_por_estaca_pbes_tf: float
    n_estacas_necessario: int
    taxa_utilizacao_pbes: float
    status: str  # "OK", "ATENCAO", "EXCEDE"
    observacao_auditoria: str


@dataclass(frozen=True)
class ResultadoAuditoriaProjeto:
    config: ConfiguracaoProjeto
    p_adm_adotada_tf: float
    total_pontos: int
    carga_total_tf: float
    n_blocos_1e_pbes: int
    n_blocos_2e_pbes: int
    total_estacas_pbes: int
    total_estacas_otimizado: int
    max_carga_ponto_tf: float
    max_carga_por_estaca_pbes_tf: float
    ponto_mais_solicitado_1e: str
    ponto_mais_solicitado_2e: str
    pontos_excedentes: List[AuditoriaPonto]
    auditoria_pontos: List[AuditoriaPonto]
    verificacao_estaca_critica: ResultadoEstacaEstrutural
    verificacao_bloco_1e_critico: Optional[ResultadoBloco1Estaca]
    verificacao_bloco_2e_critico: Optional[ResultadoBloco2Estacas]
    verificacao_bloco_2e_capacidade_cheia: ResultadoBloco2Estacas
    dimensionamento_geotecnico_por_cota: Dict[float, Optional[ResumoCapacidadeGeotecnica]] = field(
        default_factory=dict
    )


def carregar_projeto(diretorio_projeto: str | Path) -> tuple[ConfiguracaoProjeto, List[PontoCarga]]:
    """Carrega config.yaml e pontos_carga.csv de uma pasta de projeto."""
    pasta = Path(diretorio_projeto)
    with (pasta / "config.yaml").open("r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)

    b1 = cfg["bloco_1_estaca"]
    b2 = cfg["bloco_2_estacas"]
    diam_cm = float(cfg["estaca"]["diametro_cm"])
    embut_cm = float(cfg["estaca"]["embutimento_cm"])
    cob_cm = float(cfg["concreto"]["cobrimento_cm"])

    config = ConfiguracaoProjeto(
        nome=str(cfg["nome"]),
        codigo_pbes=str(cfg["codigo_pbes"]),
        empreendimento=str(cfg["empreendimento"]),
        fck_mpa=float(cfg["concreto"]["fck_mpa"]),
        caa=ClasseAgressividade(str(cfg["concreto"]["caa"])),
        cobrimento_cm=cob_cm,
        diametro_estaca_cm=diam_cm,
        embutimento_cm=embut_cm,
        p_adm_referencia_tf=float(cfg["estaca"]["p_adm_referencia_tf"]),
        area_planta_aprox_m2=float(cfg["estrutura"]["area_planta_aprox_m2"]),
        volume_concreto_total_pbes_m3=float(cfg["referencia_pbes"]["volume_concreto_total_m3"]),
        volume_blocos_pbes_m3=float(cfg["referencia_pbes"]["volume_blocos_m3"]),
        area_forma_blocos_pbes_m2=float(cfg["referencia_pbes"]["area_forma_blocos_m2"]),
        geometria_bloco_1e=GeometriaBloco1Estaca(
            largura_x_cm=float(b1["largura_x_cm"]),
            largura_y_cm=float(b1["largura_y_cm"]),
            altura_h_cm=float(b1["altura_h_cm"]),
            diametro_estaca_cm=diam_cm,
            embutimento_estaca_cm=embut_cm,
            cobrimento_cm=cob_cm,
            pilar_a_cm=float(b1.get("pilar_a_cm", 30.0)),
            pilar_b_cm=float(b1.get("pilar_b_cm", 30.0)),
        ),
        geometria_bloco_2e=GeometriaBloco2Estacas(
            largura_b_cm=float(b2["largura_b_cm"]),
            comprimento_l_cm=float(b2["comprimento_l_cm"]),
            altura_h_cm=float(b2["altura_h_cm"]),
            espacamento_e_cm=float(b2["espacamento_e_cm"]),
            diametro_estaca_cm=diam_cm,
            embutimento_estaca_cm=embut_cm,
            cobrimento_cm=cob_cm,
            pilar_ap_cm=float(b2.get("pilar_ap_cm", 25.0)),
            pilar_bp_cm=float(b2.get("pilar_bp_cm", 30.0)),
        ),
        n_barras_tirante_2e=int(b2.get("n_barras_tirante", 12)),
        bitola_tirante_2e_mm=float(b2.get("bitola_tirante_mm", 16.0)),
        dobra_vertical_2e_cm=float(b2.get("dobra_vertical_cm", 60.0)),
        armada_compressao_estaca=bool(cfg["estaca"].get("armada_compressao", False)),
    )

    pontos: List[PontoCarga] = []
    with (pasta / "pontos_carga.csv").open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            pontos.append(
                PontoCarga(
                    id=row["id"].strip(),
                    nk_tf=float(row["nk_tf"]),
                    n_estacas_pbes=int(row["n_estacas_pbes"]),
                    cota_topo_bloco_m=float(row["cota_topo_bloco_m"]),
                    cota_arrasamento_m=float(row["cota_arrasamento_m"]),
                    tipo_elemento=row.get("tipo_elemento", "parede").strip(),
                    orientacao_bloco_2e=row.get("orientacao_bloco_2e", "").strip(),
                    observacao=row.get("observacao", "").strip(),
                )
            )
    return config, pontos


def auditar_projeto(
    config: ConfiguracaoProjeto,
    pontos: List[PontoCarga],
    p_adm_tf: Optional[float] = None,
    sondagem: Optional[Sondagem] = None,
    criterio_geotecnico: str = "media",
) -> ResultadoAuditoriaProjeto:
    """Executa auditoria geotécnica e estrutural completa de todos os pontos do projeto."""
    p_adm = config.p_adm_referencia_tf if p_adm_tf is None else p_adm_tf
    concreto = Concreto(fck_mpa=config.fck_mpa, caa=config.caa)

    auditorias: List[AuditoriaPonto] = []
    excedentes: List[AuditoriaPonto] = []

    for pt in pontos:
        carga_est = pt.carga_por_estaca_pbes_tf
        n_nec = max(1, math.ceil(pt.nk_tf / p_adm))
        taxa = carga_est / p_adm
        if carga_est > p_adm + 1e-6:
            status = "EXCEDE"
            obs = (
                f"Carga/estaca ({carga_est:.1f} tf) > P_adm ({p_adm:.1f} tf); "
                f"requer {n_nec} estaca(s) em vez de {pt.n_estacas_pbes}."
            )
        elif taxa >= 0.90:
            status = "ATENCAO"
            obs = f"Utilização elevada ({taxa * 100:.1f}% de P_adm)."
        else:
            status = "OK"
            obs = ""

        item = AuditoriaPonto(
            ponto=pt,
            carga_por_estaca_pbes_tf=round(carga_est, 2),
            n_estacas_necessario=n_nec,
            taxa_utilizacao_pbes=round(taxa, 3),
            status=status,
            observacao_auditoria=obs,
        )
        auditorias.append(item)
        if status == "EXCEDE":
            excedentes.append(item)

    pontos_1e = [p for p in pontos if p.n_estacas_pbes == 1]
    pontos_2e = [p for p in pontos if p.n_estacas_pbes == 2]

    crit_1e = max(pontos_1e, key=lambda p: p.nk_tf) if pontos_1e else None
    crit_2e = max(pontos_2e, key=lambda p: p.nk_tf) if pontos_2e else None
    max_carga_est = max(p.carga_por_estaca_pbes_tf for p in pontos)

    verif_estaca = verificar_estaca_helice_continua(
        diametro_cm=config.diametro_estaca_cm,
        carga_atuante_tf=max_carga_est,
        concreto=concreto,
        armada_compressao=config.armada_compressao_estaca,
    )

    verif_b1 = (
        verificar_bloco_1_estaca(
            nk_tf=crit_1e.nk_tf,
            geometria=config.geometria_bloco_1e,
            concreto=concreto,
        )
        if crit_1e
        else None
    )

    verif_b2 = (
        verificar_bloco_2_estacas(
            nk_tf=crit_2e.nk_tf,
            geometria=config.geometria_bloco_2e,
            concreto=concreto,
            n_barras_tirante_adotado=config.n_barras_tirante_2e,
            bitola_tirante_adotada_mm=config.bitola_tirante_2e_mm,
            dobra_vertical_ancoragem_cm=config.dobra_vertical_2e_cm,
        )
        if crit_2e
        else None
    )

    # Também verifica o bloco de 2 estacas na capacidade nominal cheia (2 * P_adm)
    verif_b2_cheio = verificar_bloco_2_estacas(
        nk_tf=2.0 * p_adm,
        geometria=config.geometria_bloco_2e,
        concreto=concreto,
        n_barras_tirante_adotado=config.n_barras_tirante_2e,
        bitola_tirante_adotada_mm=config.bitola_tirante_2e_mm,
        dobra_vertical_ancoragem_cm=config.dobra_vertical_2e_cm,
    )

    dim_geo: Dict[float, Optional[ResumoCapacidadeGeotecnica]] = {}
    if sondagem is not None:
        cotas_unicas = sorted({p.cota_arrasamento_m for p in pontos})
        for cota in cotas_unicas:
            dim_geo[cota] = dimensionar_comprimento_estaca(
                sondagem=sondagem,
                diametro_m=config.diametro_estaca_cm / 100.0,
                cota_arrasamento_m=cota,
                carga_alvo_tf=p_adm,
                criterio=criterio_geotecnico,
            )

    return ResultadoAuditoriaProjeto(
        config=config,
        p_adm_adotada_tf=round(p_adm, 2),
        total_pontos=len(pontos),
        carga_total_tf=round(sum(p.nk_tf for p in pontos), 2),
        n_blocos_1e_pbes=len(pontos_1e),
        n_blocos_2e_pbes=len(pontos_2e),
        total_estacas_pbes=sum(p.n_estacas_pbes for p in pontos),
        total_estacas_otimizado=sum(a.n_estacas_necessario for a in auditorias),
        max_carga_ponto_tf=round(max(p.nk_tf for p in pontos), 2),
        max_carga_por_estaca_pbes_tf=round(max_carga_est, 2),
        ponto_mais_solicitado_1e=f"{crit_1e.id} ({crit_1e.nk_tf:.0f} tf)" if crit_1e else "N/A",
        ponto_mais_solicitado_2e=f"{crit_2e.id} ({crit_2e.nk_tf:.0f} tf)" if crit_2e else "N/A",
        pontos_excedentes=excedentes,
        auditoria_pontos=auditorias,
        verificacao_estaca_critica=verif_estaca,
        verificacao_bloco_1e_critico=verif_b1,
        verificacao_bloco_2e_critico=verif_b2,
        verificacao_bloco_2e_capacidade_cheia=verif_b2_cheio,
        dimensionamento_geotecnico_por_cota=dim_geo,
    )


def estudo_sensibilidade_carga_adm(
    pontos: List[PontoCarga],
    cargas_adm_tf: List[float],
) -> List[Dict[str, float | int]]:
    """Simula quantidades de blocos (1e, 2e, 3e+) e total de estacas para diferentes P_adm."""
    cenarios: List[Dict[str, float | int]] = []
    for p_adm in cargas_adm_tf:
        contagem = {1: 0, 2: 0, 3: 0}
        total_est = 0
        for pt in pontos:
            n = max(1, math.ceil(pt.nk_tf / p_adm))
            total_est += n
            contagem[min(n, 3)] += 1
        cenarios.append(
            {
                "p_adm_tf": p_adm,
                "blocos_1e": contagem[1],
                "blocos_2e": contagem[2],
                "blocos_3e_ou_mais": contagem[3],
                "total_estacas": total_est,
                "carga_media_estaca_tf": round(sum(p.nk_tf for p in pontos) / total_est, 2),
            }
        )
    return cenarios
