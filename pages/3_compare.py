"""Compare Perturbations"""

import streamlit as st
from mglia import records
from mglia.constants import (
    COLOR_DANGER,
    COLOR_SUCCESS,
    FUNCTIONAL_ASSAY_NAMES,
    GENE_A_COLOR,
    GENE_B_COLOR,
    STATES,
)
from mglia.ui_components import (
    render_functional_card,
    render_global_styles,
    render_method_assumptions,
    render_multistate_heatmap,
    render_signature_bars,
)

render_global_styles()

st.title("Compare Perturbations")

# ---------------------------------------------------------------------------
# Gene selectors
# ---------------------------------------------------------------------------

genes = records.list_genes()
default_a = genes.index("ZNF532") if "ZNF532" in genes else 0
default_b = genes.index("PRDM1") if "PRDM1" in genes else min(1, len(genes) - 1)

col_a, col_b, col_m = st.columns([2, 2, 1])

with col_a:
    gene_a = st.selectbox("Gene A", options=genes, index=default_a, key="gene_a")

with col_b:
    gene_b = st.selectbox("Gene B", options=genes, index=default_b, key="gene_b")

with col_m:
    model = st.radio("Model", options=["iTF-MG", "iMG"], horizontal=False)

record_a = records.get_record(gene_a, model)
record_b = records.get_record(gene_b, model)

if record_a is None or record_b is None:
    missing = gene_a if record_a is None else gene_b
    st.error(f"No record found for {missing} in {model}.")
    st.stop()

# ---------------------------------------------------------------------------
# Signature shift comparison
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Microglia State Signature Shifts")

reliable_states = [k for k, meta in STATES.items() if meta["reliable"]]
shifts_a = record_a.prediction_targets["signature_shift"]
shifts_b = record_b.prediction_targets["signature_shift"]
shared_range = max(
    1.0,
    max(abs(shifts_a[k]["delta_pctl"]) for k in shifts_a) * 1.3,
    max(abs(shifts_b[k]["delta_pctl"]) for k in shifts_b) * 1.3,
)

col_left, col_right = st.columns(2)

with col_left:
    st.markdown(f"**{gene_a}**")
    fig_a = render_signature_bars(
        shifts_a, reliable_states, x_range=shared_range, height=320
    )
    st.plotly_chart(fig_a, config={"displaylogo": False}, width="stretch", theme=None)

with col_right:
    st.markdown(f"**{gene_b}**")
    fig_b = render_signature_bars(
        shifts_b, reliable_states, x_range=shared_range, height=320
    )
    st.plotly_chart(fig_b, config={"displaylogo": False}, width="stretch", theme=None)

st.markdown("**State Agreement**")
agreement_states = [
    (state_key, meta)
    for state_key, meta in STATES.items()
    if state_key in shifts_a and state_key in shifts_b
]
agreement_cols = st.columns(len(agreement_states))
for col, (state_key, meta) in zip(agreement_cols, agreement_states):
    sign_a = shifts_a[state_key]["delta_pctl"] >= 0
    sign_b = shifts_b[state_key]["delta_pctl"] >= 0
    if sign_a == sign_b:
        symbol = "↑↑" if sign_a else "↓↓"
        color = COLOR_SUCCESS
    else:
        symbol = "↑↓" if sign_a else "↓↑"
        color = COLOR_DANGER
    with col:
        st.markdown(
            f"<div style='text-align:center;'>"
            f"<span style='color:{color};font-weight:600;font-size:1.2em;'>{symbol}</span><br>"
            f"<span style='font-size:0.85em;'>{meta['display']}</span></div>",
            unsafe_allow_html=True,
        )

# ---------------------------------------------------------------------------
# Method assumptions & caveats comparison
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Method assumptions & caveats")

col_aud_a, col_aud_b = st.columns(2)

with col_aud_a:
    st.markdown(f"**{gene_a}**")
    render_method_assumptions(record_a)

with col_aud_b:
    st.markdown(f"**{gene_b}**")
    render_method_assumptions(record_b)

# ---------------------------------------------------------------------------
# Functional readouts comparison
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Functional readouts")
col_fn_a, col_fn_b = st.columns(2)
with col_fn_a:
    st.markdown(f"**{gene_a}**")
    readouts_a = record_a.functional_readouts
    for assay_id, assay_name in FUNCTIONAL_ASSAY_NAMES.items():
        render_functional_card(assay_name, readouts_a.get(assay_id))
with col_fn_b:
    st.markdown(f"**{gene_b}**")
    readouts_b = record_b.functional_readouts
    for assay_id, assay_name in FUNCTIONAL_ASSAY_NAMES.items():
        render_functional_card(assay_name, readouts_b.get(assay_id))

# ---------------------------------------------------------------------------
# ZNF532 vs PRDM1 narrative callout
# ---------------------------------------------------------------------------

if {gene_a, gene_b} == {"ZNF532", "PRDM1"} and model == "iMG":
    st.info(
        "Both ZNF532 and PRDM1 drive DAM up and phagocytosis up. But ZNF532 drives "
        "antigen-presenting **down** while PRDM1 drives it **up**. Same functional outcome, "
        "different state combinations. This supports modular, not monolithic, state regulation."
    )

# ---------------------------------------------------------------------------
# Multi-state heatmap overview
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("All knockdowns: Microglia State Signature Heatmap")
# st.caption("Click a row to navigate to that gene in the Explorer.")

highlight_genes = {gene_a: GENE_A_COLOR, gene_b: GENE_B_COLOR}
st.markdown(
    f"<span style='color:{GENE_A_COLOR};font-weight:600;'>■ {gene_a}</span>"
    f"&nbsp;&nbsp;&nbsp;"
    f"<span style='color:{GENE_B_COLOR};font-weight:600;'>■ {gene_b}</span>",
    unsafe_allow_html=True,
)

all_records = records.load_all_records()
col_itf, col_img = st.columns(2)

for col, model_name in [(col_itf, "iTF-MG"), (col_img, "iMG")]:
    with col:
        st.markdown(f"**{model_name}**")
        heatmap_fig = render_multistate_heatmap(
            all_records, model_name, highlight_genes=highlight_genes
        )
        selection = st.plotly_chart(
            heatmap_fig,
            config={"displaylogo": False},
            width="stretch",
            theme=None,
            on_select="rerun",
            key=f"compare_heatmap_{model_name}",
        )
        if selection and selection.get("selection", {}).get("points"):
            point = selection["selection"]["points"][0]
            selected_gene = point.get("y")
            if selected_gene:
                st.session_state["explore_gene"] = selected_gene
                st.switch_page("pages/1_explore.py")

st.caption("For significance values, refer to Figure 2D in paper.")
