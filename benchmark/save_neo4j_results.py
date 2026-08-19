import csv
from pathlib import Path
import statistics


INPUT_FILE = Path("results/neo4j_workload_results.csv")
OUTPUT_FILE = Path("results/neo4j_benchmark_summary.csv")


def main():

    if not INPUT_FILE.exists():
        print(f"ERROR: Input file not found: {INPUT_FILE}")
        return

    rows = []

    with INPUT_FILE.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            if row["status"] == "SUCCESS":
                rows.append(row)

    if not rows:
        print("ERROR: No successful benchmark results found.")
        return

    times = [
        float(row["execution_time_seconds"])
        for row in rows
    ]

    total_time = sum(times)
    average_time = statistics.mean(times)
    minimum_time = min(times)
    maximum_time = max(times)

    min_query = rows[times.index(minimum_time)]["query"]
    max_query = rows[times.index(maximum_time)]["query"]

    summary = [
        {
            "database": "Neo4j",
            "total_queries": len(rows),
            "successful_queries": len(rows),
            "total_execution_time_seconds": round(total_time, 6),
            "average_execution_time_seconds": round(average_time, 6),
            "minimum_execution_time_seconds": round(minimum_time, 6),
            "maximum_execution_time_seconds": round(maximum_time, 6),
            "fastest_query": min_query,
            "slowest_query": max_query,
        }
    ]

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline=""
    ) as file:

        fieldnames = [
            "database",
            "total_queries",
            "successful_queries",
            "total_execution_time_seconds",
            "average_execution_time_seconds",
            "minimum_execution_time_seconds",
            "maximum_execution_time_seconds",
            "fastest_query",
            "slowest_query",
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(summary)

    print("=" * 50)
    print("Neo4j benchmark summary created successfully.")
    print("=" * 50)
    print()
    print(f"Queries executed : {len(rows)}")
    print(f"Successful       : {len(rows)}")
    print(f"Total time       : {total_time:.6f} seconds")
    print(f"Average time     : {average_time:.6f} seconds")
    print(f"Fastest query    : {min_query} ({minimum_time:.6f} s)")
    print(f"Slowest query    : {max_query} ({maximum_time:.6f} s)")
    print()
    print(f"Results saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()