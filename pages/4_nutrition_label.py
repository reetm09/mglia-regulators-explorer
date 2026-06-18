"""Dataset nutrition label page."""

import streamlit as st

st.title("Dataset Nutrition Label")

with st.expander("How to read this"):
    st.markdown(
        "The nutrition label is auto-generated from the perturbation records. "
        "Green indicates a healthy metric, yellow is a caution, and red flags a known limitation. "
        "Values update when records are regenerated with `make generate`."
    )

# ---------------------------------------------------------------------------
# Four metric card sections in 2×2 grid
# ---------------------------------------------------------------------------

# TODO: label = load_nutrition_label()  # from data/nutrition_label.json

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Coverage")
    # TODO: render key-value rows with colored indicators

with col2:
    st.markdown("### Perturbation quality")
    # TODO: render key-value rows

col3, col4 = st.columns(2)

with col3:
    st.markdown("### Known limitations")
    # TODO: render key-value rows

with col4:
    st.markdown("### Benchmark readiness")
    # TODO: render key-value rows

st.markdown("---")

st.download_button(
    label="Download nutrition_label.json",
    data="{}",  # TODO: real file
    file_name="nutrition_label.json",
    mime="application/json",
    disabled=True,
)

st.caption(
    "This label is auto-generated from the perturbation records. "
    "Values update when records are regenerated."
)
