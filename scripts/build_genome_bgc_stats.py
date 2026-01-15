from pathlib import Path
import csv
import argparse
import statistics
from collections import defaultdict

### arguments ###

parser = argparse.ArgumentParser(
    description="Build genome-level BGC statistics table"
)
parser.add_argument("--batch", required=True)
args = parser.parse_args()

### paths ###

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = PIPELINE_ROOT / "batches" / args.batch

INPUT_CSV = BATCH_DIR / "master_bgc_antismash.csv"
OUTPUT_CSV = BATCH_DIR / "genome_bgc_stats.csv"

### load bgc table ###

genome_lengths = defaultdict(list)
genome_types = defaultdict(set)

with open(INPUT_CSV, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        genome_id = row["genome_id"]
        length = int(row["bgc_length_bp"])
        bgc_type = row["bgc_type"]

        genome_lengths[genome_id].append(length)
        genome_types[genome_id].add(bgc_type)

### write genome stats ###

with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "batch_id",
        "genome_id",
        "total_bgcs",
        "unique_bgc_types",
        "mean_bgc_length",
        "median_bgc_length",
        "min_bgc_length",
        "max_bgc_length"
    ])

    for genome_id, lengths in genome_lengths.items():
        writer.writerow([
            args.batch,
            genome_id,
            len(lengths),
            len(genome_types[genome_id]),
            round(statistics.mean(lengths), 2),
            round(statistics.median(lengths), 2),
            min(lengths),
            max(lengths)
        ])

print(f"Genome-level stats written to {OUTPUT_CSV}")
