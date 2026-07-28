"""Generate data/nutrition_label.json from perturbations.json.

Usage:
    python scripts/generate_nutrition.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from mglia.nutrition import (
    compute_nutrition_label,
    export_nutrition_label,
)


def main() -> None:
    """Compute and export nutrition_label.json."""
    records_path = ROOT / "data" / "perturbations.json"
    out_path = ROOT / "data" / "nutrition_label.json"

    label = compute_nutrition_label(
        str(records_path), sections_to_include=["coverage", "perturbation_quality"]
    )
    export_nutrition_label(label, str(out_path))

    coverage = label["coverage"]
    print(f"Wrote nutrition label to {out_path}")
    print(f"  total KDs: {coverage['total_kds']}")
    print(f"  n states profiled: {coverage['states_profiled']}")


if __name__ == "__main__":
    main()
