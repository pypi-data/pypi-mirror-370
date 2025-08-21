"""Functions for parsing virulencefinder result."""

import json
import logging
from typing import Any

from ..models.phenotype import ElementType, ElementVirulenceSubtype
from ..models.phenotype import PredictionSoftware as Software
from ..models.phenotype import (
    VirulenceElementTypeResult,
    VirulenceGene,
    VirulenceMethodIndex,
)
from ..models.sample import MethodIndex
from ..models.typing import TypingMethod, TypingResultGeneAllele

LOG = logging.getLogger(__name__)


def parse_vir_gene(
    info: dict[str, Any], subtype: ElementVirulenceSubtype = ElementVirulenceSubtype.VIR
) -> VirulenceGene:
    """Parse virulence gene prediction results."""
    start_pos, end_pos = map(int, info["position_in_ref"].split(".."))
    # Some genes doesnt have accession numbers
    accnr = None if info["accession"] == "NA" else info["accession"]
    return VirulenceGene(
        # info
        gene_symbol=info["virulence_gene"],
        accession=accnr,
        sequence_name=info["protein_function"].strip(),
        # gene classification
        element_type=ElementType.VIR,
        element_subtype=subtype,
        # position
        ref_start_pos=start_pos,
        ref_end_pos=end_pos,
        ref_gene_length=info["template_length"],
        alignment_length=info["HSP_length"],
        # prediction
        identity=info["identity"],
        coverage=info["coverage"],
    )


def _parse_vir_results(pred: str) -> VirulenceElementTypeResult:
    """Parse virulence prediction results from virulencefinder."""
    # parse virulence finder results
    species = list(k for k in pred["virulencefinder"]["results"])
    vir_genes = []
    for key, genes in pred["virulencefinder"]["results"][species[0]].items():
        # skip stx typing result
        if key == "stx":
            continue
        # assign element subtype
        virulence_group = key.split("_")[1] if "_" in key else key
        match virulence_group:
            case "toxin":
                subtype = ElementVirulenceSubtype.TOXIN
            case _:
                subtype = ElementVirulenceSubtype.VIR
        # parse genes
        if not genes == "No hit found":
            for gene in genes.values():
                vir_genes.append(parse_vir_gene(gene, subtype))
    # sort genes
    genes = sorted(vir_genes, key=lambda entry: (entry.gene_symbol, entry.coverage))
    return VirulenceElementTypeResult(genes=genes, phenotypes={}, variants=[])


def parse_virulence_pred(path: str) -> VirulenceMethodIndex | None:
    """Parse virulencefinder virulence prediction results.

    :param file: File name
    :type file: str
    :return: Return element type if virulence was predicted else null
    :rtype: ElementTypeResult | None
    """
    LOG.info("Parsing virulencefinder virulence prediction")
    with open(path, "rb") as inpt:
        pred = json.load(inpt)
        if "virulencefinder" in pred:
            results: VirulenceElementTypeResult = _parse_vir_results(pred)
            result = VirulenceMethodIndex(
                type=ElementType.VIR, software=Software.VIRFINDER, result=results
            )
        else:
            result = None
    return result


def parse_stx_typing(path: str) -> MethodIndex | None:
    """Parse virulencefinder's output re stx typing"""
    LOG.info("Parsing virulencefinder stx results")
    with open(path, "rb") as inpt:
        pred_obj = json.load(inpt)
        # if has valid results
        pred_result = None
        if "virulencefinder" in pred_obj:
            results = pred_obj["virulencefinder"]["results"]
            species = list(results)
            for assay, result in results[species[0]].items():
                # skip non typing results
                if not assay == "stx":
                    continue

                # if no stx gene was identified
                if isinstance(result, str):
                    continue

                # take first result as the valid prediction
                hit = next(iter(result.values()))
                vir_gene = parse_vir_gene(hit)
                gene = TypingResultGeneAllele(**vir_gene.model_dump())
                pred_result = MethodIndex(
                    type=TypingMethod.STX,
                    software=Software.VIRFINDER,
                    result=gene,
                )
    return pred_result
