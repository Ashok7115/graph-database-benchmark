import os
import time
import csv
from dotenv import load_dotenv
from neo4j import GraphDatabase


# ========================================
# Neo4j Workload Benchmark
# ========================================

load_dotenv(".env", override=True)

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

DATASET = os.path.join("data", "pokec_sample.csv")
RESULT_FILE = os.path.join("results", "neo4j_workload_results.csv")


# Neo4j Aura certificate handling
if NEO4J_URI.startswith("neo4j+s://"):
    NEO4J_URI = NEO4J_URI.replace(
        "neo4j+s://",
        "neo4j+ssc://",
        1
    )


# ========================================
# Queries
# ========================================

QUERIES = {

    "Q1_Count_Persons": """
        MATCH (p:Person)
        RETURN count(p) AS count
    """,

    "Q2_Count_Relationships": """
        MATCH ()-[r:KNOWS]->()
        RETURN count(r) AS count
    """,

    "Q3_Find_Person": """
        MATCH (p:Person {id: $person_id})
        RETURN p.id AS id
    """,

    "Q4_Find_Neighbors": """
        MATCH (p:Person {id: $person_id})-[:KNOWS]->(n:Person)
        RETURN n.id AS id
    """,

    "Q5_Neighbor_Count": """
        MATCH (p:Person {id: $person_id})-[:KNOWS]->(n:Person)
        RETURN count(n) AS count
    """,

    "Q6_Two_Hop_Neighbors": """
        MATCH (p:Person {id: $person_id})
              -[:KNOWS]->()
              -[:KNOWS]->(n:Person)
        RETURN count(DISTINCT n) AS count
    """,

    "Q7_Three_Hop_Neighbors": """
        MATCH (p:Person {id: $person_id})
              -[:KNOWS]->()
              -[:KNOWS]->()
              -[:KNOWS]->(n:Person)
        RETURN count(DISTINCT n) AS count
    """,

    "Q8_Most_Connected": """
        MATCH (p:Person)-[:KNOWS]->(n:Person)
        RETURN p.id AS id, count(n) AS degree
        ORDER BY degree DESC
        LIMIT 10
    """,

    "Q9_Relationship_Existence": """
        MATCH (p:Person {id: $person_id})
              -[:KNOWS]->
              (n:Person {id: $target_id})
        RETURN count(*) AS count
    """,

    "Q10_Short_Path": """
        MATCH (a:Person {id: $person_id}),
              (b:Person {id: $target_id})
        MATCH p = shortestPath((a)-[:KNOWS*..6]-(b))
        RETURN length(p) AS path_length
    """
}


# ========================================
# Get sample IDs
# ========================================

def get_sample_ids():

    ids = []

    with open(DATASET, "r", newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:

            source = int(row["source_id"])
            target = int(row["target_id"])

            ids.append(source)
            ids.append(target)

            if len(ids) >= 20:
                break

    ids = list(dict.fromkeys(ids))

    if len(ids) < 2:
        raise RuntimeError("Not enough person IDs found in dataset.")

    return ids


# ========================================
# Execute query
# ========================================

def execute_query(session, query_name, query, parameters=None):

    start = time.perf_counter()

    result = session.run(
        query,
        parameters or {}
    )

    records = list(result)

    elapsed = time.perf_counter() - start

    return elapsed, len(records)


# ========================================
# Main benchmark
# ========================================

def main():

    print("=" * 50)
    print("       Neo4j Workload Benchmark")
    print("=" * 50)

    print()
    print("Neo4j URI:", NEO4J_URI)
    print("Database:", NEO4J_DATABASE)
    print("Dataset:", DATASET)

    print()
    print("Connecting to Neo4j...")

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(
            NEO4J_USERNAME,
            NEO4J_PASSWORD
        )
    )

    try:

        driver.verify_connectivity()

        print("Neo4j connection successful.")

        sample_ids = get_sample_ids()

        person_id = sample_ids[0]
        target_id = sample_ids[1]

        print()
        print("Sample person ID:", person_id)
        print("Sample target ID:", target_id)

        os.makedirs("results", exist_ok=True)

        results = []

        print()
        print("=" * 50)
        print("Running workloads...")
        print("=" * 50)

        with driver.session(database=NEO4J_DATABASE) as session:

            for query_name, query in QUERIES.items():

                print()
                print("Running:", query_name)

                parameters = {
                    "person_id": person_id,
                    "target_id": target_id
                }

                try:

                    elapsed, record_count = execute_query(
                        session,
                        query_name,
                        query,
                        parameters
                    )

                    print(
                        f"Time: {elapsed:.6f} seconds"
                    )

                    print(
                        f"Records: {record_count}"
                    )

                    results.append({
                        "query": query_name,
                        "execution_time_seconds": round(
                            elapsed,
                            6
                        ),
                        "records": record_count,
                        "status": "SUCCESS"
                    })

                except Exception as error:

                    print("Query failed:", error)

                    results.append({
                        "query": query_name,
                        "execution_time_seconds": "",
                        "records": "",
                        "status": f"FAILED: {error}"
                    })

        # ========================================
        # Save results
        # ========================================

        with open(
            RESULT_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "query",
                    "execution_time_seconds",
                    "records",
                    "status"
                ]
            )

            writer.writeheader()
            writer.writerows(results)

        print()
        print("=" * 50)
        print("Workload benchmark completed.")
        print("=" * 50)

        print()
        print("Results saved to:")
        print(RESULT_FILE)

    finally:

        driver.close()


if __name__ == "__main__":
    main()