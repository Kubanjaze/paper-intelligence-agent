# Phase 03 — Paper Intelligence Agent: Implementation Plan

**Version:** 1.1 (updated post-run 2026-03-24)
**Author:** Kerwyn Medrano
**Date:** 2026-03-23
**New API Concepts:** Files API (PDF), Agent SDK, Web Search

---

## 1. Project Overview

### Goal
Build a CLI tool that accepts a PDF research paper and produces three outputs: a structured compound table (`compounds.json`), a SAR findings table (`sar_trends.json`), and a prose analyst report (`report.md`). The agent reads the paper, extracts every compound and assay result, then searches the live literature to place those findings in context.

Optional `--admet` flag pipes extracted compounds directly into the Phase 02 ADMET pipeline.

### What Makes This Phase Educational

Phase 01 used `messages.create()` — you drove every call.
Phase 02 used `batches.create()` — you drove N calls at once, async.
Phase 03 introduces the **agentic model**: you define a goal and a set of tools. Claude decides the sequence, when to search, what to read next, and when it's done.

Three new API surfaces:

| Surface | What you learn |
|---|---|
| **Files API** | Upload PDF once → `file_id` → reuse across multiple requests without re-encoding |
| **Agent SDK** | `query()` / `ClaudeAgentOptions`: agentic loop, built-in tools, Claude drives execution |
| **Web Search** | Built-in `WebSearch` + `WebFetch` tools: Claude searches and synthesizes live literature |

### Architecture: Two-Phase Design

The tool uses two distinct phases that each teach a different API surface:

```
Phase A — Extraction (Files API + direct messages.create())
  Upload PDF → file_id → one structured API call → compounds.json + sar_trends.json

Phase B — Research (Agent SDK + Web Search)
  Feed extracted compounds to an agent → agent searches live literature → writes report.md
```

**Why two phases instead of one big agent?**

The extraction pass benefits from a deterministic, schema-constrained single call — exactly the structured output pattern from Phase 01. The research/synthesis pass benefits from an open-ended agentic loop where the number of searches is unknown upfront. Separating them keeps each phase at its optimal API surface.

### Domain Context

Drug discovery literature is the highest-signal input in the early discovery pipeline. A published paper on KRAS G12C inhibitors contains compound structures, IC50 values, SAR trends, and often clinical/in-vivo data — all locked in PDF prose. This tool mimics the work of a medicinal chemistry analyst: extract the data table, look up what happened to each compound after publication, and write the briefing note.

### Paper Used

**"Discovery and Characterization of Divarasib (GDC-6036), a Potent Covalent Inhibitor of KRAS G12C"**
Journal of Medicinal Chemistry, 2026 — PMC12990036, DOI 10.1021/acs.jmedchem.5c02272

> **Note on PDF acquisition:** PMC PDF downloads are gated behind a JavaScript proof-of-work challenge (returns 1816 bytes of HTML). Bypass: use the NCBI Eutils full-text XML API (`efetch.fcgi?db=pmc&id=...&rettype=xml`) to get the raw JATS XML, then convert to PDF via `data/xml_to_pdf.py` (fpdf2).

---

## 2. Input / Output Contract

### Input
```
data/paper.pdf          # Real research paper (not committed — .gitignore)
```

Required CLI flag: `--paper path/to/paper.pdf`

### Output: `compounds.json`
```json
[
  {
    "compound_name": "divarasib",
    "smiles": null,
    "activity_value": 2.9,
    "activity_unit": "pM",
    "activity_type": "IC50",
    "assay_type": "biochemical",
    "assay_target": "KRAS G12C",
    "assay_species": "human",
    "source_quote": "Divarasib inhibited KRAS G12C with a biochemical IC50 of 2.9 pM...",
    "page_reference": "3"
  }
]
```

