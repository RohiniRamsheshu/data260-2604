# DATA-260 Homework 4 Report

**Name**: Rohini Ramasheshu
**Repository**: https://github.com/RohiniRamsheshu/data260-2604 (collaborators: Sbnikitha, supriyaselvanganesan)

> Lines marked **[TODO]** need something only you have (a screenshot, a number from your own run). Delete this note and every TODO before exporting.

## Section 0 — Configuration

| Value | Setting |
|---|---|
| SID4 | 2604 |
| PORT_BASE | 8804 |
| PREFIX | s2604 |
| SEED | 2604 |
| VERIFY_SEED | 262604 |
| DOMAIN_ID | 4 (Open-source package vulnerabilities) |
| Hardware | MacBook Air M2, 8 GB RAM |
| Local model | qwen2.5:3b (substituted for qwen3:8b, see HW1) |
| Tagged commit | 83a3a37 **[TODO: confirm with `git rev-parse hw4` after the final commit and tag]** |

Database credentials are kept in a local `.env` file that is not committed.

---

## Part 1 — React Client (`localhost:5173`)

Components: `Login.jsx`, `Home.jsx`, `CreateRecord.jsx`, `UpdateRecord.jsx`, `DeleteRecord.jsx`, routed with `react-router-dom`. State is held with `useState`, data is loaded with `useEffect`, and Create/Update/Delete receive their behavior through props.

- **Not logged in**: the app shows "Login required: Please log in to view or edit records." and hides the record navigation.
- **Login**: email + password posted to the backend, which sets an HTTP-only session cookie.

| Screen | Screenshot |
|---|---|
| Login required (logged out) | ![](screenshots/react-login-required.png) |
| Login form | ![](screenshots/react-login.png) |
| Home: record list | ![](screenshots/react-home.png) |
| Create | ![](screenshots/react-create.png) |
| Update | ![](screenshots/react-update.png) |
| Delete | ![](screenshots/react-delete.png) |

**[TODO]** Paste a short code snippet under each screenshot (the assignment wants code and output together).

---

## Part 2 — MySQL Persistence and Server-Side Sessions

Database `s2604_rel` with four tables, defined as SQLAlchemy models in `src/models.py`:

| Table | Columns | Purpose |
|---|---|---|
| vulnerabilities | id, package_name, cve_id | Domain entity |
| advisories | id, vulnerability_id, note | Related rows for Part 3 |
| users | id, name, email (unique), password_hash | Login accounts (bcrypt hashes) |
| sessions | id (token), user_id, created_at, expires_at | Server-side sessions |

The session cookie is HTTP-only and holds only the opaque token. All user data stays server-side in the `sessions` table. The connection variable is named `db_session_basede26`.

### Endpoints (all under `/api/vulnerabilities`)

| Operation | Method and path | Screenshot |
|---|---|---|
| Login | POST `/api/login` | ![](screenshots/postman-login.png) |
| Create | POST `/api/vulnerabilities` | ![](screenshots/postman-create.png) |
| List | GET `/api/vulnerabilities` | ![](screenshots/postman-list.png) |
| Get one | GET `/api/vulnerabilities/{id}` | ![](screenshots/postman-get-one.png) |
| Update | PUT `/api/vulnerabilities/{id}` | ![](screenshots/postman-update.png) |
| Delete | DELETE `/api/vulnerabilities/{id}` | ![](screenshots/postman-delete.png) |

**[TODO]** Add two more Postman shots: (a) the Cookies tab after login showing the HTTP-only session cookie, and (b) a protected request with no cookie returning 401/403.

### Database and project structure

- Database: `SHOW TABLES` in `s2604_rel` lists advisories, sessions, users, vulnerabilities. ![](screenshots/db-show-tables.png)
- **[TODO]** Project folder structure screenshot (VS Code explorer): ![](screenshots/folder-structure.png)

---

## Part 3 — N+1 Measurement and Query Tuning

**Setup.** 5,000 `vulnerabilities` rows and 200 `advisories` rows seeded with SEED = 2604 (generator script and schema committed). Each list response includes the related advisory data. Each endpoint was requested 30 times at page sizes 10, 50 and 200, giving 3 × 2 × 30 = 180 measured requests, saved in `reports/hw04/raw/benchmark_results.csv`.

- **Naive**: one query for the page, then one extra query per record (1 + N).
- **Fixed**: eager loading / join, so the related rows come back without a per-record query.

### Results (from `analyze_benchmark.py`, all times in ms; verified reproducible — re-running the script against the same 180-row raw CSV on 2026-09-28 produced identical numbers)

| Page size | Version | SQL stmts/req | p50 | p95 | p99 |
|---|---|---|---|---|---|
| 10 | naive | 11 (1 + N) | 6.56 | 11.48 | **259.26** |
| 10 | fixed | 1-2 | 3.17 | 5.35 | 5.60 |
| 50 | naive | 51 (1 + N) | 15.88 | 21.43 | 28.89 |
| 50 | fixed | 1-2 | 4.30 | 6.81 | 11.20 |
| 200 | naive | 201 (1 + N) | 37.76 | 46.62 | 53.82 |
| 200 | fixed | 1-2 | 6.91 | 9.15 | 9.33 |

**Remaining gap in the current script.** The "SQL stmts/req" column above is the expected count by design (naive issues one query for the page plus one per record; fixed issues one query with a join, or two with `selectinload`) — for a fully rigorous number, instrument the actual query count per request (e.g. a SQLAlchemy `before_cursor_execute` event counter) rather than relying on the design expectation.

