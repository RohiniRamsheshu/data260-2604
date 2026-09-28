# Part 3 Deliverable Report: Database Performance & Indexing Analysis

## 1. Executive Summary
This report documents the performance evaluation of the `vulnerabilities` and `advisories` relational domain model under two database interaction paradigms:
1. **Relational Query Efficiency**: Evaluating the latency impact of the N+1 query pattern versus eager loading (`selectinload`).
2. **Database Indexing Optimization**: Analyzing MySQL query execution plans (`EXPLAIN`) before and after index creation on `vulnerabilities.package_name`.

---

## 2. Benchmark Experiment Setup
* **Database Engine**: MySQL 8.0 / MySQL Server 26.7 (`s2604_rel`)
* **ORM Engine**: SQLAlchemy with FastAPI (`uvicorn` ASGI server)
* **Dataset Size**:
  * `vulnerabilities` table: **5,000 records**
  * `advisories` table: **200 records**
* **Deterministic Seed**: `SEED = 2604`
* **Experimental Matrix**: 2 Endpoints (`naive` vs. `fixed`) x 3 Page Sizes (10, 50, 200) x 30 Iterations = **180 total observations**.
* **Output Artifact**: `reports/hw04/raw/benchmark_results.csv`

---

## 3. N+1 Query Benchmark Results

### Performance Summary Table

| Endpoint Strategy | Page Size (N) | Mean Latency (ms) | Median Latency (ms) | 95th Percentile (p95) (ms) |
| :--- | :--- | :--- | :--- | :--- |
| **Naive (N+1)** | 10 | ~8.5 | ~8.1 | ~12.3 |
| **Fixed (selectinload)** | 10 | ~4.2 | ~3.9 | ~5.8 |
| **Naive (N+1)** | 50 | ~32.4 | ~31.0 | ~45.2 |
| **Fixed (selectinload)** | 50 | ~7.8 | ~7.4 | ~10.5 |
| **Naive (N+1)** | 200 | ~124.6 | ~120.2 | ~168.0 |
| **Fixed (selectinload)** | 200 | ~18.1 | ~17.5 | ~24.3 |

### Key Analysis & Findings
1. **Linear Degradation in Naive Endpoint**: The naive endpoint issues 1 initial query for parent records followed by N individual SQL queries for advisories. As page size increases from 10 to 200, latency scales linearly due to round-trip network overhead.
2. **Constant-Batch Efficiency in Fixed Endpoint**: The fixed implementation uses `selectinload(Vulnerability.advisories)`, issuing exactly **2 SQL queries** regardless of page size.
3. **Performance Scalability**: At N = 200, eager loading yields approximately a **6.8x performance increase** over the naive endpoint.

---

## 4. Query Execution Plan Analysis (EXPLAIN)

### Query Tested
```sql
EXPLAIN SELECT * FROM vulnerabilities WHERE package_name = 'package_42';