### Output: `sar_trends.json`
```json
[
  {
    "finding": "Addition of fluorine at quinazoline C8 improved potency 5-7-fold",
    "structural_feature": "C8-fluorine on quinazoline",
    "direction": "improve",
    "magnitude": "5-7-fold",
    "evidence_quote": "Addition of a fluorine at C8 of the quinazoline improved potency...",
    "page_reference": "5"
  }
]
```

### Output: `report.md`
- Summary of paper scope and key findings
- Compound table with activity values
- SAR narrative
- For each compound: what happened post-publication (clinical outcomes, related mechanisms, structural alerts) — sourced from web search
- Consistency assessment: do the paper's claims hold up against broader literature?

### Output: `admet_report.csv` (with `--admet` flag)
Compounds with SMILES strings are piped into the Phase 02 sequential scorer. Output is written alongside the other artifacts. Compounds without SMILES are skipped with a warning.

---

## 3. Project Structure

```
paper-intelligence-agent/
├── main.py                    # CLI entry point (auto-loads .env)
├── requirements.txt
├── README.md
├── .env                       # API key (gitignored)
├── .gitignore
├── data/
│   ├── paper.pdf              # Research paper (not committed — .gitignore)
│   ├── paper_raw.xml          # PMC JATS XML (not committed)
│   └── xml_to_pdf.py          # Helper: convert PMC XML → PDF (bypasses JS gate)
├── output/
│   ├── compounds.json         # Extracted compounds (committed)
│   ├── sar_trends.json        # Extracted SAR trends (committed)
│   └── report.md              # Agent-written analyst report (committed)
└── src/
    ├── __init__.py
    ├── models.py              # Pydantic schemas with field_validator coercions
    ├── pdf_uploader.py        # Files API: upload PDF → file_id, cleanup on exit
    ├── extractor.py           # Phase A: file_id → compounds.json + sar_trends.json
    ├── research_agent.py      # Phase B: Agent SDK — contextualize + write report.md
    └── admet_handoff.py       # Convert compounds.json → CSV → Phase 02 scorer
```

---

## 4. Module Specifications

### 4.1 `src/models.py` — Pydantic Schemas

```python
from pydantic import BaseModel, field_validator
from typing import Literal, Optional

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
    assay_target: Optional[str] = None   # Optional: DMPK rows may have no target
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
    magnitude: Optional[str] = None
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
```

**Why validators are necessary:** The model returns valid-but-non-matching values in practice:
- `page_reference` comes back as an integer (5, 6, 7…) not a string
- `activity_type` comes back as "SOS exchange IC50", "MW", "oral bioavailability (F%)"
- `assay_type` comes back as "SOS exchange biochemical assay", "PK study", "physicochemical property"
- `assay_species` comes back as "dog" (not in the enum)
- `activity_unit` comes back as "Da", "Å²"

`mode="before"` validators run before Pydantic's type coercion and map unknown values to `"other"` instead of raising a `ValidationError`. This made the difference between 55 validation errors and a clean run.

**Why `Literal` only on enumerable fields:** Free-text fields (`finding`, `source_quote`, `structural_feature`) cannot be enumerated — using `str` there is correct. `Literal` is reserved for fields where the full value set is known and deterministic filtering is needed downstream (e.g., `activity_unit == "nM"` in ADMET handoff).

### 4.2 `src/pdf_uploader.py` — Files API

```python
import os
import anthropic

def upload_pdf(path: str) -> str:
    """Upload PDF via Files API. Returns file_id."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    with open(path, "rb") as f:
        uploaded = client.beta.files.upload(
            file=(os.path.basename(path), f, "application/pdf"),
        )
    return uploaded.id

def delete_file(file_id: str) -> None:
    """Clean up uploaded file after session. Wraps in try/except so cleanup
    errors don't fail the run."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    try:
        client.beta.files.delete(file_id)
    except Exception as e:
        print(f"  Warning: could not delete file {file_id}: {e}")
```

