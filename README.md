# Paper Intelligence Agent

**Phase 03** of the Claude API learning series.

Accepts a research paper PDF and produces a structured compound table, SAR findings, and a prose analyst report enriched with live literature context.

**New API concepts:** Files API (PDF upload), Agent SDK, built-in web search.

---

## What it does

```
Phase A — Extraction (Files API + messages.create)
  Upload PDF → file_id → structured extraction → compounds.json + sar_trends.json

Phase B — Research (Agent SDK + WebSearch/WebFetch/Write)
  Extraction results → agent searches live literature → writes report.md
```

---

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt

# Claude Code CLI is required for the Agent SDK
pip install claude-agent-sdk
```

Set your API key:
```bash
set ANTHROPIC_API_KEY=sk-ant-...
```

Place your PDF at `data/paper.pdf` (not committed to git — supply your own).

---

## Usage

```bash
# Basic run
PYTHONUTF8=1 python main.py --paper data/paper.pdf

# With target hint (improves extraction focus)
PYTHONUTF8=1 python main.py --paper data/paper.pdf --target CETP

# Custom output directory
PYTHONUTF8=1 python main.py --paper data/paper.pdf --output results/ --target CETP

# With ADMET handoff to Phase 02
PYTHONUTF8=1 python main.py --paper data/paper.pdf --target CETP \
    --admet --phase02 ../compound-intelligence-pipeline
```

On Windows without `PYTHONUTF8=1`, the main.py UTF-8 fix handles encoding automatically.

---

## Output artifacts

| File | Description |
|---|---|
| `output/compounds.json` | Structured compound table (Pydantic-validated) |
| `output/sar_trends.json` | Structured SAR findings (Pydantic-validated) |
| `output/report.md` | Analyst report with live literature context |
| `output/compounds_for_admet.csv` | Temp input for Phase 02 (`--admet` only) |
| `output/admet_report.csv` | ADMET-enriched compound table (`--admet` only) |
| `output/admet_report.md` | ADMET summary report (`--admet` only) |

---

## CLI flags

| Flag | Default | Description |
|---|---|---|
| `--paper` | (required) | Path to input PDF |
| `--target` | None | Target name hint — improves extraction focus |
| `--output` | `output` | Directory for all output artifacts |
| `--model` | `claude-opus-4-6` | Model for extraction and agent phases |
| `--admet` | False | Run Phase 02 ADMET scorer on compounds with SMILES |
| `--phase02` | `../compound-intelligence-pipeline` | Path to Phase 02 root (with `--admet`) |

---

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

- **ADMET handoff requires Phase 02 installed and `ANTHROPIC_API_KEY` in the environment.**
  The handoff calls Phase 02's `main.py` as a subprocess. If Phase 02 is not at the expected
  path or its virtualenv is not activated, the handoff will fail (the rest of the pipeline is unaffected).

---

## Project structure

```
paper-intelligence-agent/
├── main.py                    # CLI entry point
├── requirements.txt
├── README.md
├── .gitignore
├── data/
│   └── paper.pdf              # Real CETP paper (not committed — user-supplied)
└── src/
    ├── __init__.py
    ├── models.py              # Pydantic schemas: Compound, SARTrend, ExtractionResult
    ├── pdf_uploader.py        # Files API: upload PDF → file_id, cleanup on exit
    ├── extractor.py           # Phase A: file_id → compounds.json + sar_trends.json
    ├── research_agent.py      # Phase B: Agent SDK — web search + write report.md
    └── admet_handoff.py       # Convert compounds.json → CSV → Phase 02 scorer
```

---

## Related projects

- [Phase 01 — Molecule Research Assistant](https://github.com/Kubanjaze/molecule-assistant) — structured outputs, tool use, vision, streaming
- [Phase 02 — Compound Intelligence Pipeline](https://github.com/Kubanjaze/compound-intelligence-pipeline) — Batches API, async polling, sequential fallback
