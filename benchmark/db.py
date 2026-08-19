import os
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


# ========================================
# Project configuration
# ========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env from project root
load_dotenv(PROJECT_ROOT / ".env", override=True)


NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")


# ========================================
# Validate configuration
# ========================================

if not NEO4J_URI:
    raise ValueError("NEO4J_URI is missing from .env")

if not NEO4J_USERNAME:
    raise ValueError("NEO4J_USERNAME is missing from .env")

if not NEO4J_PASSWORD:
    raise ValueError("NEO4J_PASSWORD is missing from .env")

if not NEO4J_DATABASE:
    raise ValueError("NEO4J_DATABASE is missing from .env")


# ========================================
# Handle Neo4j SSL
# ========================================

# Your working loader uses this conversion.
# It allows the Neo4j Python driver to connect
# using the self-signed certificate.
if NEO4J_URI.startswith("neo4j+s://"):

    NEO4J_URI = NEO4J_URI.replace(
        "neo4j+s://",
        "neo4j+ssc://",
        1
    )


# ========================================
# Create driver
# ========================================

def create_driver():

    print("Neo4j URI:", NEO4J_URI)
    print("Neo4j Username:", NEO4J_USERNAME)
    print("Neo4j Database:", NEO4J_DATABASE)

    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(
            NEO4J_USERNAME,
            NEO4J_PASSWORD
        )
    )

    return driver


# ========================================
# Database name
# ========================================

def get_database():

    return NEO4J_DATABASE