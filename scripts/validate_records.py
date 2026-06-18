"""Validate perturbations.json against schema and cross-field constraints.

Standalone script — not a pytest test. Writes a report to data/validation_report.txt.

Usage:
    python scripts/validate_records.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def main() -> None:
    """Validate all records and write data/validation_report.txt."""
    # TODO: implement
    # 1. Load perturbations.json
    # 2. validate_all_records()
    # 3. Check: no test gene appears in any train computation
    # 4. Check: all 31 genes present in both models (62 records total)
    # 5. Check: functional readouts present for ZNF532, PRDM1, STAT2, DNMT1
    # 6. Check: all delta_pctl values within [-100, 100]
    # 7. Print pass/fail summary
    # 8. Write data/validation_report.txt
    raise NotImplementedError


if __name__ == "__main__":
    main()
