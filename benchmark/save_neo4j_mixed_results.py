import csv
from pathlib import Path


RESULT_FILE = Path("results/neo4j_mixed_results.csv")


RESULTS = [
    {
        "database": "Neo4j",
        "concurrency": 1,
        "duration_seconds": 30.09,
        "reads": 348,
        "writes": 144,
        "errors": 0,
        "total_operations": 492,
        "qps": 16.35,
    },
    {
        "database": "Neo4j",
        "concurrency": 10,
        "duration_seconds": 30.10,
        "reads": 3117,
        "writes": 1312,
        "errors": 0,
        "total_operations": 4429,
        "qps": 147.15,
    },
    {
        "database": "Neo4j",
        "concurrency": 40,
        "duration_seconds": 30.26,
        "reads": 4251,
        "writes": 1885,
        "errors": 0,
        "total_operations": 6136,
        "qps": 202.76,
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
                "concurrency",
                "duration_seconds",
                "reads",
                "writes",
                "errors",
                "total_operations",
                "qps",
            ],
        )

        writer.writeheader()
        writer.writerows(RESULTS)

    print()
    print("=" * 50)
    print("Neo4j mixed workload results saved.")
    print("=" * 50)
    print()
    print("File:", RESULT_FILE)


if __name__ == "__main__":
    main()