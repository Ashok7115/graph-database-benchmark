import sys
import os

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from benchmark.db import create_driver


print("=" * 40)
print("Neo4j Benchmark Connection Test")
print("=" * 40)

driver = None

try:
    driver = create_driver()

    driver.verify_connectivity()

    print()
    print("Neo4j connection successful.")
    print("Benchmark database connection is working.")

except Exception as e:
    print()
    print("Neo4j connection failed.")
    print()
    print("Error:", e)

finally:
    if driver:
        driver.close()