from benchmark.db import create_driver


def main():
    driver = create_driver()

    try:
        driver.verify_connectivity()

        with driver.session() as session:
            result = session.run(
                "RETURN 'CognoDB connection successful' AS message"
            )
            record = result.single()

            print(record["message"])

    finally:
        driver.close()


if __name__ == "__main__":
    main()