import streamlit as st
import shutil
from pathlib import Path
from scripts.run_batch import run_batch, check_docker, fasta_txt_check

repo_root = Path(__file__).resolve().parent

st.title("BGC Discovery Pipeline")

### status log ###
if "status_log" not in st.session_state:
    st.session_state["status_log"] = []

### session state messages ###

if "batch_created" in st.session_state:
    st.success(
        f"Batch '{st.session_state['batch_created']}' created successfully."
    )
    del st.session_state["batch_created"]
    
### batch uploading ###

st.subheader("Create a new batch")

with st.form("create_batch_form", clear_on_submit=True):

    new_batch_name = st.text_input(
        "Batch name",
        placeholder="e.g. ecoli_test_batch",
        key="create_batch_name"
    )

    uploaded_files = st.file_uploader(
        "Upload genome files. [fna / fasta / gbk / txt]",
        type=["fna", "fasta", "gbk", "txt"],
        accept_multiple_files=True,
        key="create_batch_files"
    )

    submitted = st.form_submit_button("Create Batch")

# name validation
batch_name_valid = bool(new_batch_name)
files_valid = bool(uploaded_files)

invalid_chars = r'\/:*?"<>|'
has_invalid_chars = (
    any(c in new_batch_name for c in invalid_chars)
    if new_batch_name else False
)

batch_dir = repo_root / "batches" / new_batch_name if new_batch_name else None
batch_exists = batch_dir.exists() if batch_dir else False

ready_to_create = (
    submitted
    and batch_name_valid
    and files_valid
    and not has_invalid_chars
    and not batch_exists
)

# feedback on error
if submitted and has_invalid_chars:
    st.error(r'Batch name contains invalid characters: \ / : * ? " < > |')

if (
    submitted
    and batch_exists
    and st.session_state.get("batch_created") != new_batch_name
):
    st.info(f"Batch '{new_batch_name}' already exists.")

### button creation ###
if ready_to_create:

    # validation tests
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith(".txt"):
            if not fasta_txt_check(uploaded_file.getvalue()):
                st.error(
                    f"{uploaded_file.name} does not look like a FASTA file."
                )
                st.stop()

    # save dir only if validation tests passes
    input_dir = batch_dir / "input"
    input_dir.mkdir(parents=True)

    # write the files
    for uploaded_file in uploaded_files:
        file_path = input_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

    # pass parameters and update session state
    st.session_state["batch_created"] = new_batch_name
    st.rerun()

### batch selection ###


batches_dir = repo_root / "batches"

batches = [b.name for b in batches_dir.iterdir() if b.is_dir()]

batch = st.selectbox("Select batch", batches)

### delete batch ###

st.subheader("Delete batch")

st.warning(
    "Deleting a batch will permanently remove all associated input files, "
    "antiSMASH results, and BiG-SCAPE outputs."
)

with st.form("delete_batch_form", clear_on_submit=True):

    confirm_text = st.text_input(
        "Type 'confirm' to permanently delete the selected batch",
        placeholder="...",
        key="delete_confirm"
    )

    submitted = st.form_submit_button("Delete Batch")

delete_disabled = confirm_text != "confirm"

if submitted and delete_disabled:
    st.error("You must type 'confirm' to delete this batch.")

if submitted and not delete_disabled:

    batch_dir = repo_root / "batches" / batch

    if batch_dir.exists():
        shutil.rmtree(batch_dir)

        # store message across rerun
        st.session_state["batch_deleted"] = batch
        st.rerun()
    else:
        st.error("Batch directory not found.")

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

status_box = st.empty()

def stream_status(msg: str):
    """
    Receive status updates from run_batch and display them live in Streamlit.
    """
    st.session_state["status_log"].append(msg)
    status_box.write("\n".join(st.session_state["status_log"]))

if st.button("Run Pipeline"):

    # clear previous run messages
    st.session_state["status_log"] = []

    # check Docker availability
    try:
        check_docker()
    except RuntimeError as e:
        status_box.error(str(e))
        st.stop()

    # validate user input
    if not bigscape_cutoffs:
        status_box.error("Select at least one BiG-SCAPE cutoff.")
        st.stop()

    mibig_status = "including MIBiG" if use_mibig else "excluding MIBiG"
    status_box.info(
        f"Running batch `{batch}` with cutoffs {bigscape_cutoffs} "
        f"{mibig_status}."
    )

    # run pipeline with live progress updates
    with st.spinner("Pipeline running… this may take a while."):
        run_batch(
            batch,
            bigscape_cutoffs,
            use_mibig,
            status_callback=stream_status
        )

    status_box.success("Pipeline finished successfully.")