**Key decisions:**
- Upload happens once at startup; `file_id` is reused for both extraction and any follow-up calls
- `delete_file()` called in a `finally` block in `main.py` — file is cleaned up even on error
- Files API is beta — requires `client.beta.files` and `client.beta.messages.create()`
- PDF not committed to git (`.gitignore`) — user supplies their own paper

### 4.3 `src/extractor.py` — Phase A: Structured Extraction

Single `client.beta.messages.create()` call. PDF referenced by `file_id` in a document content block.

```python
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
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    target_context = f"The paper studies the target: {target_hint}." if target_hint else ""

    response = client.beta.messages.create(
        model=model,
        max_tokens=8192,
        system=EXTRACTION_SYSTEM_PROMPT,
        messages=[{
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

1. Every compound mentioned with quantitative activity data
2. Every SAR trend stated or implied
3. Paper-level metadata: paper_title, target

Return ONLY a JSON object matching the ExtractionResult schema."""
                }
            ]
        }],
        betas=["files-api-2025-04-14"],
    )

    text = next((b.text for b in response.content if b.type == "text"), "")

    # JSON guard: isolate first { ... last }
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"No JSON object found in extraction response: {text[:200]}")

    data = json.loads(text[start:end+1])
    return ExtractionResult.model_validate(data)
```

**Why `claude-opus-4-6` for extraction:** Dense scientific text with multi-row data tables, compound names, and units requires the highest accuracy. Missing an IC50 or misreading a unit invalidates downstream work.

### 4.4 `src/research_agent.py` — Phase B: Agent SDK

```python
import os
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

async def run_research_agent(
    extraction_json: str,
    output_dir: str,
    model: str = "claude-opus-4-6",
) -> None:
    abs_output_dir = os.path.abspath(output_dir)  # MUST be absolute

    prompt = f"""\
You are a drug discovery analyst. You have been given a structured extraction from a research paper.

CRITICAL INSTRUCTIONS:
1. Your FIRST action must be a WebSearch to gather context on the paper and compounds.
2. Your FINAL action must be to call the Write tool to write "report.md" in the current directory.
   Do NOT end without writing this file.

Here is the structured extraction from the paper:

{extraction_json}

[... search strategy and report format instructions ...]

You MUST end by calling Write to create report.md. This is required.\
"""

    result_text = None
    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            cwd=abs_output_dir,
            allowed_tools=["WebSearch", "WebFetch", "Write"],
            permission_mode="acceptEdits",
            model=model,
        ),
    ):
        if isinstance(message, ResultMessage):
            print(f"  Agent complete. Stop reason: {message.stop_reason}")
            result_text = message.result

    # Fallback: if the agent never used Write, save result text as report.md
    report_path = os.path.join(abs_output_dir, "report.md")
    if not os.path.exists(report_path) and result_text:
        print("  Agent did not use Write tool — saving result text as report.md")
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(result_text)
```

**Key decisions:**
- `cwd` **must be an absolute path** (`os.path.abspath(output_dir)`) — relative paths silently cause the Write tool to fail or write to the wrong location
- The prompt must **explicitly require Write as the final action** — without this, the agent treats the task as a chat response and never touches the filesystem
- **Fallback write** saves `ResultMessage.result` to `report.md` if the agent completes without using the Write tool — ensures the run always produces a report
- `allowed_tools=["WebSearch", "WebFetch", "Write"]` — minimum viable set; no Bash, no Read, no Edit
- `permission_mode="acceptEdits"` — auto-accepts file writes; avoids interactive prompts in CLI context
- `claude-opus-4-6` for research synthesis: reasoning across multiple search results and contradictory scientific claims requires the strongest model

### 4.5 `src/admet_handoff.py` — Phase 02 Integration

Calls Phase 02's `main.py` as a subprocess using `sys.executable`. Wraps in try/except so ADMET failures don't fail the main pipeline.

**Why `subprocess` instead of direct import:** Phase 02 is a standalone project with its own virtualenv. The handoff is a process boundary, not a library call.

### 4.6 `main.py` — CLI Entry Point

