import csv
from pathlib import Path


RESULT_FILE = Path("results/cognodb_read_results.csv")


RESULTS = [
    {
        "database": "CognoDB",
        "workload": "1-hop traversal",
        "p50_ms": 262.505,
        "p95_ms": 275.157,
    },
    {
        "database": "CognoDB",
        "workload": "2-hop traversal",
        "p50_ms": 261.896,
        "p95_ms": 271.985,
    },
    {
        "database": "CognoDB",
        "workload": "3-hop traversal",
        "p50_ms": 263.657,
        "p95_ms": 273.267,
    },
    {
        "database": "CognoDB",
        "workload": "Point lookup",
        "p50_ms": 263.328,
        "p95_ms": 278.196,
    },
    {
        "database": "CognoDB",
        "workload": "Indexed lookup",
        "p50_ms": 262.221,
        "p95_ms": 280.617,
    },
    {
        "database": "CognoDB",
        "workload": "Aggregation",
        "p50_ms": 255.528,
        "p95_ms": 265.470,
    },
]


def main():
    RESULT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with RESULT_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "database",
                "workload",
                "p50_ms",
                "p95_ms",
            ],
        )

        writer.writeheader()
        writer.writerows(RESULTS)

    print(f"Saved results to {RESULT_FILE}")


if __name__ == "__main__":
    main()