"""Side-by-side KD comparison page."""

import streamlit as st

st.title("Compare Knockdowns")

# ---------------------------------------------------------------------------
# Gene selectors
# ---------------------------------------------------------------------------

col_a, col_b, col_m = st.columns([2, 2, 1])

with col_a:
    gene_a = st.selectbox("Gene A", options=[], index=0, key="gene_a")  # TODO: from constants

with col_b:
    gene_b = st.selectbox("Gene B", options=[], index=1, key="gene_b")  # TODO: from constants

with col_m:
    model = st.radio("Model", options=["iTF-MG", "iMG"], horizontal=False)

# ---------------------------------------------------------------------------
# Signature shift comparison
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("State signature shifts")

col_left, col_mid, col_right = st.columns(3)

with col_left:
    st.markdown(f"**{gene_a}**")
    # TODO: render_signature_bars(shifts_a, reliable_states)

with col_mid:
    st.markdown("**Agreement**")
    # TODO: render agreement/opposition per state (↑↑ ↓↓ ↑↓)

with col_right:
    st.markdown(f"**{gene_b}**")
    # TODO: render_signature_bars(shifts_b, reliable_states)

# ---------------------------------------------------------------------------
# Assumption audit comparison
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("Assumption audit")

col_aud_a, col_aud_b = st.columns(2)

with col_aud_a:
    st.markdown(f"**{gene_a}**")
    # TODO: render_assumption_flags(record_a.assumption_audit)

with col_aud_b:
    st.markdown(f"**{gene_b}**")
    # TODO: render_assumption_flags(record_b.assumption_audit)

# ---------------------------------------------------------------------------
# Functional readouts comparison (featured KDs only)
# ---------------------------------------------------------------------------

FEATURED_KDS = ["ZNF532", "PRDM1", "STAT2", "DNMT1"]

if gene_a in FEATURED_KDS and gene_b in FEATURED_KDS:
    st.markdown("---")
    st.subheader("Functional readouts")
    col_fn_a, col_fn_b = st.columns(2)
    # TODO: render functional cards for both

# ---------------------------------------------------------------------------
# ZNF532 vs PRDM1 narrative callout
# ---------------------------------------------------------------------------

if set([gene_a, gene_b]) == {"ZNF532", "PRDM1"}:
    st.info(
        "Both ZNF532 and PRDM1 drive DAM up and phagocytosis up. But ZNF532 drives "
        "antigen-presenting **down** while PRDM1 drives it **up**. Same functional outcome, "
        "different state combinations. This supports modular, not monolithic, state regulation."
    )

# ---------------------------------------------------------------------------
# Multi-state heatmap overview
# ---------------------------------------------------------------------------

st.markdown("---")
st.subheader("All knockdowns — state heatmap")
st.caption("Click a row to navigate to that gene in the Explorer.")

# TODO: fig = render_multistate_heatmap(all_records, model)
# TODO: selected = st.plotly_chart(fig, config={"displaylogo": False}, on_select="rerun")
