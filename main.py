"""
main.py — Paper Intelligence Agent

Usage:
    python main.py --paper data/paper.pdf
    python main.py --paper data/paper.pdf --target CETP
    python main.py --paper data/paper.pdf --admet --phase02 ../compound-intelligence-pipeline
    python main.py --paper data/paper.pdf --output results/ --target CETP --admet
"""
import os
import sys

# Windows UTF-8 fix — must precede all other imports that touch I/O
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Load .env from project root if present (so ANTHROPIC_API_KEY doesn't need
# to be set manually in the shell each time)
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.isfile(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

import argparse
import json

import anyio

from src.pdf_uploader import upload_pdf, delete_file
from src.extractor import extract_from_paper
from src.research_agent import run_research_agent
from src.admet_handoff import handoff_to_admet


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Paper Intelligence Agent — extract, contextualize, and report on a research paper",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--paper",   required=True,
                        help="Path to input PDF")
    parser.add_argument("--target",  default=None,
                        help="Target name hint (e.g. 'CETP') — improves extraction focus")
    parser.add_argument("--output",  default="output",
                        help="Output directory for all artifacts")
    parser.add_argument("--model",   default="claude-opus-4-6",
                        help="Model for extraction and agent phases")
    parser.add_argument("--skip-agent", action="store_true",
                        help="Skip Phase B research agent (web search + report). "
                             "Saves ~$0.50–$1.00 per paper.")
    parser.add_argument("--admet",   action="store_true",
                        help="Run ADMET scoring on extracted compounds with SMILES")
    parser.add_argument("--phase02", default="../compound-intelligence-pipeline",
                        help="Path to Phase 02 project root (required with --admet)")

    args = parser.parse_args()

    if "ANTHROPIC_API_KEY" not in os.environ:
        print("ERROR: ANTHROPIC_API_KEY not set.", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(args.paper):
        print(f"ERROR: paper not found: {args.paper}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(args.output, exist_ok=True)

    # ── Phase A — Upload + Extract ──────────────────────────────────────────
    print(f"Uploading {args.paper}...")
    file_id = upload_pdf(args.paper)
    print(f"Uploaded: {file_id}")

    try:
        print("Extracting compounds and SAR trends...")
        extraction = extract_from_paper(
            file_id=file_id,
            target_hint=args.target,
            model=args.model,
        )
        print(f"  Found {len(extraction.compounds)} compound(s), "
              f"{len(extraction.sar_trends)} SAR trend(s).")

        compounds_path = os.path.join(args.output, "compounds.json")
        sar_path       = os.path.join(args.output, "sar_trends.json")

        with open(compounds_path, "w", encoding="utf-8") as f:
            json.dump([c.model_dump() for c in extraction.compounds], f, indent=2)
        with open(sar_path, "w", encoding="utf-8") as f:
            json.dump([s.model_dump() for s in extraction.sar_trends], f, indent=2)

        print(f"  compounds.json  → {compounds_path}")
        print(f"  sar_trends.json → {sar_path}")

        # ── Phase B — Research Agent ────────────────────────────────────────
        if args.skip_agent:
            print("Skipping research agent (--skip-agent).")
        else:
            print("Running research agent (web search + report)...")
            extraction_json = json.dumps(extraction.model_dump(), indent=2)
            anyio.run(run_research_agent, extraction_json, args.output, args.model)
            print(f"  report.md       → {os.path.join(args.output, 'report.md')}")

        # ── ADMET Handoff (optional) ────────────────────────────────────────
        if args.admet:
            print("Running ADMET handoff...")
            handoff_to_admet(
                extraction=extraction,
                output_dir=args.output,
                phase02_path=args.phase02,
            )

    finally:
        print(f"Cleaning up uploaded file {file_id}...")
        delete_file(file_id)

    print(f"\nDone. Artifacts in {args.output}/")


if __name__ == "__main__":
    main()
