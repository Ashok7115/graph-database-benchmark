import csv
from pathlib import Path


RESULTS_DIR = Path("results")


NEO4J_READ = RESULTS_DIR / "neo4j_read_results.csv"
COGNODB_READ = RESULTS_DIR / "cognodb_read_results.csv"

NEO4J_MIXED = RESULTS_DIR / "neo4j_mixed_results.csv"
COGNODB_MIXED = RESULTS_DIR / "cognodb_mixed_results.csv"

OUTPUT_FILE = RESULTS_DIR / "database_comparison.csv"


def read_csv(file_path):
    with file_path.open(
        "r",
        newline="",
        encoding="utf-8"
    ) as file:
        return list(csv.DictReader(file))


def compare_read_results():
    neo4j = read_csv(NEO4J_READ)
    cognodb = read_csv(COGNODB_READ)

    comparison = []

    for neo4j_row in neo4j:

        workload = neo4j_row["workload"]

        cognodb_row = next(
            row for row in cognodb
            if row["workload"] == workload
        )

        neo4j_p50 = float(neo4j_row["p50_ms"])
        cognodb_p50 = float(cognodb_row["p50_ms"])

        neo4j_p95 = float(neo4j_row["p95_ms"])
        cognodb_p95 = float(cognodb_row["p95_ms"])

        p50_difference = cognodb_p50 - neo4j_p50
        p95_difference = cognodb_p95 - neo4j_p95

        if neo4j_p50 < cognodb_p50:
            p50_winner = "Neo4j"
        elif cognodb_p50 < neo4j_p50:
            p50_winner = "CognoDB"
        else:
            p50_winner = "Tie"

        if neo4j_p95 < cognodb_p95:
            p95_winner = "Neo4j"
        elif cognodb_p95 < neo4j_p95:
            p95_winner = "CognoDB"
        else:
            p95_winner = "Tie"

        comparison.append({
            "category": "Read Latency",
            "workload": workload,
            "neo4j_p50_ms": round(neo4j_p50, 3),
            "cognodb_p50_ms": round(cognodb_p50, 3),
            "p50_difference_ms": round(p50_difference, 3),
            "p50_winner": p50_winner,
            "neo4j_p95_ms": round(neo4j_p95, 3),
            "cognodb_p95_ms": round(cognodb_p95, 3),
            "p95_difference_ms": round(p95_difference, 3),
            "p95_winner": p95_winner
        })

    return comparison


def compare_mixed_results():
    neo4j = read_csv(NEO4J_MIXED)
    cognodb = read_csv(COGNODB_MIXED)

    comparison = []

    for neo4j_row in neo4j:

        concurrency = neo4j_row["concurrency"]

        cognodb_row = next(
            row for row in cognodb
            if row["concurrency"] == concurrency
        )

        neo4j_qps = float(neo4j_row["qps"])
        cognodb_qps = float(cognodb_row["qps"])

        neo4j_errors = int(neo4j_row["errors"])
        cognodb_errors = int(cognodb_row["errors"])

        if neo4j_qps > cognodb_qps:
            qps_winner = "Neo4j"
        elif cognodb_qps > neo4j_qps:
            qps_winner = "CognoDB"
        else:
            qps_winner = "Tie"

        comparison.append({
            "category": "Mixed Workload",
            "workload": f"Concurrency {concurrency}",
            "neo4j_qps": round(neo4j_qps, 2),
            "cognodb_qps": round(cognodb_qps, 2),
            "qps_winner": qps_winner,
            "neo4j_errors": neo4j_errors,
            "cognodb_errors": cognodb_errors
        })

    return comparison


def save_comparison(read_results, mixed_results):

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        read_fields = [
            "category",
            "workload",
            "neo4j_p50_ms",
            "cognodb_p50_ms",
            "p50_difference_ms",
            "p50_winner",
            "neo4j_p95_ms",
            "cognodb_p95_ms",
            "p95_difference_ms",
            "p95_winner"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=read_fields
        )

        writer.writeheader()

        for row in read_results:
            writer.writerow(row)

        mixed_fields = [
            "category",
            "workload",
            "neo4j_qps",
            "cognodb_qps",
            "qps_winner",
            "neo4j_errors",
            "cognodb_errors"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=mixed_fields
        )

        for row in mixed_results:

            file.write(
                ",".join(
                    [
                        row["category"],
                        row["workload"],
                        "",
                        "",
                        "",
                        row["qps_winner"],
                        "",
                        ""
                    ]
                )
                + "\n"
            )


