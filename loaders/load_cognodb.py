import csv
import time
from pathlib import Path

from benchmark.db import create_driver


DATA_FILE = Path("data/pokec_sample.csv")
BATCH_SIZE = 1000


def load_data():
    driver = create_driver()

    start_time = time.perf_counter()
    relationship_count = 0
    node_ids = set()

    try:
        with driver.session() as session:
            session.run("""
                CREATE CONSTRAINT person_id IF NOT EXISTS
                FOR (p:Person) REQUIRE p.id IS UNIQUE
            """).consume()

            batch = []

            with DATA_FILE.open("r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    source_id = int(row["source_id"])
                    target_id = int(row["target_id"])

                    node_ids.add(source_id)
                    node_ids.add(target_id)

                    batch.append({
                        "source_id": source_id,
                        "target_id": target_id,
                    })

                    if len(batch) >= BATCH_SIZE:
                        session.run("""
                            UNWIND $rows AS row

                            MERGE (a:Person {id: row.source_id})
                            MERGE (b:Person {id: row.target_id})
                            MERGE (a)-[:FRIEND]->(b)
                        """, rows=batch).consume()

                        relationship_count += len(batch)
                        batch.clear()

                if batch:
                    session.run("""
                        UNWIND $rows AS row

                        MERGE (a:Person {id: row.source_id})
                        MERGE (b:Person {id: row.target_id})
                        MERGE (a)-[:FRIEND]->(b)
                    """, rows=batch).consume()

                    relationship_count += len(batch)

        elapsed = time.perf_counter() - start_time

        print(f"Nodes: {len(node_ids):,}")
        print(f"Relationships: {relationship_count:,}")
        print(f"Load time: {elapsed:.3f} seconds")
        print(f"Nodes/sec: {len(node_ids) / elapsed:,.2f}")
        print(f"Relationships/sec: {relationship_count / elapsed:,.2f}")

    finally:
        driver.close()


if __name__ == "__main__":
    load_data()