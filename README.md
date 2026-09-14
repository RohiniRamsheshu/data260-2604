# DATA-260 — Rohini Ramasheshu (SID4: 2604)

A small full-stack project built across DATA-260 homeworks: a vulnerability-report web app, backed by FastAPI, containerized with Docker, deployed to AWS ECS, and extended with a local multi-agent LLM pipeline built on LangGraph.

**Domain**: Open-source package vulnerabilities (`DOMAIN_ID = SID4 mod 8 = 4`).

## Config values (fixed all semester)

## How to run it

**1. Backend + form** (FastAPI, serves the form and the CRUD API):
```bash
source venv/bin/activate
uvicorn src.main:app --reload --port 8804
```
Visit `http://localhost:8804`. API lives at `/api/records` (GET to list/search, POST to add, `/1/update` and `/delete-highest` for the other operations).

**2. Docker** (containerized version, HW1):
```bash
docker build --platform linux/amd64 -t vuln-report-app .
docker run -p 8804:8804 vuln-report-app
```
`--platform linux/amd64` is required when building on Apple Silicon for AWS Fargate compatibility.

**3. Agent pipeline** (needs Ollama running locally with `qwen2.5:3b` pulled — substituted for `qwen3:8b` due to 8GB RAM on this machine):
```bash
brew services start ollama
ollama pull qwen2.5:3b
python src/agents_demo.py       # HW1: simple sequential pipeline
python src/agent_graph.py       # HW2: LangGraph Supervisor with self-correction loop
```

**4. Experiments**:
```bash
python src/run_experiment.py            # HW1: 40 runs, temperature 0.7 vs 0.0
python src/run_schema_experiment.py     # HW2: 30 runs, schema-validation outcomes
python src/run_ceiling_experiment.py    # HW2: turn ceiling 2 vs 10, 20 runs each
```
Raw results land in `reports/hw01/raw/` and `reports/hw02/raw/`.

**5. Self-check**:
```bash
python verify.py
```

## Key lessons worth remembering

- **A background Docker container can silently squat on a port** for days and serve stale content even after you restart your real server — always check `docker ps` if a server behaves "impossibly" wrong.
- **JS code pasted after a function's closing `}` runs outside its scope** and can't see variables declared inside — a bug hit twice during HW1.
- **Apple Silicon builds arm64 images by default**; AWS Fargate needs amd64 — always `docker build --platform linux/amd64` when deploying from an M-series Mac.
- **A Reviewer LLM node needs objective, checkable criteria**, not subjective quality judgment — otherwise a self-correction loop can reject forever and always hit the turn ceiling (seen directly in HW2's Part 3/4 experiments).
- **The in-memory `records` list is not a real database** — it lives in server RAM and is wiped on every restart. That's intentional for this assignment, not a bug.

## Submission tags
- `hw1` -> commit `529e9b3`
- `hw2` -> commit `20cafe2` (see `git rev-parse hw2` for the exact hash used in report.pdf)
