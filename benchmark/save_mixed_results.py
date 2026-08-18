import csv
from pathlib import Path


RESULT_FILE = Path("results/cognodb_mixed_results.csv")

RESULTS = [
    {
        "database": "CognoDB",
        "concurrency": 1,
        "duration_seconds": 30.22,
        "reads": 87,
        "writes": 24,
        "errors": 0,
        "total_operations": 111,
        "qps": 3.67,
    },
    {
        "database": "CognoDB",
        "concurrency": 10,
        "duration_seconds": 30.28,
        "reads": 737,
        "writes": 334,
        "errors": 0,
        "total_operations": 1071,
        "qps": 35.37,
    },
    {
        "database": "CognoDB",
        "concurrency": 40,
        "duration_seconds": 30.33,
        "reads": 2722,
        "writes": 1267,
        "errors": 6,
        "total_operations": 3989,
        "qps": 131.50,
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

    print(f"Saved results to {RESULT_FILE}")


if __name__ == "__main__":
    main()