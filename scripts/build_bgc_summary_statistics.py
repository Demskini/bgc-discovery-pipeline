from pathlib import Path
import csv
import argparse
import statistics
from collections import defaultdict

parser = argparse.ArgumentParser(description="Build statistical summary CSV for BGC pipeline")
parser.add_argument("--batch", required=True)
args = parser.parse_args()

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = PIPELINE_ROOT / "batches" / args.batch

INPUT_CSV = BATCH_DIR / "master_bgc_antismash.csv"
OUTPUT_CSV = BATCH_DIR / "bgc_summary_statistics.csv"

genome_bgcs = defaultdict(int)
bgc_lengths = []
bgc_types = set()

with open(INPUT_CSV, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        genome_id = row["genome_id"]
        genome_bgcs[genome_id] += 1
        bgc_lengths.append(int(row["bgc_length_bp"]))

        for bgc_type in row["bgc_type"].split(";"):
            bgc_types.add(bgc_type.strip())

bgcs_per_genome = list(genome_bgcs.values())

def safe_stdev(values):
    return round(statistics.stdev(values), 2) if len(values) > 1 else 0

rows = [
    [args.batch, "batch", "total_genomes", len(genome_bgcs)],
    [args.batch, "batch", "total_bgcs", sum(bgcs_per_genome)],
    [args.batch, "batch", "unique_bgc_types", len(bgc_types)],

    [args.batch, "bgcs_per_genome", "mean", round(statistics.mean(bgcs_per_genome), 2)],
    [args.batch, "bgcs_per_genome", "median", round(statistics.median(bgcs_per_genome), 2)],
    [args.batch, "bgcs_per_genome", "min", min(bgcs_per_genome)],
    [args.batch, "bgcs_per_genome", "max", max(bgcs_per_genome)],
    [args.batch, "bgcs_per_genome", "standard_deviation", safe_stdev(bgcs_per_genome)],

    [args.batch, "bgc_length_bp", "mean", round(statistics.mean(bgc_lengths), 2)],
    [args.batch, "bgc_length_bp", "median", round(statistics.median(bgc_lengths), 2)],
    [args.batch, "bgc_length_bp", "min", min(bgc_lengths)],
    [args.batch, "bgc_length_bp", "max", max(bgc_lengths)],
    [args.batch, "bgc_length_bp", "standard_deviation", safe_stdev(bgc_lengths)],
]

with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["batch_id", "level", "metric", "value"])
    writer.writerows(rows)

print(f"Summary statistics written to {OUTPUT_CSV}")