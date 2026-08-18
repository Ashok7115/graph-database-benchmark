import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from benchmark.db import create_driver


DURATION_SECONDS = 30
CONCURRENCY_LEVELS = [1, 10, 40]

READ_RATIO = 0.70
WRITE_RATIO = 0.30

READ_QUERY = """
MATCH (n:Person {id: $node_id})
RETURN n.id AS id
"""

WRITE_QUERY = """
MATCH (n:Person {id: $node_id})
SET n.last_benchmark_update = $timestamp
RETURN n.id AS id
"""


def get_node_ids(driver):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (n:Person)
            RETURN n.id AS id
            ORDER BY rand()
            LIMIT 200
            """
        )

        return [record["id"] for record in result]


def worker(driver, node_ids, stop_event, counters, lock):
    local_reads = 0
    local_writes = 0
    local_errors = 0

    with driver.session() as session:

        while not stop_event.is_set():

            node_id = random.choice(node_ids)

            try:
                if random.random() < READ_RATIO:

                    session.run(
                        READ_QUERY,
                        node_id=node_id
                    ).consume()

                    local_reads += 1

                else:

                    session.run(
                        WRITE_QUERY,
                        node_id=node_id,
                        timestamp=time.time()
                    ).consume()

                    local_writes += 1

            except Exception:
                local_errors += 1

    with lock:
        counters["reads"] += local_reads
        counters["writes"] += local_writes
        counters["errors"] += local_errors


def run_benchmark(driver, node_ids, concurrency):
    stop_event = threading.Event()

    counters = {
        "reads": 0,
        "writes": 0,
        "errors": 0,
    }

    lock = threading.Lock()

    start = time.perf_counter()

    with ThreadPoolExecutor(
        max_workers=concurrency
    ) as executor:

        futures = []

        for _ in range(concurrency):
            futures.append(
                executor.submit(
                    worker,
                    driver,
                    node_ids,
                    stop_event,
                    counters,
                    lock
                )
            )

        time.sleep(DURATION_SECONDS)

        stop_event.set()

        for future in futures:
            future.result()

    elapsed = time.perf_counter() - start

    total_operations = (
        counters["reads"]
        + counters["writes"]
    )

    qps = total_operations / elapsed

    print(
        f"Concurrency: {concurrency}"
    )

    print(
        f"Duration: {elapsed:.2f} seconds"
    )

    print(
        f"Reads: {counters['reads']:,}"
    )

    print(
        f"Writes: {counters['writes']:,}"
    )

    print(
        f"Errors: {counters['errors']:,}"
    )

    print(
        f"Total operations: {total_operations:,}"
    )

    print(
        f"Throughput: {qps:.2f} queries/sec"
    )

    print()


def main():
    driver = create_driver()

    try:

        node_ids = get_node_ids(driver)

        print(
            f"Benchmark nodes available: "
            f"{len(node_ids):,}"
        )

        print(
            f"Read ratio: {READ_RATIO * 100:.0f}%"
        )

        print(
            f"Write ratio: {WRITE_RATIO * 100:.0f}%"
        )

        print(
            f"Test duration: "
            f"{DURATION_SECONDS} seconds"
        )

        print()

        for concurrency in CONCURRENCY_LEVELS:

            run_benchmark(
                driver,
                node_ids,
                concurrency
            )

    finally:
        driver.close()


if __name__ == "__main__":
    main()