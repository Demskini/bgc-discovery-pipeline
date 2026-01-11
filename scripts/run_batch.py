import subprocess
import sys
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

def check_docker():
    """
    Input = none
    Output = Raise error
    Function that checks to see docker is running before attempting the run the batch. """
    try:
        subprocess.run(
            ["docker", "info"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True
        )
    except subprocess.CalledProcessError:
        raise RuntimeError("Docker is not running. Please start Docker Desktop.")
    
def run_batch(batch_name: str, bigscape_cutoffs: list, use_mibig: bool):
    root = Path(__file__).resolve().parent.parent
    batch = root / "batches" / batch_name

    input_dir = batch / "input"
    antismash_dir = batch / "antismash"
    bigscape_dir = batch / "bigscape"

    if not input_dir.exists():
        sys.exit(f"ERROR: Input directory not found: {input_dir}")

    genomes = (
        list(input_dir.glob("*.fna"))
        + list(input_dir.glob("*.fasta"))
        + list(input_dir.glob("*.gbk"))
    )

    if not genomes:
        sys.exit(f"ERROR: No genome files found in {input_dir}")

    ### RUN AntiSMASH PER GENOME

    for genome in genomes:
        name = genome.stem
        genome_out = antismash_dir / name

        if genome_out.exists():
            print(f"~Skipping antiSMASH for {genome.name} (already exists)~")
            continue

        print(f"~Running antiSMASH on {genome.name}~")

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
        print(f"~Finished {genome.name}~\n")

    ### RUN BiG-SCAPE PER CUTOFF

    bigscape_dir.mkdir(exist_ok=True)

    for cutoff in bigscape_cutoffs:
        cutoff_dir = bigscape_dir / f"cutoff_{cutoff}"
        cutoff_dir.mkdir(exist_ok=True)

        print(f"~Running BiG-SCAPE at cutoff {cutoff}~")

        bigscape_cmd = [
    "docker", "run", "--rm",
    "--platform", "linux/amd64",
    "-v", f"{antismash_dir}:/input",
    "-v", f"{cutoff_dir}:/output",
    "-v", f"{root / 'pfam'}:/pfam",
    "-w", "/input",
]

        # Only mount MIBiG if the checkbox is checked (streamlit)
        if use_mibig:
            bigscape_cmd += [
                "-v", f"{root / 'mibig'}:/mibig"
            ]

        bigscape_cmd += [
            "quay.io/biocontainers/bigscape:1.1.5--pyhdfd78af_0",
            "bigscape.py",
            "-i", "/input",
            "-o", "/output",
            "--cutoffs", str(cutoff),
            "--mix",
            "--include_singletons",
            "--include_gbk_str", "region",
            "--pfam_dir", "/pfam",
            "--no_classify"
        ]

        # Tell BiG-SCAPE where MIBiG is ONLY if mounted
        if use_mibig:
            bigscape_cmd += ["--mibig_dir", "/mibig"]



        result = subprocess.run(
            bigscape_cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            if "html_template" in result.stderr.lower():
                print(f"BiG-SCAPE finished at cutoff {cutoff} (HTML bug only).")
            else:
                print(f"BiG-SCAPE failed at cutoff {cutoff}")
                print("STDERR:")
                print(result.stderr)
                print("STDOUT:")
                print(result.stdout)
                raise RuntimeError(f"BiG-SCAPE failed at cutoff {cutoff}")
        else:
            print(f"~Finished BiG-SCAPE cutoff {cutoff}~\n")

    print(f"Batch {batch_name} complete.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python run_batch.py <batch_name>")

    # Example CLI defaults
    run_batch(sys.argv[1], [0.3], use_mibig=False)
