import os

from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("COGNODB_URI")
username = os.getenv("COGNODB_USER")
password = os.getenv("COGNODB_PASSWORD")

if not uri or not username or not password:
    raise RuntimeError("CognoDB credentials are missing from .env")

driver = GraphDatabase.driver(
    uri,
    auth=(username, password)
)

try:
    driver.verify_connectivity()
    print("SUCCESS: Connected to CognoDB!")

    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        record = result.single()
        print("Cypher test result:", record["test"])

finally:
    driver.close()