**The naive p99 outlier at page size 10 (259.26 ms) is worth calling out explicitly.** It is roughly 40x the p50 for the same row (6.56 ms) and far above naive's own p99 at page sizes 50 and 200 (28.89 ms and 53.82 ms). A single unusually slow request among 30 samples can dominate a p99 estimate — with only 30 samples, p99 is effectively close to the single worst observation, so this number is sensitive to one outlier (likely connection setup, a GC pause, or OS scheduling jitter on an 8 GB machine) rather than a stable property of the naive endpoint at that page size. It does not change the overall conclusion (naive is consistently and substantially slower than fixed), but a small-sample p99 like this should not be read as precise, and I would not compare it directly against the p99 at page sizes 50/200 without a larger sample.

### Speed-up of fixed over naive

| Page size | By median (p50) | By p95 |
|---|---|---|
| 10 | 2.1x | 2.1x |
| 50 | 3.7x | 3.2x |
| 200 | 5.5x | 5.1x |

I report the median and p95 rather than mean or p99 for this comparison. The mean for naive at page size 10 (18.85 ms) is more than double its median (6.56 ms), and naive's p99 at the same page size (259.26 ms) is a single-outlier artifact (see the note under the results table) — both would distort a "how much faster" claim. The median and p95 columns are consistent with each other and with the overall pattern, so they are what I use to make the deployment argument below.

### Why the speed-up grows with page size

The naive version issues one extra query per record, so its work grows roughly linearly with page size (11, 51, 201 statements). Each query pays a fixed round-trip cost to MySQL. The fixed version does a constant number of queries no matter how many records are on the page, so its latency grows only with the extra rows returned. At page size 10 the naive endpoint has only 10 extra queries, so the two are close. At 200 it has 200 extra round trips, so the gap widens.

### Index and EXPLAIN

```sql
EXPLAIN SELECT * FROM vulnerabilities WHERE package_name = 'package_42';
CREATE INDEX idx_package_name ON vulnerabilities(package_name);
EXPLAIN SELECT * FROM vulnerabilities WHERE package_name = 'package_42';
```

- **Before** (no index): `Filter: package_name = 'package_42'` over `Table scan on vulnerabilities (cost=504 rows=5000)` — MySQL scans all 5,000 rows to find matches. ![](screenshots/explain-before.png)
- **After** (with `idx_package_name`, re-verified live): `Index lookup on vulnerabilities using idx_package_name (package_name = 'package_42') (cost=50.7 rows=48)` — MySQL uses the index to jump straight to matching rows. ![](screenshots/explain-after.png)
- **Change**: estimated cost dropped from 504 to 50.7 (about a 10x reduction), and the estimated rows examined dropped from 5,000 to 48. The plan changed from a full table scan to an index lookup, which is the entire point of the index — instead of checking every row's `package_name`, MySQL uses the BTREE index to go directly to the matching rows.

**[TODO]** Postman screenshots of the naive and fixed endpoints at page sizes 10, 50 and 200 (six shots).

---

## Part 4 — Grounded RAG

**[TODO — nothing from Part 4 appears in your screenshot doc.]** Fill this from `rag.py` and the files in `reports/hw04/raw/`:

1. **Corpus and index**: number of documents, chunk_size 500, chunk_overlap 50, vector store used.
2. **Retrieved chunks** (source + score) printed before each LLM call.
3. **Three-configuration comparison** for Q1–Q6: (A) No RAG, (B) Basic RAG top-3, (C) Context-engineered RAG.
4. **Refusals**: Q5 (not in the documents) and Q6 (unrelated) must show "I cannot answer this question from the provided documents" under configuration C. State plainly what A and B did on Q5/Q6, including any hallucination.
5. **k sweep** at k = 1, 3, 5 for at least one question.
6. **Evaluation table**:

| Question | Config | Correct retrieval | Correct answer | Grounded | Refused when needed |
|---|---|---|---|---|---|
| Q1 | A / B / C | | | | |
| Q2 | A / B / C | | | | |
| Q3 | A / B / C | | | | |
| Q4 | A / B / C | | | | |
| Q5 | A / B / C | | | | |
| Q6 | A / B / C | | | | |

7. **Analysis (300–500 words)**: which questions retrieved the right chunks; which context changes helped (top_k, de-duplication, chunk size, source labels, ordering, grounding rules); whether the model hallucinated on Q5/Q6; how retrieval, context and prompt together shaped answers.

---

## AI Use

See `reports/hw04/AI_USE.md`. Draft answers, **confirm each is true for you before submitting**:

1. **What I used AI for / did myself**: AI help with SQLAlchemy model drafts, benchmarking logic, and debugging shell command errors. I ran every command, seeded the data, took the measurements and checked the outputs myself.
2. **One thing I verified independently**: **[TODO: pick a real one, for example that both endpoints return identical data, or that the summary script was missing p99.]**
3. **How I detected/verified it**: **[TODO]**
4. **What I changed and why it works now**: **[TODO]**

---

## Reproducing the results

```bash
source venv/bin/activate
uvicorn src.main:app --reload --port 8804      # backend
cd client && npm run dev                        # React on :5173
python analyze_benchmark.py                     # summary from raw/benchmark_results.csv
python rag.py                                   # Part 4
python verify.py                                # writes reports/hw04/verification.json
```
