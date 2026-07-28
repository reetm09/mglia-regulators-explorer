"""Validate perturbations.json against schema and cross-field constraints.

Standalone script, writes a report to data/validation_report.txt.

Usage:
    python scripts/validate_records.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from mglia.constants import ALL_KD_GENES, CELL_MODELS
from mglia.schema import validate_all_records

FEATURED_KDS = ["ZNF532", "PRDM1", "STAT2", "DNMT1"]


def main() -> None:
    """Validate all records and write data/validation_report.txt."""
    records_path = ROOT / "data" / "perturbations.json"
    report_path = ROOT / "data" / "validation_report.txt"

    lines = []
    passed = True

    try:
        records = validate_all_records(str(records_path))
        lines.append(f"PASS: {len(records)} records loaded and schema-valid")
    except Exception as e:
        lines.append(f"FAIL: schema validation raised {type(e).__name__}: {e}")
        passed = False
        _write_report(report_path, lines, passed)
        raise

    expected_n = len(ALL_KD_GENES) * len(CELL_MODELS)
    if len(records) == expected_n:
        lines.append(f"PASS: expected {expected_n} records, got {len(records)}")
    else:
        lines.append(f"FAIL: expected {expected_n} records, got {len(records)}")
        passed = False

    present = {(r.perturbation, r.cell_model) for r in records}
    missing = [
        (g, m) for g in ALL_KD_GENES for m in CELL_MODELS if (g, m) not in present
    ]
    if not missing:
        lines.append("PASS: all genes present in both cell models")
    else:
        lines.append(f"FAIL: missing (gene, model) combinations: {missing}")
        passed = False
    featured_records = [r for r in records if r.perturbation in FEATURED_KDS]
    missing_functional = [
        f"{r.perturbation}/{r.cell_model}"
        for r in featured_records
        if not r.functional_readouts
    ]
    if not missing_functional:
        lines.append("PASS: functional readouts present for all featured KDs")
    else:
        lines.append(
            f"FAIL: featured KDs missing functional readouts: {missing_functional}"
        )
        passed = False

    out_of_range = []
    for r in records:
        signature_shift = r.prediction_targets.get("signature_shift", {})
        for state, shift in signature_shift.items():
            delta = shift.get("delta_pctl")
            if delta is not None and not (-100 <= delta <= 100):
                out_of_range.append(f"{r.perturbation}/{r.cell_model}/{state}={delta}")
    if not out_of_range:
        lines.append("PASS: all delta_pctl values within [-100, 100]")
    else:
        lines.append(f"FAIL: delta_pctl values out of range: {out_of_range}")
        passed = False

    lines.append("")
    lines.append("OVERALL: " + ("PASS" if passed else "FAIL"))

    _write_report(report_path, lines, passed)


def _write_report(report_path: Path, lines: list[str], passed: bool) -> None:
    with open(report_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    for line in lines:
        print(line)
    if not passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
