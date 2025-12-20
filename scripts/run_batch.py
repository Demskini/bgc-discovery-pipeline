import subprocess
import sys
from pathlib import Path

def run_batch(batch_name: str):
    root = Path(__file__).resolve().parent.parent #bgc_pipeline
    batch = root / "batches" / batch_name #sets function batch path

    input_dir = batch / "input" #sets input folder path 
    antismash_dir = batch / "antismash" #set antismash folder path

    if not input_dir.exists():
        sys.exit(f"ERROR: Input directory not found: {input_dir}")

    genomes = list(input_dir.glob("*.fna")) + \
              list(input_dir.glob("*.fasta")) + \
              list(input_dir.glob("*.gbk"))

    if not genomes:
        sys.exit(f"ERROR: No genome files found in {input_dir}")

    for genome in genomes:
        name = genome.stem
        print(f"~Running antiSMASH on {genome.name}~") #update status to user

        #run docker command
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

        print(f"~Finished {genome.name}~\n") #update status to user

    print(f"Batch {batch_name} complete.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python run_batch.py <batch_name>")

    run_batch(sys.argv[1])
