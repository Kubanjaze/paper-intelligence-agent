"""
extractor.py — Phase A: structured extraction from uploaded PDF via Files API.

Single client.beta.messages.create() call. PDF referenced by file_id in a
document content block. Returns a Pydantic-validated ExtractionResult.
"""
import json
import os

import anthropic

from src.models import ExtractionResult

EXTRACTION_SYSTEM_PROMPT = """\
You are a medicinal chemistry analyst. Extract structured data from the provided research paper.
Return ONLY valid JSON matching the schema exactly. No prose, no markdown fences, no commentary.\
"""


def extract_from_paper(
    file_id: str,
    target_hint: str | None = None,
    model: str = "claude-opus-4-6",
) -> ExtractionResult:
    """
    Phase A: use file_id to extract compounds and SAR trends from the paper.

    Args:
        file_id:     Files API file_id returned by upload_pdf().
        target_hint: Optional target name (e.g. "CETP") to focus extraction.
        model:       Model to use. Defaults to claude-opus-4-6 for accuracy on
                     dense scientific text.

    Returns:
        Validated ExtractionResult containing compounds and SAR trends.
    """
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    target_context = f"The paper studies the target: {target_hint}." if target_hint else ""

    response = client.beta.messages.create(
        model=model,
        max_tokens=8192,
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {"type": "file", "file_id": file_id},
                    },
                    {
                        "type": "text",
                        "text": f"""{target_context}

Extract all of the following from this paper:

1. Every compound mentioned with quantitative activity data:
   - compound_name, smiles (if reported), activity_value, activity_unit,
     activity_type, assay_type, assay_target, assay_species,
     source_quote (verbatim sentence from paper), page_reference

2. Every SAR trend stated or implied:
   - finding (plain English summary), structural_feature, direction
     (improve/worsen/neutral/unclear), magnitude (if stated),
     evidence_quote (verbatim), page_reference

3. Paper-level metadata: paper_title, target

Return ONLY a JSON object matching this schema:
{{
  "paper_title": "<string>",
  "target": "<string>",
  "compounds": [ ...Compound objects... ],
  "sar_trends": [ ...SARTrend objects... ]
}}""",
                    },
                ],
            }
        ],
        betas=["files-api-2025-04-14"],
    )

    text = next((b.text for b in response.content if b.type == "text"), "")

    # JSON guard: isolate first { ... last }
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in extraction response: {text[:200]}")

    data = json.loads(text[start : end + 1])
    return ExtractionResult.model_validate(data)
