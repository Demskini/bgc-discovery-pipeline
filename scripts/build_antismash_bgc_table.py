from pathlib import Path
import csv
import argparse
from Bio import SeqIO

### arguments ###

parser = argparse.ArgumentParser(
    description="Build master BGC table from antiSMASH outputs"
)
parser.add_argument("--batch", required=True)
args = parser.parse_args()

### paths ###

PIPELINE_ROOT = Path(__file__).resolve().parents[1]
BATCH_DIR = PIPELINE_ROOT / "batches" / args.batch
ANTISMASH_DIR = BATCH_DIR / "antismash"
OUTPUT_CSV = BATCH_DIR / "master_bgc_antismash.csv"

### collect rows ###

rows = []

for genome_dir in ANTISMASH_DIR.iterdir():
    if not genome_dir.is_dir():
        continue

    genome_id = genome_dir.name

    for gbk_file in genome_dir.glob("*.region*.gbk"):
        try:
            record = SeqIO.read(gbk_file, "genbank")
        except Exception:
            continue

        region_number = gbk_file.stem.split(".region")[-1]

        region_feature = next(
            (f for f in record.features if f.type == "region"),
            None
        )
        if region_feature is None:
            continue

        start = int(region_feature.location.start)
        end = int(region_feature.location.end)
        length = end - start

        bgc_type = ";".join(
            region_feature.qualifiers.get("product", ["unknown"])
        )

        bgc_id = f"{genome_id}|region{region_number}"

        rows.append([
            args.batch,
            genome_id,
            record.id,
            bgc_id,
            region_number,
            bgc_type,
            start,
            end,
            length,
            "antiSMASH"
        ])

### write output ###

with open(OUTPUT_CSV, "w", newline="") as f:
    writer = csv.writer(f)

    writer.writerow([
        "batch_id",
        "genome_id",
        "contig_id",
        "bgc_id",
        "region_number",
        "bgc_type",
        "bgc_start",
        "bgc_end",
        "bgc_length_bp",
        "source_tool"
    ])

    writer.writerows(rows)

print(f"{len(rows)} BGCs written to {OUTPUT_CSV}")