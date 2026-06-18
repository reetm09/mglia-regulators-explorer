"""Benchmark tasks page — for ML / virtual cell researchers."""

import streamlit as st

st.title("Benchmark")

# ---------------------------------------------------------------------------
# Task overview — 2×2 grid
# ---------------------------------------------------------------------------

st.subheader("Tasks")

task_cols = st.columns(2)

TASK_NAMES = [
    "perturbation_prediction",
    "cross_model_generalization",
    "dose_response",
    "multistate_combinatorial",
]

for i, task in enumerate(TASK_NAMES):
    with task_cols[i % 2]:
        with st.expander(task.replace("_", " ").title(), expanded=False):
            st.markdown("**Description:** TODO")
            st.markdown("**Train / test:** TODO")
            st.markdown("**Primary metric:** TODO")
            # TODO: show full spec from benchmark.get_split(task)

# ---------------------------------------------------------------------------
# Null baselines
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Null baselines")
st.caption("Your model should beat these to be meaningful.")

# TODO: baseline_df = pd.DataFrame(...)
# TODO: st.dataframe(baseline_df, use_container_width=True, hide_index=True)

# ---------------------------------------------------------------------------
# Score your model
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Score your model")

task_sel = st.selectbox("Select task", options=TASK_NAMES)
uploaded = st.file_uploader("Upload predictions (CSV or JSON)", type=["csv", "json"])

if uploaded is not None:
    with st.spinner("Scoring predictions..."):
        pass  # TODO: validate + score_predictions()

# ---------------------------------------------------------------------------
# Data download
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Downloads & code")

st.download_button(
    label="Download benchmark_splits.json",
    data="{}",  # TODO: real file
    file_name="benchmark_splits.json",
    mime="application/json",
    disabled=True,
)

st.code(
    """\
from mglia import get_split, load_split_data, score_predictions

split = get_split("perturbation_prediction")
train_data = load_split_data("perturbation_prediction", "train")
# ... train your model ...
scores = score_predictions(predictions, "perturbation_prediction")
""",
    language="python",
)
