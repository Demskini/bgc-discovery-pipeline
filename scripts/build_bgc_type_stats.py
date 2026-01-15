from pathlib import Path
import csv
import argparse
from collections import defaultdict

parser = argparse.ArgumentParser(
    description="Build BGC type frequency table"
)
parser.add_argument("--batch", required=True)
args = parser.parse_args()

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = PIPELINE_ROOT / "batches" / args.batch

INPUT_CSV = BATCH_DIR / "master_bgc_antismash.csv"
OUTPUT_CSV = BATCH_DIR / "bgc_type_stats.csv"

type_counts = defaultdict(int)

with open(INPUT_CSV, newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        bgc_type = row["bgc_type"]
        for t in bgc_type.split(";"):
            type_counts[t.strip()] += 1

with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "batch_id",
        "bgc_type",
        "count"
    ])
    for bgc_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        writer.writerow([
            args.batch,
            bgc_type,
            count
        ])

print(f"BGC type stats written to {OUTPUT_CSV}")
