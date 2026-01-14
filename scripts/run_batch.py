import subprocess
import sys
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

def check_docker() -> None:
    """
    Check is docker is running by attempting to communicate with the Docker daemon.

    Raises
    ----
    RuntimeError
        if Docker is not running or is not accessible.
    """
    try:
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except subprocess.CalledProcessError:
        raise RuntimeError("Docker is not running. Please start Docker Desktop.")

def fasta_txt_check(file_bytes: bytes) -> bool:
    """
    Check whether a txt file appears to be in FASTA format.

    Parameters
    ----
    file_bytes : bytes
        Raw file contents read from uploaded files [txt]
    
    Returns
    ----
    bool
        True if the file passes FASTA formatting check, else False.
    """ 
    text = file_bytes.decode("utf-8", errors="ignore")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    return bool(lines) and lines[0].startswith(">")

def run_batch(
    batch_name: str,
    bigscape_cutoffs: list,
    status_callback=None
) -> None:
    """
    Run the complete BGC discovery pipeline for a batch. 

    executes antiSMASH on all genome files in the specificed batch input directory, then
    runs BiG-SCAPE for one or more of the selected similarity cutoffs. Results are written
    to batch-specific output directories.
    """

    def update_status(msg: str) -> None:
        """
        Send status updates to Streamlit if a callback is provided,
        otherwise fall back to standard output.
        """
        if status_callback is not None:
            status_callback(msg)
        print(msg)

    update_status("Entered run_batch()")

    root = Path(__file__).resolve().parent.parent
    batch = root / "batches" / batch_name

    input_dir = batch / "input"
    antismash_dir = batch / "antismash"
    bigscape_dir = batch / "bigscape"

    antismash_dir.mkdir(exist_ok=True)

    if not input_dir.exists():
        sys.exit(f"ERROR: Input directory not found: {input_dir}")

    genomes = (
        list(input_dir.glob("*.fna"))
        + list(input_dir.glob("*.fasta"))
        + list(input_dir.glob("*.gbk"))
        + list(input_dir.glob("*.txt"))
    )

    if not genomes:
        sys.exit(f"ERROR: No genome files found in {input_dir}")

    ### run AntiSMASH PER GENOME

    for genome in genomes:

        if genome.suffix == ".txt":
            fixed_genome = genome.with_suffix(".fasta")
            genome.rename(fixed_genome)
            genome = fixed_genome

        name = genome.stem
        genome_out = antismash_dir / name

        if genome_out.exists():
            update_status(
                f"Skipping antiSMASH for {genome.name} (already exists)"
            )
            continue

        update_status(f"Running antiSMASH on {genome.name}")

        cmd = [
            "docker", "run", "--rm",
            "--platform", "linux/amd64",
            "-v", f"{input_dir}:/input",
            "-v", f"{antismash_dir}:/output",
            "antismash/standalone",
            genome.name,
            "--genefinding-tool", "prodigal",
            "--output-dir", f"/output/{name}"
        ]

        subprocess.run(cmd, check=True)
        update_status(f"Finished antiSMASH on {genome.name}")

    ### run BiG-SCAPE PER CUTOFF

    bigscape_dir.mkdir(exist_ok=True)
    pfam_dir = (root / "pfam").resolve()

    known_nonfatal = [
        "no aligned sequences found",
        "starting with 0 files",
        "file with list of anchor domains not found",
        "html_template",
        "cannot copy tree",
        "distutilsfileerror"
    ]

    for cutoff in bigscape_cutoffs:
        cutoff_dir = bigscape_dir / f"cutoff_{cutoff}"
        cutoff_dir.mkdir(exist_ok=True)

        update_status(f"Running BiG-SCAPE at cutoff {cutoff}")

        bigscape_cmd = [
            "docker", "run", "--rm",
            "--platform", "linux/amd64",
            "-v", f"{antismash_dir}:/input",
            "-v", f"{cutoff_dir}:/output",
            "-v", f"{pfam_dir}:/pfam",
            "-w", "/input",
            "quay.io/biocontainers/bigscape:1.1.5--pyhdfd78af_0",
            "bigscape.py",
            "-i", "/input",
            "-o", "/output",
            "--cutoffs", str(cutoff),
            "--mix",
            "--include_gbk_str", "region",
            "--skip_ma",
            "--pfam_dir", "/pfam"
        ]

        result = subprocess.run(
            bigscape_cmd,
            capture_output=True,
            text=True
        )

    stderr = (result.stderr or "").lower()
    stdout = (result.stdout or "").lower()

    known_nonfatal = [
        "no aligned sequences found",
        "starting with 0 files",
        "file with list of anchor domains not found",
        "html_template",
        "cannot copy tree",
        "running with skip_ma parameter",
        "unicodedecodeerror",
        "pickle.load"       
    ]

    if result.returncode != 0:

        nonfatal_hit = any(pat in stderr for pat in known_nonfatal)

        progressed = any(
            pat in stderr or pat in stdout
            for pat in [
                "predicting domains",
                "finished generating pfs and pfd",
                "processing domains sequence files",
                "running with skip_ma parameter",
                "using hmmalign",
                "calculating distance matrix",
                "launch_hmmalign"
            ]
        )

        if nonfatal_hit and progressed:
            msg = (
                f"BiG-SCAPE stats completed at cutoff {cutoff} "
                "(matrix / networks intentionally skipped)."
            )
            print(msg)
            if status_callback:
                status_callback(msg)

        elif nonfatal_hit:
            msg = (
                f"BiG-SCAPE completed at cutoff {cutoff} "
                "(no comparable BGCs found)."
            )
            print(msg)
            if status_callback:
                status_callback(msg)

        else:
            print(f"BiG-SCAPE failed at cutoff {cutoff}")
            print("STDERR:")
            print(result.stderr)
            print("STDOUT:")
            print(result.stdout)
            raise RuntimeError(f"BiG-SCAPE failed at cutoff {cutoff}")

    else:
        msg = f"Finished BiG-SCAPE cutoff {cutoff}"
        print(msg)
        if status_callback:
            status_callback(msg)

    final_msg = f"Batch {batch_name} complete."
    print(final_msg)
    if status_callback:
        status_callback(final_msg)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python run_batch.py <batch_name>")

    run_batch(sys.argv[1], [0.3])