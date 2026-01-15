from pathlib import Path
import csv
import argparse

parser = argparse.ArgumentParser(
    description="Build per-BGC catalog with genome, region, and type"
)
parser.add_argument("--batch", required=True)
args = parser.parse_args()

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = PIPELINE_ROOT / "batches" / args.batch

INPUT_CSV = BATCH_DIR / "master_bgc_antismash.csv"
OUTPUT_CSV = BATCH_DIR / "bgc_catalog.csv"

rows = []

with open(INPUT_CSV, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        rows.append([
            row["batch_id"],
            row["genome_id"],
            row["contig_id"],
            row["bgc_id"],
            row["region_number"],
            row["bgc_type"],
            row["bgc_length_bp"],
            row["bgc_start"],
            row["bgc_end"],
        ])

with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "batch_id",
        "genome_id",
        "contig_id",
        "bgc_id",
        "region_number",
        "bgc_type",
        "bgc_length_bp",
        "bgc_start",
        "bgc_end",
    ])
    writer.writerows(rows)

print(f"{len(rows)} BGCs written to {OUTPUT_CSV}")
