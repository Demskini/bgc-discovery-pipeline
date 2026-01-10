import subprocess
import sys
from pathlib import Path
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

test_lst = [0.3]

def run_batch(batch_name: str, bigscape_cutoffs: list):
    root = Path(__file__).resolve().parent.parent  # bgc_pipeline
    batch = root / "batches" / batch_name         # sets batch path

    input_dir = batch / "input"                   # sets input folder path
    antismash_dir = batch / "antismash"            # sets antismash folder path
    bigscape_dir = batch / "bigscape"              # sets bigscape folder path

    if not input_dir.exists():
        sys.exit(f"ERROR: Input directory not found: {input_dir}")

    genomes = list(input_dir.glob("*.fna")) + \
              list(input_dir.glob("*.fasta")) + \
              list(input_dir.glob("*.gbk"))

    if not genomes:
        sys.exit(f"ERROR: No genome files found in {input_dir}")

    ### RUN AntiSMASH per GENOME ###
    
    for genome in genomes:
        name = genome.stem
        genome_out = antismash_dir / name  # expected antismash output folder

        if genome_out.exists():
            print(f"~Skipping antiSMASH for {genome.name} (already exists)~")
            continue
        print(f"~Running antiSMASH on {genome.name}~")  # update status to user

        cmd = [
            "docker", "run", "--rm", "-it",
            "-v", f"{input_dir}:/input",
            "-v", f"{antismash_dir}:/output",
            "antismash/standalone",
            genome.name,
            "--genefinding-tool", "prodigal",
            "--output-dir", f"/output/{name}"
        ]

        subprocess.run(cmd, check=True)

        print(f"~Finished {genome.name}~\n")  # update status to user

  ### RUN BiG-SCAPE once per BATCH ###
  
    bigscape_dir.mkdir(exist_ok=True)  # make sure bigscape folder exists

    for cutoff in bigscape_cutoffs:
        cutoff_dir = bigscape_dir / f"cutoff_{cutoff}"
        cutoff_dir.mkdir(exist_ok=True)  # one folder per cutoff

        print(f"~Running BiG-SCAPE at cutoff {cutoff}~")  # update status to user

        bigscape_cmd = [
            "docker", "run", "--rm",
            "--platform", "linux/amd64",
            "-v", f"{antismash_dir}:/input",
            "-v", f"{cutoff_dir}:/output",
            "-v", f"{root / 'pfam'}:/pfam",
            "-w", "/input",
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

        result = subprocess.run(
        bigscape_cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        # Known BiG-SCAPE HTML template bug
        if "html_template" in result.stderr:
            print("BiG-SCAPE completed without HTML output.")
        else:
            print("BiG-SCAPE failed with unexpected error:")
            print(result.stderr)
            raise RuntimeError("BiG-SCAPE failed")
    else:
        print(f"~Finished BiG-SCAPE cutoff {cutoff}~\n")  # update status to user

    print(f"Batch {batch_name} complete.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python run_batch.py <batch_name>")

    run_batch(sys.argv[1])
