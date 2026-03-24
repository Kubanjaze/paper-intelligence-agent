"""
models.py — Pydantic schemas for Phase 03.

Literal types are used only on enumerable fields where the full value set is
known and deterministic filtering is needed downstream (e.g. activity_unit == "nM"
in the ADMET handoff). Free-text fields (finding, source_quote, structural_feature)
use str — they cannot be usefully enumerated.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


class Compound(BaseModel):
    compound_name: str
    smiles: Optional[str] = None
    activity_value: Optional[float] = None
    activity_unit: Optional[Literal["nM", "uM", "pM", "%", "other"]] = None
    activity_type: Literal["IC50", "Ki", "EC50", "Kd", "%inhibition", "other"]
    assay_type: Literal["biochemical", "cellular", "in-vivo", "other"]
    assay_target: str
    assay_species: Optional[Literal["human", "rat", "mouse", "other"]] = None
    source_quote: str
    page_reference: Optional[str] = None


class SARTrend(BaseModel):
    finding: str
    structural_feature: str
    direction: Literal["improve", "worsen", "neutral", "unclear"]
    magnitude: Optional[str] = None  # e.g. "10-fold", ">100x"
    evidence_quote: str
    page_reference: Optional[str] = None


class ExtractionResult(BaseModel):
    paper_title: Optional[str] = None
    target: Optional[str] = None
    compounds: list[Compound]
    sar_trends: list[SARTrend]
