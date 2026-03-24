"""
admet_handoff.py — Phase 02 integration.

Converts extracted compounds with SMILES to a CSV and runs the Phase 02
sequential scorer as a subprocess. Compounds without SMILES are skipped.
"""
import csv
import subprocess
import sys
from pathlib import Path

from src.models import ExtractionResult


def handoff_to_admet(
    extraction: ExtractionResult,
    output_dir: str,
    phase02_path: str,
    model: str = "claude-haiku-4-5-20251001",
) -> None:
    """
    Convert extracted compounds with SMILES to a CSV and run the Phase 02
    sequential scorer. Compounds without SMILES are skipped.

    Args:
        extraction:   Validated ExtractionResult from Phase A.
        output_dir:   Directory to write compounds_for_admet.csv and admet_report.*.
        phase02_path: Path to the Phase 02 project root (compound-intelligence-pipeline/).
        model:        Model for Phase 02 scorer. Haiku is sufficient for formulaic scoring.
    """
    scoreable = [c for c in extraction.compounds if c.smiles]
    skipped = len(extraction.compounds) - len(scoreable)

    if skipped:
        print(f"  Skipping {skipped} compound(s) with no reported SMILES.")

    if not scoreable:
        print("  No compounds with SMILES found. ADMET handoff skipped.")
        return

    # Write temp CSV for Phase 02 input
    csv_path = Path(output_dir) / "compounds_for_admet.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["compound_id", "smiles", "activity_value", "activity_type"],
        )
        writer.writeheader()
        for c in scoreable:
            writer.writerow(
                {
                    "compound_id": c.compound_name.replace(" ", "_"),
                    "smiles": c.smiles,
                    "activity_value": c.activity_value or "",
                    "activity_type": c.activity_type,
                }
            )

    admet_csv = Path(output_dir) / "admet_report.csv"
    admet_md = Path(output_dir) / "admet_report.md"

    print(f"  Running Phase 02 scorer on {len(scoreable)} compound(s)...")
    try:
        subprocess.run(
            [
                sys.executable,
                str(Path(phase02_path) / "main.py"),
                "--input", str(csv_path),
                "--output", str(admet_csv),
                "--report", str(admet_md),
                "--model", model,
            ],
            check=True,
            cwd=phase02_path,
        )
        print(f"  ADMET report written to {admet_csv}")
    except subprocess.CalledProcessError as exc:
        print(f"  Warning: ADMET handoff failed (exit {exc.returncode}). "
              "Main pipeline unaffected.")
    except FileNotFoundError:
        print(f"  Warning: Phase 02 not found at {phase02_path}. "
              "ADMET handoff skipped.")
