# Graph Database Benchmark Report

## 1. Overview

This project evaluates graph database performance using the Pokec social-network dataset.

The benchmark compares Neo4j and CognoDB using read workloads and mixed read/write workloads under different concurrency levels.

The benchmark evaluates:

- Point lookups
- Indexed lookups
- 1-hop traversal
- 2-hop traversal
- 3-hop traversal
- Aggregation
- Mixed read/write workloads
- Concurrent execution
- Query errors
- Throughput
- P50 and P95 latency

---

## 2. Dataset

**Dataset:** Pokec

**Prepared sample:** `data/pokec_sample.csv`

- Relationships: 120,000
- Person nodes loaded into Neo4j: 60,454
- Relationship type: `KNOWS`

Neo4j successfully loaded all 120,000 relationships.

**Neo4j loading time:** 19.39 seconds

---

## 3. Neo4j Workload Validation

A total of 10 benchmark queries were executed against Neo4j.

| Query | Execution Time (seconds) | Status |
|---|---:|---|
| Q1 Count Persons | 0.075124 | SUCCESS |
| Q2 Count Relationships | 0.068765 | SUCCESS |
| Q3 Find Person | 0.072836 | SUCCESS |
| Q4 Find Neighbors | 0.100275 | SUCCESS |
| Q5 Neighbor Count | 0.080772 | SUCCESS |
| Q6 Two-Hop Neighbors | 0.082471 | SUCCESS |
| Q7 Three-Hop Neighbors | 0.096232 | SUCCESS |
| Q8 Most Connected | 0.202026 | SUCCESS |
| Q9 Relationship Existence | 0.081814 | SUCCESS |
| Q10 Shortest Path | 0.090856 | SUCCESS |

### Validation Summary

- Total queries: 10
- Successful queries: 10
- Failed queries: 0
- Total execution time: 0.951171 seconds
- Average execution time: 0.095117 seconds
- Fastest query: Q2 Count Relationships
- Slowest query: Q8 Most Connected

---

## 4. Read Performance Comparison

Neo4j was compared with CognoDB across six read workloads.

### P50 Latency

| Workload | Neo4j P50 (ms) | CognoDB P50 (ms) | Difference (ms) | Winner |
|---|---:|---:|---:|---|
| 1-hop traversal | 55.254 | 262.505 | 207.251 | Neo4j |
| 2-hop traversal | 57.015 | 261.896 | 204.881 | Neo4j |
| 3-hop traversal | 56.965 | 263.657 | 206.692 | Neo4j |
| Point lookup | 55.477 | 263.328 | 207.851 | Neo4j |
| Indexed lookup | 54.666 | 262.221 | 207.555 | Neo4j |
| Aggregation | 55.235 | 255.528 | 200.293 | Neo4j |

Neo4j won all six workloads based on P50 latency.

### P95 Latency

| Workload | Neo4j P95 (ms) | CognoDB P95 (ms) | Difference (ms) | Winner |
|---|---:|---:|---:|---|
| 1-hop traversal | 66.891 | 275.157 | 208.266 | Neo4j |
| 2-hop traversal | 71.762 | 271.985 | 200.223 | Neo4j |
| 3-hop traversal | 68.002 | 273.267 | 205.265 | Neo4j |
| Point lookup | 63.264 | 278.196 | 214.932 | Neo4j |
| Indexed lookup | 91.386 | 280.617 | 189.231 | Neo4j |
| Aggregation | 73.672 | 265.470 | 191.798 | Neo4j |

Neo4j won all six workloads based on P95 latency.

---

## 5. Mixed Workload Comparison

The mixed workload used approximately 70% reads and 30% writes.

Each concurrency level was tested for approximately 30 seconds.

| Concurrency | Neo4j QPS | CognoDB QPS | Winner | Neo4j Errors | CognoDB Errors |
|---:|---:|---:|---|---:|---:|
| 1 | 16.35 | 3.67 | Neo4j | 0 | 0 |
| 10 | 147.15 | 35.37 | Neo4j | 0 | 0 |
| 40 | 202.76 | 131.50 | Neo4j | 0 | 6 |

Neo4j achieved higher throughput at every tested concurrency level.

At concurrency 40:

- Neo4j: 202.76 QPS
- CognoDB: 131.50 QPS
- Neo4j errors: 0
- CognoDB errors: 6

---

## 6. Performance Summary

### Read Workloads

Neo4j demonstrated substantially lower latency across all tested read workloads.

- P50: Neo4j won 6/6 workloads
- P95: Neo4j won 6/6 workloads

### Mixed Workloads

Neo4j achieved higher throughput at every tested concurrency level:

- Concurrency 1: 16.35 QPS
- Concurrency 10: 147.15 QPS
- Concurrency 40: 202.76 QPS

Neo4j also maintained zero reported errors across all tested concurrency levels.

---

## 7. Charts

The benchmark generated the following charts:

- `charts/read_performance_comparison.png`
- `charts/mixed_workload_comparison.png`

These charts visualize:

- Neo4j vs CognoDB read latency
- Neo4j vs CognoDB mixed workload throughput

---

## 8. Conclusion

Based on the benchmark results, Neo4j demonstrated stronger performance than CognoDB for the tested Pokec dataset and workload configuration.

Neo4j achieved lower P50 and P95 latency across all six read workloads and higher throughput at all tested concurrency levels.

Neo4j successfully completed all 10 validation queries.

During the mixed workload benchmark, Neo4j reported zero errors at all tested concurrency levels.

At concurrency 40, Neo4j achieved 202.76 QPS compared with 131.50 QPS for CognoDB.

Therefore, for this benchmark configuration, Neo4j provided better read latency, higher mixed-workload throughput, and more consistent execution under increasing concurrency.

---

## 9. Benchmark Artifacts

### Dataset

`data/pokec_sample.csv`

### Loaders

`loaders/load_neo4j.py`

`loaders/load_cognodb.py`

### Workloads

`workloads/neo4j_workload.py`

`workloads/neo4j_read_workload.py`

`workloads/mixed_workload.py`

### Results

`results/neo4j_workload_results.csv`

`results/neo4j_read_results.csv`

`results/cognodb_read_results.csv`

`results/read_comparison.csv`

`results/neo4j_mixed_results.csv`

`results/cognodb_mixed_results.csv`

`results/mixed_comparison.csv`

### Charts

`charts/read_performance_comparison.png`

`charts/mixed_workload_comparison.png`