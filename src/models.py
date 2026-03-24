"""
models.py — Pydantic schemas for Phase 03.

Literal types are used only on enumerable fields where the full value set is
known and deterministic filtering is needed downstream (e.g. activity_unit == "nM"
in the ADMET handoff). Free-text fields (finding, source_quote, structural_feature)
use str — they cannot be usefully enumerated.

Validators coerce model output to schema:
- page_reference: int → str (model often returns bare page numbers)
- Literal fields: unknown values → "other" (model may return descriptive strings
  like "SOS exchange IC50" or "PK study")
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, field_validator, model_validator

_ACTIVITY_TYPE_VALUES = {"IC50", "Ki", "EC50", "Kd", "%inhibition", "other"}
_ASSAY_TYPE_VALUES = {"biochemical", "cellular", "in-vivo", "other"}
_ACTIVITY_UNIT_VALUES = {"nM", "uM", "pM", "%", "other"}
_ASSAY_SPECIES_VALUES = {"human", "rat", "mouse", "other"}


def _to_other_if_unknown(value: str | None, allowed: set[str]) -> str | None:
    if value is None:
        return None
    return value if value in allowed else "other"


class Compound(BaseModel):
    compound_name: str
    smiles: Optional[str] = None
    activity_value: Optional[float] = None
    activity_unit: Optional[Literal["nM", "uM", "pM", "%", "other"]] = None
    activity_type: Literal["IC50", "Ki", "EC50", "Kd", "%inhibition", "other"]
    assay_type: Literal["biochemical", "cellular", "in-vivo", "other"]
    assay_target: Optional[str] = None
    assay_species: Optional[Literal["human", "rat", "mouse", "other"]] = None
    source_quote: str
    page_reference: Optional[str] = None

    @field_validator("page_reference", mode="before")
    @classmethod
    def coerce_page_reference(cls, v):
        return str(v) if v is not None else None

    @field_validator("activity_type", mode="before")
    @classmethod
    def coerce_activity_type(cls, v):
        return _to_other_if_unknown(v, _ACTIVITY_TYPE_VALUES) or "other"

    @field_validator("assay_type", mode="before")
    @classmethod
    def coerce_assay_type(cls, v):
        return _to_other_if_unknown(v, _ASSAY_TYPE_VALUES) or "other"

    @field_validator("activity_unit", mode="before")
    @classmethod
    def coerce_activity_unit(cls, v):
        return _to_other_if_unknown(v, _ACTIVITY_UNIT_VALUES)

    @field_validator("assay_species", mode="before")
    @classmethod
    def coerce_assay_species(cls, v):
        return _to_other_if_unknown(v, _ASSAY_SPECIES_VALUES)


class SARTrend(BaseModel):
    finding: str
    structural_feature: str
    direction: Literal["improve", "worsen", "neutral", "unclear"]
    magnitude: Optional[str] = None  # e.g. "10-fold", ">100x"
    evidence_quote: str
    page_reference: Optional[str] = None

    @field_validator("page_reference", mode="before")
    @classmethod
    def coerce_page_reference(cls, v):
        return str(v) if v is not None else None


class ExtractionResult(BaseModel):
    paper_title: Optional[str] = None
    target: Optional[str] = None
    compounds: list[Compound]
    sar_trends: list[SARTrend]
