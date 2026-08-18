\# Graph Database Cloud Benchmark



Reproducible benchmarking of CognoDB Cloud and other managed graph database platforms using the same dataset and workloads.



\## Project Status



CognoDB benchmark completed.



\### Dataset



\- Dataset: SNAP soc-Pokec social network sample

\- Nodes: 60,454

\- Relationships: 120,000

\- Relationship type: `FRIEND`

\- Source: Stanford Network Analysis Project (SNAP)

\- Sample size: 120,000 relationships



\## CognoDB Environment



| Property | Value |

|---|---|

| Platform | CognoDB Cloud |

| Tier | Free |

| Instance | c0 |

| Memory | 512 MB |

| CPU | Burst to 0.5 vCPU |

| Storage | 1 GiB |

| Region | N. Virginia (us-east4) |

| Max connections | 200 |

| Disk IOPS | Up to 500 |

| Version | v0.9.11 |



\## CognoDB Data Loading



| Metric | Result |

|---|---:|

| Nodes | 60,454 |

| Relationships | 120,000 |

| Load time | 44.663 seconds |

| Nodes/sec | 1,353.57 |

| Relationships/sec | 2,686.80 |



\## CognoDB Read Benchmark



20 warm-up iterations followed by 100 measured iterations.



| Workload | p50 (ms) | p95 (ms) |

|---|---:|---:|

| 1-hop traversal | 262.505 | 275.157 |

| 2-hop traversal | 261.896 | 271.985 |

| 3-hop traversal | 263.657 | 273.267 |

| Point lookup | 263.328 | 278.196 |

| Indexed lookup | 262.221 | 280.617 |

| Aggregation | 255.528 | 265.470 |



\## CognoDB Mixed Workload



Workload mix: 70% reads / 30% writes.



| Concurrency | Reads | Writes | Errors | QPS |

|---:|---:|---:|---:|---:|

| 1 | 87 | 24 | 0 | 3.67 |

| 10 | 737 | 334 | 0 | 35.37 |

| 40 | 2,722 | 1,267 | 6 | 131.50 |



The 6 errors observed at 40-client concurrency are retained and will be documented as a benchmark caveat.



\## Methodology



The benchmark aims to use:



\- The same dataset on every platform.

\- The same logical workloads.

\- The same client machine.

\- The same region where practical.

\- Comparable compute and storage resources.

\- Warm-up iterations before measured queries.

\- 100 measured iterations for read workloads.

\- p50 and p95 latency reporting.

\- Explicit reporting of errors, limitations and platform differences.



\## Reproducibility



Credentials are loaded from environment variables and are not stored in this repository.



The raw compressed dataset is excluded from Git because of its size. The benchmark sample is included in `data/pokec\_sample.csv`.



\## Repository Structure



```text

benchmark/

data/

loaders/

results/

workloads/

charts/

requirements.txt

