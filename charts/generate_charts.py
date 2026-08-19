import csv
from pathlib import Path

import matplotlib.pyplot as plt


RESULTS_DIR = Path("results")
CHARTS_DIR = Path("charts")

READ_FILE = RESULTS_DIR / "read_comparison.csv"
MIXED_FILE = RESULTS_DIR / "mixed_comparison.csv"


def read_csv(file_path):
    with open(file_path, "r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def generate_read_chart():
    rows = read_csv(READ_FILE)

    workloads = []
    neo4j_p50 = []
    cognodb_p50 = []

    for row in rows:
        workloads.append(row["workload"])

        # Automatically detect column names
        neo4j_value = None
        cognodb_value = None

        for key, value in row.items():
            key_lower = key.lower()

            if "neo4j" in key_lower and "p50" in key_lower:
                neo4j_value = float(value)

            if "cognodb" in key_lower and "p50" in key_lower:
                cognodb_value = float(value)

        if neo4j_value is None or cognodb_value is None:
            print("Could not find expected columns.")
            print("Available columns:")
            print(row.keys())
            return

        neo4j_p50.append(neo4j_value)
        cognodb_p50.append(cognodb_value)

    x = range(len(workloads))

    plt.figure(figsize=(10, 6))

    plt.bar(
        [i - 0.2 for i in x],
        neo4j_p50,
        width=0.4,
        label="Neo4j"
    )

    plt.bar(
        [i + 0.2 for i in x],
        cognodb_p50,
        width=0.4,
        label="CognoDB"
    )

    plt.xticks(x, workloads, rotation=30, ha="right")

    plt.ylabel("P50 Latency (ms)")
    plt.xlabel("Workload")
    plt.title("Neo4j vs CognoDB Read Performance")
    plt.legend()

    plt.tight_layout()

    output = CHARTS_DIR / "read_performance_comparison.png"

    plt.savefig(output, dpi=300)
    plt.close()

    print(f"Created: {output}")


def generate_mixed_chart():
    rows = read_csv(MIXED_FILE)

    concurrency = []
    neo4j_qps = []
    cognodb_qps = []

    for row in rows:
        concurrency.append(int(row["concurrency"]))

        neo4j_value = None
        cognodb_value = None

        for key, value in row.items():
            key_lower = key.lower()

            if "neo4j" in key_lower and "qps" in key_lower:
                neo4j_value = float(value)

            if "cognodb" in key_lower and "qps" in key_lower:
                cognodb_value = float(value)

        if neo4j_value is None or cognodb_value is None:
            print("Could not find expected mixed-workload columns.")
            print("Available columns:")
            print(row.keys())
            return

        neo4j_qps.append(neo4j_value)
        cognodb_qps.append(cognodb_value)

    x = range(len(concurrency))

    plt.figure(figsize=(9, 6))

    plt.plot(
        concurrency,
        neo4j_qps,
        marker="o",
        label="Neo4j"
    )

    plt.plot(
        concurrency,
        cognodb_qps,
        marker="o",
        label="CognoDB"
    )

    plt.xlabel("Concurrency")
    plt.ylabel("Throughput (QPS)")
    plt.title("Neo4j vs CognoDB Mixed Workload Throughput")
    plt.legend()
    plt.grid(True)

    plt.tight_layout()

    output = CHARTS_DIR / "mixed_workload_comparison.png"

    plt.savefig(output, dpi=300)
    plt.close()

    print(f"Created: {output}")


def main():
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 50)
    print("Generating Benchmark Charts")
    print("=" * 50)

    print()

    if READ_FILE.exists():
        generate_read_chart()
    else:
        print(f"Missing file: {READ_FILE}")

    print()

    if MIXED_FILE.exists():
        generate_mixed_chart()
    else:
        print(f"Missing file: {MIXED_FILE}")

    print()
    print("=" * 50)
    print("Chart generation completed.")
    print("=" * 50)


if __name__ == "__main__":
    main()