```python
import os
import sys

# Windows UTF-8 fix — must precede all other imports
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Auto-load .env from project root
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.isfile(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())
```

The `.env` loader uses `setdefault` — shell-level env vars take precedence. No `python-dotenv` dependency needed.

---

## 5. CLI Flag Reference

| Flag | Type | Default | Description |
|---|---|---|---|
| `--paper` | str | (required) | Path to input PDF |
| `--target` | str | None | Target name hint — improves extraction focus |
| `--output` | str | `output` | Directory for all output artifacts |
| `--model` | str | `claude-opus-4-6` | Model for both extraction and agent phases |
| `--admet` | flag | False | Run Phase 02 ADMET scorer on compounds with SMILES |
| `--phase02` | str | `../compound-intelligence-pipeline` | Path to Phase 02 project root (required with `--admet`) |

---

## 6. Output Artifacts

| File | Produced by | Description |
|---|---|---|
| `output/compounds.json` | `extractor.py` | Structured compound table, Pydantic-validated |
| `output/sar_trends.json` | `extractor.py` | Structured SAR findings, Pydantic-validated |
| `output/report.md` | `research_agent.py` | Agent-written analyst report with search citations |
| `output/compounds_for_admet.csv` | `admet_handoff.py` | Temp CSV for Phase 02 input (with `--admet`) |
| `output/admet_report.csv` | Phase 02 pipeline | ADMET-enriched compound table (with `--admet`) |
| `output/admet_report.md` | Phase 02 pipeline | ADMET summary report (with `--admet`) |

---

## 7. Key Patterns Being Learned

| Pattern | Where | Notes |
|---|---|---|
| `client.beta.files.upload()` | `pdf_uploader.py` | Upload once, reuse `file_id`; free upload, normal billing on use |
| File cleanup in `finally` | `main.py` | Files persist 29 days if not deleted — always clean up |
| `{"type": "document", "source": {"type": "file", "file_id": "..."}}` | `extractor.py` | How file_id appears in a message content block |
| `betas=["files-api-2025-04-14"]` | `extractor.py` | Required beta header for Files API in messages |
| `query(prompt, options)` | `research_agent.py` | Agent SDK entry point; async generator of messages |
| `ClaudeAgentOptions(cwd=abs_path, ...)` | `research_agent.py` | `cwd` must be absolute or Write tool silently misfires |
| `allowed_tools` | `research_agent.py` | Minimum viable tool set — restrict what the agent can do |
| `permission_mode="acceptEdits"` | `research_agent.py` | Auto-accept file writes; avoid prompts in CLI context |
| `ResultMessage` | `research_agent.py` | Terminal message type; contains agent's final answer + fallback content |
| `field_validator(mode="before")` | `models.py` | Coerce model output before Pydantic type validation; maps unknown enum values → "other" |
| `os.environ.setdefault()` in `.env` loader | `main.py` | Shell vars take precedence over .env |
| Hybrid search via prompt engineering | `research_agent.py` | Agent SDK WebSearch has no `allowed_domains`; scope through instructions |
| `subprocess` cross-project call | `admet_handoff.py` | Cross-phase integration without breaking dependency boundaries |

---

## 8. Lessons Learned (post-run)

