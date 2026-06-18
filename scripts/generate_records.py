"""Generate perturbations.json from h5mu files.

Loads both MuData files, iterates over all 31 KD genes × 2 models,
computes or extracts all record fields, validates against schema,
and writes data/perturbations.json.

Usage:
    python scripts/generate_records.py
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def main() -> None:
    """Build perturbations.json from raw h5mu data."""
    # TODO: implement
    # 1. Load both MuData files via loader.load_mdata()
    # 2. For each gene in ALL_KD_GENES × CELL_MODELS:
    #    a. compute_signature_shifts()
    #    b. compute_deg_list(top_n=50)
    #    c. get_schpf_factors() → top increased/decreased
    #    d. get cell count from adata.n_obs
    #    e. KD_EFFICIENCY.get(gene)
    #    f. audit_record()
    #    g. Hard-code functional readouts from FUNCTIONAL_ASSAYS
    #    h. Hard-code discordances from paper
    #    i. benchmark_split = "test" if gene in TEST_SET_GENES else "train"
    #    j. Hard-code orthogonal_validations and paper_figures
    # 3. validate_all_records()
    # 4. Write to data/perturbations.json
    # 5. Print summary
    raise NotImplementedError


if __name__ == "__main__":
    main()
