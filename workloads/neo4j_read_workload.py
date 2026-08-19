import os
import csv
import random
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ========================================
# Neo4j Read Workload Benchmark
# ========================================

load_dotenv(".env", override=True)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

RESULT_FILE = os.path.join(
    "results",
    "neo4j_read_results.csv"
)

ITERATIONS = 100
WARMUP = 20
START_NODE_COUNT = 200


# ========================================
# Certificate handling
# ========================================

if NEO4J_URI.startswith("neo4j+s://"):
    NEO4J_URI = NEO4J_URI.replace(
        "neo4j+s://",
        "neo4j+ssc://",
        1
    )


# ========================================
# Percentile calculation
# ========================================

def percentile(values, percentile_value):

    values = sorted(values)

    index = (
        (len(values) - 1)
        * percentile_value
        / 100
    )

    lower = int(index)

    upper = min(
        lower + 1,
        len(values) - 1
    )

    if lower == upper:
        return values[lower]

    fraction = index - lower

    return (
        values[lower]
        + (
            values[upper]
            - values[lower]
        )
        * fraction
    )


# ========================================
# Execute query
# ========================================

def run_query(session, query, params=None):

    start = time.perf_counter()

    result = session.run(
        query,
        params or {}
    )

    result.consume()

    elapsed_ms = (
        time.perf_counter()
        - start
    ) * 1000

    return elapsed_ms


# ========================================
# Benchmark individual workload
# ========================================

def benchmark_query(
    session,
    name,
    query,
    node_ids
):

    print()
    print(
        f"Running: {name}"
    )

    # -------------------------------
    # Warm-up
    # -------------------------------

    warmup_ids = random.choices(
        node_ids,
        k=WARMUP
    )

    for node_id in warmup_ids:

        run_query(
            session,
            query,
            {
                "node_id": node_id
            }
        )

    # -------------------------------
    # Measured iterations
    # -------------------------------

    latencies = []

    test_ids = random.choices(
        node_ids,
        k=ITERATIONS
    )

    for node_id in test_ids:

        latency = run_query(
            session,
            query,
            {
                "node_id": node_id
            }
        )

        latencies.append(
            latency
        )

    p50 = percentile(
        latencies,
        50
    )

    p95 = percentile(
        latencies,
        95
    )

    print(
        f"P50: {p50:.3f} ms"
    )

    print(
        f"P95: {p95:.3f} ms"
    )

    return p50, p95


# ========================================
# Aggregation benchmark
# ========================================

def benchmark_aggregation(session):

    name = "Aggregation"

    query = """
        MATCH (n:Person)
        RETURN count(n) AS total
    """

    print()
    print(
        f"Running: {name}"
    )

    # -------------------------------
    # Warm-up
    # -------------------------------

    for _ in range(WARMUP):

        run_query(
            session,
            query
        )

    # -------------------------------
    # Measured iterations
    # -------------------------------

    latencies = []

    for _ in range(ITERATIONS):

        latency = run_query(
            session,
            query
        )

        latencies.append(
            latency
        )

    p50 = percentile(
        latencies,
        50
    )

    p95 = percentile(
        latencies,
        95
    )

    print(
        f"P50: {p50:.3f} ms"
    )

    print(
        f"P95: {p95:.3f} ms"
    )

    return p50, p95


# ========================================
# Main
# ========================================

