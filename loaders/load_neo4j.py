import os
import csv
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


# =========================================================
# PROJECT PATH
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# =========================================================
# LOAD .env
# =========================================================

ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE, override=True)


# =========================================================
# CONFIGURATION
# =========================================================

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

DATASET = PROJECT_ROOT / "data" / "pokec_sample.csv"


# =========================================================
# VALIDATE CONFIGURATION
# =========================================================

print("========================================")
print("       Neo4j Pokec Dataset Loader")
print("========================================")

print()
print("Neo4j URI:", NEO4J_URI)
print("Username:", NEO4J_USERNAME)
print("Database:", NEO4J_DATABASE)
print("Dataset:", DATASET.relative_to(PROJECT_ROOT))


if not NEO4J_URI:
    raise ValueError("NEO4J_URI is missing from .env")

if not NEO4J_USERNAME:
    raise ValueError("NEO4J_USERNAME is missing from .env")

if not NEO4J_PASSWORD:
    raise ValueError("NEO4J_PASSWORD is missing from .env")

if not NEO4J_DATABASE:
    raise ValueError("NEO4J_DATABASE is missing from .env")

if not DATASET.exists():
    raise FileNotFoundError(
        f"Dataset not found: {DATASET}"
    )


# =========================================================
# CREATE NEO4J DRIVER
# =========================================================

# Use neo4j+ssc:// because the Neo4j server
# requires encrypted connection with self-signed certificate
if NEO4J_URI.startswith("neo4j+s://"):
    NEO4J_URI = NEO4J_URI.replace(
        "neo4j+s://",
        "neo4j+ssc://",
        1
    )

driver = GraphDatabase.driver(
    NEO4J_URI,
    auth=(
        NEO4J_USERNAME,
        NEO4J_PASSWORD
    )
)

# =========================================================
# TEST CONNECTION
# =========================================================

def test_connection():

    print()
    print("Testing Neo4j connection...")

    with driver.session(
        database=NEO4J_DATABASE
    ) as session:

        result = session.run(
            "RETURN 1 AS result"
        )

        record = result.single()

        if record["result"] == 1:
            print("Neo4j connection successful.")

        else:
            raise RuntimeError(
                "Neo4j connection test failed."
            )


# =========================================================
# CREATE UNIQUENESS CONSTRAINT
# =========================================================

def create_constraint():

    print()
    print("Creating uniqueness constraint...")

    query = """
    CREATE CONSTRAINT person_id_unique IF NOT EXISTS
    FOR (p:Person)
    REQUIRE p.id IS UNIQUE
    """

    with driver.session(
        database=NEO4J_DATABASE
    ) as session:

        session.run(query).consume()

    print("Constraint ready.")


# =========================================================
# READ CSV
# =========================================================

def read_dataset():

    print()
    print("Reading dataset...")

    rows = []

    with open(
        DATASET,
        "r",
        encoding="utf-8",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        print(
            "CSV columns:",
            reader.fieldnames
        )

        # -------------------------------------------------
        # Validate columns
        # -------------------------------------------------

        required_columns = {
            "source_id",
            "target_id"
        }

        actual_columns = set(
            reader.fieldnames or []
        )

        missing_columns = (
            required_columns - actual_columns
        )

        if missing_columns:

            raise ValueError(
                f"Missing CSV columns: {missing_columns}. "
                f"Found: {reader.fieldnames}"
            )

        # -------------------------------------------------
        # Read rows
        # -------------------------------------------------

        for row in reader:

            source_id = int(
                row["source_id"]
            )

            target_id = int(
                row["target_id"]
            )

            rows.append(
                {
                    "source": source_id,
                    "target": target_id
                }
            )

    print(
        f"Rows read: {len(rows):,}"
    )

    return rows


# =========================================================
# LOAD DATA INTO NEO4J
# =========================================================

def load_data(rows):

    if not rows:

        print()
        print("Dataset is empty.")

        return

    print()
    print("Loading data into Neo4j...")

    start_time = time.perf_counter()

    batch_size = 5000

    total_rows = len(rows)

    loaded_rows = 0

    query = """
    UNWIND $rows AS row

    MERGE (source:Person {
        id: row.source
    })

    MERGE (target:Person {
        id: row.target
    })

    MERGE (source)-[:KNOWS]->(target)
    """

    with driver.session(
        database=NEO4J_DATABASE
    ) as session:

        for start in range(
            0,
            total_rows,
            batch_size
        ):

            end = min(
                start + batch_size,
                total_rows
            )

            batch = rows[
                start:end
            ]

            session.run(
                query,
                rows=batch
            ).consume()

            loaded_rows += len(batch)

            print(
                f"Loaded {loaded_rows:,} "
                f"/ {total_rows:,} rows",
                end="\r"
            )

    elapsed = (
        time.perf_counter()
        - start_time
    )

    print()

    print()
    print("Data loading completed.")

    print(
        f"Rows loaded: {loaded_rows:,}"
    )

    print(
        f"Loading time: {elapsed:.2f} seconds"
    )


# =========================================================
# VERIFY DATA
# =========================================================

def verify_data():

    print()
    print("Verifying Neo4j data...")

    with driver.session(
        database=NEO4J_DATABASE
    ) as session:

        # -------------------------------------------------
        # Count nodes
        # -------------------------------------------------

        node_result = session.run(
            """
            MATCH (p:Person)
            RETURN count(p) AS count
            """
        )

        node_count = (
            node_result.single()["count"]
        )

        # -------------------------------------------------
        # Count relationships
        # -------------------------------------------------

        relationship_result = session.run(
            """
            MATCH ()-[r:KNOWS]->()
            RETURN count(r) AS count
            """
        )

        relationship_count = (
            relationship_result.single()["count"]
        )

    print()
    print(
        f"Person nodes: {node_count:,}"
    )

    print(
        f"KNOWS relationships: "
        f"{relationship_count:,}"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    try:

        # -------------------------------------------------
        # 1. Test connection
        # -------------------------------------------------

        test_connection()

        # -------------------------------------------------
        # 2. Create constraint
        # -------------------------------------------------

        create_constraint()

        # -------------------------------------------------
        # 3. Read CSV
        # -------------------------------------------------

        rows = read_dataset()

        # -------------------------------------------------
        # 4. Load data
        # -------------------------------------------------

        load_data(rows)

        # -------------------------------------------------
        # 5. Verify data
        # -------------------------------------------------

        verify_data()

        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        print()
        print("========================================")
        print("Neo4j loader completed successfully.")
        print("========================================")

    except Exception as error:

        print()
        print("========================================")
        print("Neo4j loader failed.")
        print("========================================")

        print()
        print("Error:", error)

        raise

    finally:

        driver.close()


# =========================================================
# PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()