# Local data preparation timing

Measured on 2026-11-07 in the Ubuntu 26.04 ARM64 VM, 4 virtual CPUs, with Spark and Ray configured for two local workers. Both jobs processed the same 10,000-row UCI AI4I CSV and wrote equivalent 10,000-row outputs. See `reports/etl_benchmark_run.log` for the exact terminal output and commands.

| Job | Elapsed wall time, including startup and CSV write | Rows per second |
| --- | ---: | ---: |
| Spark 3.5.7 | 7.62 s | 1,312 |
| Ray 2.59.0 | 4.37 s | 2,288 |

These are one-run local measurements on a small synthetic dataset, not a scale benchmark. Process startup dominates this workload. The `time` command's peak RSS only covers its direct process and does not include all Spark JVM or Ray worker memory, so it is not used as a whole-job memory result. Both output CSV files had SHA-256 `b762ea195f1bb9d9150d7dd12a58ccc384790c76b12fcb8cb43c71170b124d38` and passed row-by-row comparison.
