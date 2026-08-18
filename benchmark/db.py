from neo4j import GraphDatabase

from benchmark.config import DATABASES


def create_driver(database_name="cognodb"):
    config = DATABASES[database_name]

    return GraphDatabase.driver(
        config["uri"],
        auth=(config["username"], config["password"]),
    )


def close_driver(driver):
    driver.close()