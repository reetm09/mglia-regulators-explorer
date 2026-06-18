"""Generate data/nutrition_label.json from perturbations.json.

Usage:
    python scripts/generate_nutrition.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def main() -> None:
    """Compute and export nutrition_label.json."""
    # TODO: implement
    # 1. compute_nutrition_label("data/perturbations.json")
    # 2. export_nutrition_label(label, "data/nutrition_label.json")
    # 3. Print summary
    raise NotImplementedError


if __name__ == "__main__":
    main()