def main():

    print("=" * 50)
    print(
        "      Neo4j Read Workload Benchmark"
    )
    print("=" * 50)

    print()
    print(
        "Neo4j URI:",
        NEO4J_URI
    )

    print(
        "Username:",
        NEO4J_USERNAME
    )

    print(
        "Database:",
        NEO4J_DATABASE
    )

    print()
    print(
        "Warm-up iterations:",
        WARMUP
    )

    print(
        "Measured iterations:",
        ITERATIONS
    )

    print()
    print(
        "Connecting to Neo4j..."
    )

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(
            NEO4J_USERNAME,
            NEO4J_PASSWORD
        )
    )

    results = []

    try:

        driver.verify_connectivity()

        print(
            "Neo4j connection successful."
        )

        with driver.session(
            database=NEO4J_DATABASE
        ) as session:

            # ========================================
            # Get benchmark nodes
            # ========================================

            print()
            print(
                "Selecting benchmark nodes..."
            )

            node_records = session.run(
                """
                MATCH (n:Person)
                RETURN n.id AS id
                ORDER BY rand()
                LIMIT $limit
                """,
                {
                    "limit": START_NODE_COUNT
                }
            )

            node_ids = [
                record["id"]
                for record in node_records
            ]

            print(
                "Benchmark nodes available:",
                len(node_ids)
            )

            if len(node_ids) == 0:

                raise RuntimeError(
                    "No Person nodes found in Neo4j."
                )

            # ========================================
            # 1-hop traversal
            # ========================================

            p50, p95 = benchmark_query(
                session,
                "1-hop traversal",
                """
                MATCH (
                    n:Person {id: $node_id}
                )-[:KNOWS]->(m:Person)
                RETURN count(m) AS count
                """,
                node_ids
            )

            results.append({
                "database": "Neo4j",
                "workload": "1-hop traversal",
                "p50_ms": round(p50, 3),
                "p95_ms": round(p95, 3)
            })

            # ========================================
            # 2-hop traversal
            # ========================================

            p50, p95 = benchmark_query(
                session,
                "2-hop traversal",
                """
                MATCH (
                    n:Person {id: $node_id}
                )-[:KNOWS*2]->(m:Person)
                RETURN count(m) AS count
                """,
                node_ids
            )

            results.append({
                "database": "Neo4j",
                "workload": "2-hop traversal",
                "p50_ms": round(p50, 3),
                "p95_ms": round(p95, 3)
            })

            # ========================================
            # 3-hop traversal
            # ========================================

            p50, p95 = benchmark_query(
                session,
                "3-hop traversal",
                """
                MATCH (
                    n:Person {id: $node_id}
                )-[:KNOWS*3]->(m:Person)
                RETURN count(m) AS count
                """,
                node_ids
            )

            results.append({
                "database": "Neo4j",
                "workload": "3-hop traversal",
                "p50_ms": round(p50, 3),
                "p95_ms": round(p95, 3)
            })

            # ========================================
            # Point lookup
            # ========================================

            p50, p95 = benchmark_query(
                session,
                "Point lookup",
                """
                MATCH (
                    n:Person {id: $node_id}
                )
                RETURN n.id AS id
                """,
                node_ids
            )

            results.append({
                "database": "Neo4j",
                "workload": "Point lookup",
                "p50_ms": round(p50, 3),
                "p95_ms": round(p95, 3)
            })

            # ========================================
            # Indexed lookup
            # ========================================

            p50, p95 = benchmark_query(
                session,
                "Indexed lookup",
                """
                MATCH (n:Person)
                WHERE n.id = $node_id
                RETURN n.id AS id
                """,
                node_ids
            )

            results.append({
                "database": "Neo4j",
                "workload": "Indexed lookup",
                "p50_ms": round(p50, 3),
                "p95_ms": round(p95, 3)
            })

            # ========================================
            # Aggregation
            # ========================================

            p50, p95 = benchmark_aggregation(
                session
            )

            results.append({
                "database": "Neo4j",
                "workload": "Aggregation",
                "p50_ms": round(p50, 3),
                "p95_ms": round(p95, 3)
            })

        # ========================================
        # Save results
        # ========================================

        os.makedirs(
            "results",
            exist_ok=True
        )

        with open(
            RESULT_FILE,
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
                    "p95_ms"
                ]
            )

            writer.writeheader()

            writer.writerows(results)

        print()
        print("=" * 50)
        print(
            "Neo4j read benchmark completed."
        )
        print("=" * 50)

        print()
        print(
            "Results saved to:"
        )

        print(
            RESULT_FILE
        )

    except Exception as error:

        print()
        print(
            "Neo4j read benchmark failed."
        )

        print()
        print(
            "Error:",
            error
        )

        raise

    finally:

        driver.close()


if __name__ == "__main__":
    main()