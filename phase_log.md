# Phase 03 — Paper Intelligence Agent

**Status:** Complete ✅
**Started:** 2026-03-23
**Completed:** 2026-03-24
**Repo:** https://github.com/Kubanjaze/paper-intelligence-agent

## New API Concepts
- Files API — upload PDF once, reference by `file_id` across multiple requests; cleanup in `finally`
- Agent SDK — `query()` / `ClaudeAgentOptions`, Claude drives the tool loop with WebSearch + WebFetch + Write
- Pydantic v2 field validators — `mode="before"` coercions to handle model output that doesn't match schema enums

## Architect Decisions (resolved 2026-03-23)
- [x] Agent SDK (not manual tool loop)
- [x] compounds.json schema approved as proposed
- [x] Web search scope: hybrid (open web for compound names, scoped for clinical data — via prompt engineering)
- [x] ADMET handoff: in scope for Phase 03
- [x] Target paper: real — divarasib (GDC-6036) KRAS G12C paper, J. Med. Chem. 2026, PMC12990036

## Key Engineering Lessons
- PMC PDF downloads are gated behind a JS proof-of-work challenge — bypass via NCBI Eutils full-text XML API + fpdf2 conversion
- Agent SDK `cwd` must be an absolute path (`os.path.abspath`) or the Write tool may fail silently
- Prompt must explicitly require Write as the final action, plus a fallback that saves `ResultMessage.result` if Write is never called
- `PYTHONUTF8=1` always required on Windows; load `.env` in `main.py` so key doesn't need manual export

## Pipeline Run (2026-03-24)
- Paper: "Discovery and Characterization of Divarasib (GDC-6036), a Potent Covalent Inhibitor of KRAS G12C"
- Extracted: 12 compounds, 8 SAR trends
- Report: 201 lines, Phase III trial status, clinical comparison vs. sotorasib/adagrasib, 10 sources cited

## Artifacts
- `implementation.md` — written
- `output/compounds.json` — 12 compounds (committed)
- `output/sar_trends.json` — 8 SAR trends (committed)
- `output/report.md` — analyst report (committed)