### PMC PDF acquisition
PMC's CDN returns a JavaScript proof-of-work challenge (1816 bytes of HTML) when downloading PDFs without a browser. Workaround:
1. Use NCBI Eutils `efetch` API to download full-text JATS XML: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pmc&id=PMC{ID}&rettype=xml&retmode=xml`
2. Convert XML to PDF with `data/xml_to_pdf.py` (fpdf2). The script walks the JATS tree, classifies text by tag (`article-title`, `title`, `p`, `td`), deduplicates adjacent identical lines, and renders to a 23-page PDF.

### Pydantic validation (55 errors → 0)
The model returns values like `"SOS exchange IC50"` for `activity_type` and bare integers for `page_reference`. `mode="before"` validators fix this without touching extraction prompt logic. The key lesson: schema validators are the right layer for model output coercion, not prompt engineering.

### Agent Write tool reliability
The agent must receive:
1. An absolute `cwd` path — relative paths silently cause writes to the wrong location
2. An explicit instruction that Write is a **required** final action — without this, the agent treats the entire task as a chat response
3. A fallback in the calling code that saves `ResultMessage.result` if no file appears

---

## 9. What Is NOT in Scope

- RDKit or any computed descriptors — SMILES stored as-reported, no canonicalization
- Multi-paper comparison — Phase 05
- Database writes — all outputs are flat files
- Streaming agent output — `ResultMessage` is sufficient for CLI context
- Custom MCP tools — built-in `WebSearch` / `WebFetch` / `Write` cover all needs

---

## 10. Dependencies

```
anthropic>=0.86.0        # Files API, messages API
pydantic>=2.0.0          # extraction schema validation
claude-agent-sdk         # Agent SDK (pip install claude-agent-sdk)
anyio                    # async runner for query()
fpdf2                    # PDF generation from XML (xml_to_pdf.py helper)
```

Claude Code CLI must be installed for the Agent SDK to function:
```
pip install claude-agent-sdk
```

---

## 11. Error Handling Strategy

| Error Source | Handling |
|---|---|
| Missing `ANTHROPIC_API_KEY` | `sys.exit(1)` before any API call |
| PDF not found | `FileNotFoundError` before upload |
| Files API upload failure | Exception propagates; `finally` block still runs (file_id will be None) |
| Extraction returns no JSON | `ValueError` with partial text for debugging |
| Pydantic validation failure | `mode="before"` validators coerce unknown values → "other" instead of raising |
| Agent SDK failure | Exception propagates; structured outputs already written (Phase A complete) |
| Agent doesn't use Write tool | Fallback saves `ResultMessage.result` to `report.md` |
| ADMET handoff failure | Logged; does not fail the main pipeline |
| File cleanup failure | Logged as warning; does not fail the run |

---

## 12. Carry-Forward Rules from Phase 01 / 02

- `Literal` types on all enumerable Pydantic fields — applied throughout
- Windows UTF-8 fix in `main.py` — carried forward
- `--model` flag for model override — carried forward
- `os.environ["ANTHROPIC_API_KEY"]` via `.env` auto-loader — no dotenv dependency
- Commit and push at each milestone
- `source` provenance — `source_quote` field captures verbatim evidence from paper

---

## 13. README Limitations Section

```markdown
## Limitations

- **Extraction accuracy depends on paper formatting.** PDFs with complex multi-column layouts,
  tables embedded as images, or non-standard notation may cause missed or incorrect extractions.
  Always validate `compounds.json` against the source paper before downstream use.

- **SMILES strings are extracted as reported.** No canonicalization or validity check is performed.
  If the paper does not report SMILES (most do not), `smiles` will be null and those compounds
  are skipped in the ADMET handoff.

- **Web search results reflect the live web at time of run.** Search results are synthesized by
  the agent; they are not peer-reviewed and may include preprints, conference abstracts, or
  incorrect information. Treat `report.md` as a starting point for analysis, not a final answer.

- **Agent search scope is guided by prompt, not API restrictions.** The hybrid search strategy
  (open web for compounds, scientific sources for clinical data) is enforced through instructions
  to the agent, not hard domain filtering. The agent may deviate in edge cases.

- **PMC PDFs require the NCBI Eutils XML workaround.** Direct PMC PDF downloads are gated by
  a JavaScript proof-of-work challenge. Use `data/xml_to_pdf.py` to convert the JATS XML
  (available via `efetch`) to a PDF that the Files API can ingest.

- **ADMET handoff requires Phase 02 installed and `ANTHROPIC_API_KEY` in the environment.**
  The handoff calls Phase 02's `main.py` as a subprocess. If Phase 02 is not at the expected
  path or its virtualenv is not activated, the handoff will fail (the rest of the pipeline is unaffected).
```
