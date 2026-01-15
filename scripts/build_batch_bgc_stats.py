from pathlib import Path
import csv
import argparse
import statistics
from collections import defaultdict

parser = argparse.ArgumentParser(
    description="Build batch-level BGC statistics"
)
parser.add_argument("--batch", required=True)
args = parser.parse_args()

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = PIPELINE_ROOT / "batches" / args.batch

INPUT_CSV = BATCH_DIR / "master_bgc_antismash.csv"
OUTPUT_CSV = BATCH_DIR / "batch_bgc_stats.csv"

genome_bgcs = defaultdict(int)
bgc_lengths = []
bgc_types = set()

with open(INPUT_CSV, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        genome_id = row["genome_id"]
        genome_bgcs[genome_id] += 1
        bgc_lengths.append(int(row["bgc_length_bp"]))
        bgc_types.add(row["bgc_type"])

total_genomes = len(genome_bgcs)
total_bgcs = sum(genome_bgcs.values())
bgcs_per_genome = list(genome_bgcs.values())

with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "batch_id",
        "total_genomes",
        "total_bgcs",
        "mean_bgcs_per_genome",
        "median_bgcs_per_genome",
        "unique_bgc_types",
        "mean_bgc_length"
    ])
    writer.writerow([
        args.batch,
        total_genomes,
        total_bgcs,
        round(statistics.mean(bgcs_per_genome), 2),
        round(statistics.median(bgcs_per_genome), 2),
        len(bgc_types),
        round(statistics.mean(bgc_lengths), 2)
    ])

print(f"Batch-level stats written to {OUTPUT_CSV}")
