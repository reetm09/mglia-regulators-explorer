"""Dataset nutrition label page."""

import json

import streamlit as st
from mglia.constants import GLOSSARY_BLURBS
from mglia.nutrition import load_nutrition_label
from mglia.qc_report import (
    build_qc_dataframe,
    build_summary_counts,
    render_cell_count_panel,
    render_confidence_scatter_panel,
    render_deg_counts_panel,
    render_functional_coverage_panel,
    render_mixscale_panel,
)
from mglia.records import load_all_records
from mglia.ui_components import render_global_styles, render_nutrition_label

render_global_styles()

st.title("Dataset Nutrition")

with st.expander("How to read this"):
    st.markdown(GLOSSARY_BLURBS["nutrition_label"])

st.subheader("Overall Summary")
try:
    label = load_nutrition_label()
except FileNotFoundError:
    st.error(
        "data/nutrition_label.json not found. Run `python scripts/generate_nutrition.py` "
        "to generate it."
    )
    st.stop()

render_nutrition_label(label)

st.markdown("---")

st.subheader("Nutrition Report")

qc_records = load_all_records()
qc_df = build_qc_dataframe(qc_records)
qc_summary = build_summary_counts(qc_df)

st.markdown("**Overview**")
summary_col1, summary_col2 = st.columns(2)
with summary_col1:
    st.metric("Total records", qc_summary["n_records"])
with summary_col2:
    for tier in ("high", "moderate", "low"):
        st.metric(f"Confidence: {tier}", qc_summary["by_confidence"].get(tier, 0))
# "Records with >=1 warning flag" and split:train/split:test metrics removed from
# display for now — data still available in qc_summary above.
# st.metric("Records with >=1 warning flag", qc_summary["n_with_warnings"])
# for split in ("train", "test"):
#     st.metric(f"Split: {split}", qc_summary["by_split"].get(split, 0))

st.plotly_chart(
    render_cell_count_panel(qc_df),
    width="stretch",
    config={"displaylogo": False},
    theme=None,
)
st.plotly_chart(
    render_confidence_scatter_panel(qc_df),
    width="stretch",
    config={"displaylogo": False},
    theme=None,
)
st.plotly_chart(
    render_deg_counts_panel(qc_df),
    width="stretch",
    config={"displaylogo": False},
    theme=None,
)
st.plotly_chart(
    render_mixscale_panel(qc_df),
    width="stretch",
    config={"displaylogo": False},
    theme=None,
)
st.plotly_chart(
    render_functional_coverage_panel(qc_df),
    width="stretch",
    config={"displaylogo": False},
    theme=None,
)

st.markdown("---")

st.download_button(
    label="Download nutrition_label.json",
    data=json.dumps(label, indent=2),
    file_name="nutrition_label.json",
    mime="application/json",
)