def print_read_results(results):

    print()
    print("=" * 70)
    print("READ LATENCY COMPARISON")
    print("=" * 70)

    for row in results:

        print()
        print("Workload:", row["workload"])

        print(
            f"  P50  - Neo4j: "
            f"{row['neo4j_p50_ms']:.3f} ms"
        )

        print(
            f"  P50  - CognoDB: "
            f"{row['cognodb_p50_ms']:.3f} ms"
        )

        print(
            f"  P50 Winner: "
            f"{row['p50_winner']}"
        )

        print(
            f"  P95  - Neo4j: "
            f"{row['neo4j_p95_ms']:.3f} ms"
        )

        print(
            f"  P95  - CognoDB: "
            f"{row['cognodb_p95_ms']:.3f} ms"
        )

        print(
            f"  P95 Winner: "
            f"{row['p95_winner']}"
        )


def print_mixed_results(results):

    print()
    print("=" * 70)
    print("MIXED WORKLOAD COMPARISON")
    print("=" * 70)

    for row in results:

        print()
        print("Workload:", row["workload"])

        print(
            f"  Neo4j QPS: "
            f"{row['neo4j_qps']:.2f}"
        )

        print(
            f"  CognoDB QPS: "
            f"{row['cognodb_qps']:.2f}"
        )

        print(
            f"  QPS Winner: "
            f"{row['qps_winner']}"
        )

        print(
            f"  Neo4j Errors: "
            f"{row['neo4j_errors']}"
        )

        print(
            f"  CognoDB Errors: "
            f"{row['cognodb_errors']}"
        )


def main():

    print("=" * 70)
    print("       Graph Database Benchmark Comparison")
    print("=" * 70)

    required_files = [
        NEO4J_READ,
        COGNODB_READ,
        NEO4J_MIXED,
        COGNODB_MIXED
    ]

    for file_path in required_files:

        if not file_path.exists():

            raise FileNotFoundError(
                f"Required result file not found: {file_path}"
            )

    read_results = compare_read_results()
    mixed_results = compare_mixed_results()

    print_read_results(read_results)
    print_mixed_results(mixed_results)

    print()
    print("=" * 70)
    print("Saving comparison results...")
    print("=" * 70)

    RESULTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save the read comparison separately
    read_output = RESULTS_DIR / "read_comparison.csv"

    with read_output.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        fieldnames = [
            "workload",
            "neo4j_p50_ms",
            "cognodb_p50_ms",
            "p50_difference_ms",
            "p50_winner",
            "neo4j_p95_ms",
            "cognodb_p95_ms",
            "p95_difference_ms",
            "p95_winner"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in read_results:
            writer.writerow({
                key: row[key]
                for key in fieldnames
            })

    # Save mixed comparison
    mixed_output = RESULTS_DIR / "mixed_comparison.csv"

    with mixed_output.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        fieldnames = [
            "concurrency",
            "neo4j_qps",
            "cognodb_qps",
            "qps_winner",
            "neo4j_errors",
            "cognodb_errors"
        ]

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in mixed_results:

            concurrency = row["workload"].replace(
                "Concurrency ",
                ""
            )

            writer.writerow({
                "concurrency": concurrency,
                "neo4j_qps": row["neo4j_qps"],
                "cognodb_qps": row["cognodb_qps"],
                "qps_winner": row["qps_winner"],
                "neo4j_errors": row["neo4j_errors"],
                "cognodb_errors": row["cognodb_errors"]
            })

    print()
    print("Comparison files created successfully.")

    print()
    print("Files:")
    print(read_output)
    print(mixed_output)

    print()
    print("=" * 70)
    print("Comparison completed.")
    print("=" * 70)


if __name__ == "__main__":
    main()