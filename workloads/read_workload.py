import os
import csv
import random
import time

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ========================================
# Configuration
# ========================================

load_dotenv(".env", override=True)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

ITERATIONS = 100
WARMUP = 20
START_NODE_COUNT = 200

RESULT_FILE = "results/neo4j_read_results.csv"


# ========================================
# Neo4j Aura certificate handling
# ========================================

if NEO4J_URI and NEO4J_URI.startswith("neo4j+s://"):
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
# Run one query
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
# Benchmark query
# ========================================

def benchmark_query(
    session,
    name,
    query,
    node_ids,
    results
):

    print()
    print(f"Running: {name}")

    # ------------------------------
    # Warm-up
    # ------------------------------

    warmup_ids = random.choices(
        node_ids,
        k=WARMUP
    )

    for node_id in warmup_ids:

        run_query(
            session,
            query,
            {"node_id": node_id}
        )

    # ------------------------------
    # Measured iterations
    # ------------------------------

    latencies = []

    test_ids = random.choices(
        node_ids,
        k=ITERATIONS
    )

    for node_id in test_ids:

        latency = run_query(
            session,
            query,
            {"node_id": node_id}
        )

        latencies.append(latency)

    p50 = percentile(
        latencies,
        50
    )

    p95 = percentile(
        latencies,
        95
    )

    print(
        f"{name}: "
        f"p50={p50:.3f} ms, "
        f"p95={p95:.3f} ms"
    )

    results.append({
        "database": "Neo4j",
        "workload": name,
        "p50_ms": round(p50, 3),
        "p95_ms": round(p95, 3)
    })


# ========================================
# Aggregation benchmark
# ========================================

def benchmark_aggregation(
    session,
    results
):

    name = "Aggregation"

    print()
    print(f"Running: {name}")

    query = """
        MATCH (n:Person)
        RETURN count(n) AS total
    """

    # ------------------------------
    # Warm-up
    # ------------------------------

    for _ in range(WARMUP):

        session.run(query).consume()

    # ------------------------------
    # Measurements
    # ------------------------------

    latencies = []

    for _ in range(ITERATIONS):

        start = time.perf_counter()

        session.run(query).consume()

        elapsed_ms = (
            time.perf_counter()
            - start
        ) * 1000

        latencies.append(
            elapsed_ms
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
        f"{name}: "
        f"p50={p50:.3f} ms, "
        f"p95={p95:.3f} ms"
    )

    results.append({
        "database": "Neo4j",
        "workload": name,
        "p50_ms": round(p50, 3),
        "p95_ms": round(p95, 3)
    })


# ========================================
# Main
# ========================================

def main():

    print("=" * 50)
    print("       Neo4j Read Workload Benchmark")
    print("=" * 50)

    print()
    print("Neo4j URI:", NEO4J_URI)
    print("Database:", NEO4J_DATABASE)

    print()
    print("Warm-up iterations:", WARMUP)
    print("Measured iterations:", ITERATIONS)

    # ====================================
    # Create driver
    # ====================================

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(
            NEO4J_USERNAME,
            NEO4J_PASSWORD
        )
    )

    try:

        print()
        print("Testing Neo4j connection...")

        driver.verify_connectivity()

        print(
            "Neo4j connection successful."
        )

        # ====================================
        # Get sample nodes
        # ====================================

        print()
        print(
            "Selecting benchmark nodes..."
        )

        with driver.session(
            database=NEO4J_DATABASE
        ) as session:

            records = session.run(
                """
                MATCH (n:Person)
                RETURN n.id AS id
                ORDER BY rand()
                LIMIT $limit
                """,
                limit=START_NODE_COUNT
            )

            node_ids = [
                record["id"]
                for record in records
            ]

        print(
            f"Benchmark nodes available: "
            f"{len(node_ids):,}"
        )

        if len(node_ids) < 2:

            raise RuntimeError(
                "Not enough Person nodes."
            )

        # ====================================
        # Run benchmarks
        # ====================================

        results = []

        with driver.session(
            database=NEO4J_DATABASE
        ) as session:

            # ------------------------------
            # 1-hop traversal
            # ------------------------------

            benchmark_query(
                session,
                "1-hop traversal",
                """
                MATCH (n:Person {id: $node_id})
                      -[:KNOWS]->(m:Person)
                RETURN count(m) AS count
                """,
                node_ids,
                results
            )

            # ------------------------------
            # 2-hop traversal
            # ------------------------------

            benchmark_query(
                session,
                "2-hop traversal",
                """
                MATCH (n:Person {id: $node_id})
                      -[:KNOWS*2]->(m:Person)
                RETURN count(m) AS count
                """,
                node_ids,
                results
            )

            # ------------------------------
            # 3-hop traversal
            # ------------------------------

            benchmark_query(
                session,
                "3-hop traversal",
                """
                MATCH (n:Person {id: $node_id})
                      -[:KNOWS*3]->(m:Person)
                RETURN count(m) AS count
                """,
                node_ids,
                results
            )

            # ------------------------------
            # Point lookup
            # ------------------------------

            benchmark_query(
                session,
                "Point lookup",
                """
                MATCH (n:Person {id: $node_id})
                RETURN n.id AS id
                """,
                node_ids,
                results
            )

            # ------------------------------
            # Indexed lookup
            # ------------------------------

            benchmark_query(
                session,
                "Indexed lookup",
                """
                MATCH (n:Person)
                WHERE n.id = $node_id
                RETURN n.id AS id
                """,
                node_ids,
                results
            )

            # ------------------------------
            # Aggregation
            # ------------------------------

            benchmark_aggregation(
                session,
                results
            )

        # ====================================
        # Save results
        # ====================================

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

        # ====================================
        # Completed
        # ====================================

        print()
        print("=" * 50)
        print(
            "Neo4j read workload completed."
        )
        print("=" * 50)

        print()
        print("Results saved to:")
        print(RESULT_FILE)

    finally:

        driver.close()


# ========================================
# Entry point
# ========================================

if __name__ == "__main__":
    main()