import gzip
from pathlib import Path

INPUT_FILE = Path("data/pokec-relationships.txt.gz")
OUTPUT_FILE = Path("data/pokec_sample.csv")

TARGET_RELATIONSHIPS = 120_000


def prepare_sample():
    relationships = []
    nodes = set()

    with gzip.open(INPUT_FILE, "rt", encoding="utf-8") as source:
        for line in source:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            parts = line.split()

            if len(parts) < 2:
                continue

            source_id = parts[0]
            target_id = parts[1]

            relationships.append((source_id, target_id))
            nodes.add(source_id)
            nodes.add(target_id)

            if len(relationships) >= TARGET_RELATIONSHIPS:
                break

    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as output:
        output.write("source_id,target_id\n")

        for source_id, target_id in relationships:
            output.write(f"{source_id},{target_id}\n")

    print(f"Relationships: {len(relationships):,}")
    print(f"Nodes: {len(nodes):,}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    prepare_sample()