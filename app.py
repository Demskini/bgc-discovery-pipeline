import streamlit as st
from pathlib import Path
from scripts.run_batch import run_batch, check_docker

st.title("BGC Discovery Pipeline")

### batch selection ###

repo_root = Path(__file__).resolve().parent
batches_dir = repo_root / "batches"

batches = [b.name for b in batches_dir.iterdir() if b.is_dir()]

batch = st.selectbox("Select batch", batches)

### MIBiG ###

st.subheader("BiG-SCAPE options")

use_mibig = st.checkbox("Include MIBiG reference clusters", value=True)

### bigscape cutoffs ###

st.subheader("BiG-SCAPE cutoffs")

cutoff_03 = st.checkbox("0.3", value=True)
cutoff_05 = st.checkbox("0.5", value=True)
cutoff_07 = st.checkbox("0.7", value=True)

bigscape_cutoffs = []
if cutoff_03:
    bigscape_cutoffs.append(0.3)
if cutoff_05:
    bigscape_cutoffs.append(0.5)
if cutoff_07:
    bigscape_cutoffs.append(0.7)


### run button ###

if st.button("Run Pipeline"):

    # Check Docker availability first
    try:
        check_docker()
    except RuntimeError as e:
        st.error(str(e))
        st.stop()

    # Validate user input
    if not bigscape_cutoffs:
        st.error("Select at least one BiG-SCAPE cutoff.")
        st.stop()

    # Status message
    mibig_status = "including MIBiG" if use_mibig else "excluding MIBiG"
    st.write(
        f"Running batch `{batch}` with cutoffs {bigscape_cutoffs} "
        f"{mibig_status}."
    )

    # Run the pipeline
    run_batch(batch, bigscape_cutoffs, use_mibig)

    # Success message
    st.success("Pipeline finished.")