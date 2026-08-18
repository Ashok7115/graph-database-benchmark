import os
from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    "cognodb": {
        "uri": os.getenv("COGNODB_URI"),
        "username": os.getenv("COGNODB_USER"),
        "password": os.getenv("COGNODB_PASSWORD"),
    }
}

BENCHMARK_CONFIG = {
    "warmup_iterations": 20,
    "read_iterations": 100,
    "concurrency_levels": [1, 10, 40],
}