import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USER")
PASSWORD = os.getenv("NEO4J_PASSWORD")
DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

if not URI or not USER or not PASSWORD:
    raise RuntimeError(
        "NEO4J_URI, NEO4J_USER, or NEO4J_PASSWORD is missing from .env"
    )

driver = GraphDatabase.driver(
    URI,
    auth=(USER, PASSWORD)
)

try:
    driver.verify_connectivity()
    print("Neo4j connection successful")

    with driver.session(database=DATABASE) as session:
        result = session.run("RETURN 1 AS test")
        record = result.single()
        print("Query result:", record["test"])

finally:
    driver.close()