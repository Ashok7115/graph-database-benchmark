import random
import time

from benchmark.db import create_driver


ITERATIONS = 100
WARMUP = 20
START_NODE_COUNT = 200


def percentile(values, percentile_value):
    values = sorted(values)

    index = (len(values) - 1) * percentile_value / 100
    lower = int(index)
    upper = min(lower + 1, len(values) - 1)

    if lower == upper:
        return values[lower]

    fraction = index - lower

    return (
        values[lower]
        + (values[upper] - values[lower]) * fraction
    )


def run_query(session, query, params):
    start = time.perf_counter()

    session.run(query, **params).consume()

    elapsed_ms = (time.perf_counter() - start) * 1000

    return elapsed_ms


def benchmark_query(session, name, query, node_ids):
    # Warm-up
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

    # Measured iterations
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

    p50 = percentile(latencies, 50)
    p95 = percentile(latencies, 95)

    print(
        f"{name}: "
        f"p50={p50:.3f} ms, "
        f"p95={p95:.3f} ms"
    )


def benchmark_aggregation(session):
    query = """
        MATCH (n:Person)
        RETURN count(n) AS total
    """

    # Warm-up
    for _ in range(WARMUP):
        session.run(query).consume()

    latencies = []

    # Measured iterations
    for _ in range(ITERATIONS):
        start = time.perf_counter()

        session.run(query).consume()

        elapsed_ms = (
            time.perf_counter() - start
        ) * 1000

        latencies.append(elapsed_ms)

    p50 = percentile(latencies, 50)
    p95 = percentile(latencies, 95)

    print(
        f"Aggregation: "
        f"p50={p50:.3f} ms, "
        f"p95={p95:.3f} ms"
    )


def main():
    driver = create_driver()

    try:
        with driver.session() as session:

            # Get only 200 random start nodes.
            # This avoids CognoDB's 50,000-row result limit.
            node_records = session.run(
                """
                MATCH (n:Person)
                RETURN n.id AS id
                ORDER BY rand()
                LIMIT 200
                """
            )

            node_ids = [
                record["id"]
                for record in node_records
            ]

            print(
                f"Benchmark nodes available: "
                f"{len(node_ids):,}"
            )

            print()
            print(
                f"Warm-up iterations: {WARMUP}"
            )
            print(
                f"Measured iterations: {ITERATIONS}"
            )
            print()

            # 1-hop traversal
            benchmark_query(
                session,
                "1-hop traversal",
                """
                MATCH (n:Person {id: $node_id})
                      -[:FRIEND]->(m)
                RETURN count(m) AS count
                """,
                node_ids,
            )

            # 2-hop traversal
            benchmark_query(
                session,
                "2-hop traversal",
                """
                MATCH (n:Person {id: $node_id})
                      -[:FRIEND*2]->(m)
                RETURN count(m) AS count
                """,
                node_ids,
            )

            # 3-hop traversal
            benchmark_query(
                session,
                "3-hop traversal",
                """
                MATCH (n:Person {id: $node_id})
                      -[:FRIEND*3]->(m)
                RETURN count(m) AS count
                """,
                node_ids,
            )

            # Point lookup
            benchmark_query(
                session,
                "Point lookup",
                """
                MATCH (n:Person {id: $node_id})
                RETURN n.id AS id
                """,
                node_ids,
            )

            # Indexed / filtered lookup
            benchmark_query(
                session,
                "Indexed lookup",
                """
                MATCH (n:Person)
                WHERE n.id = $node_id
                RETURN n.id AS id
                """,
                node_ids,
            )

            # Aggregation
            benchmark_aggregation(session)

    finally:
        driver.close()


if __name__ == "__main__":
    main()