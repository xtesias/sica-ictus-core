# SICA ICTUS

> A systematic knowledge management and ML-augmented hunting platform for DeFi vulnerability research.

---

## Why this exists

DeFi vulnerability research is bottlenecked by attention, not by available targets. Tens of thousands of audit findings, post-mortems, and exploit narratives exist across Solodit, Immunefi, rekt.news, Code4rena, Sherlock, and DeFi HackLabs — but they live in scattered formats, are tagged inconsistently, and offer no structural lens for studying them as a population rather than as isolated incidents.

This platform fixes that. It ingests findings from across the ecosystem, applies a structured set of analytical methodologies (STPA, FMEA, HAZOP, Bow-Tie, STRIDE, plus a five-archetype classification), trains models to surface cross-protocol patterns, and supports active hunts on live bug bounties by treating archetype as the primary research unit rather than similarity.

The system is built around a core thesis: **bugs are not isolated mistakes; they are recurring archetypes that manifest differently across protocols.** A hunt is not "find something new" but "given the archetype you're investigating, what does its population of past instances tell you about where to look here?"

---

## What it does

The platform has six functional layers, built across eight phases. End state:

- **Library** — searchable, sectorised corpus of DeFi findings ingested from multiple sources, semantically embedded for cross-pollination
- **Study Workspace** — per-finding workspace with structured methodology overlays, reproduction status, and notes
- **Hunt Workspace** — active programme workspace that treats methodologies as hypothesis generators rather than retrospective characterisations
- **Cross-reference Engine** — archetype-organised catalogue showing how each vulnerability archetype has appeared across protocols and sectors
- **Recommender** — daily ranked list of high-EV bounty targets with feature attribution (no black-box scores)
- **Reproduction integration** — Foundry-based exploit reproduction tracked as a first-class action per finding

---

## Architecture at a glance

```
┌────────────────────────────────────────────────────────────────┐
│  FRONTEND LAYER · Next.js 15 + TypeScript + Tailwind 4         │
│                                                                │
│   Library  ·  Finding Workspace  ·  Hunt Mode  ·  Recommend.   │
└──────────────────────────────┬─────────────────────────────────┘
                               │  REST + WebSocket
┌──────────────────────────────┴─────────────────────────────────┐
│  API LAYER · FastAPI + SQLAlchemy 2.0 async                    │
│  Auth · CRUD · Aggregation · Search · ML proxy                 │
└──────────────────────────────┬─────────────────────────────────┘
                               │
┌──────────────────────────────┴─────────────────────────────────┐
│  DATA LAYER                                                    │
│   Postgres 16 (relational + pgvector) · Redis 7 (cache, queue) │
└──────────────────────────────┬─────────────────────────────────┘
                               │
┌──────────────────────────────┴─────────────────────────────────┐
│  WORKERS · ML · INGESTION                                      │
│                                                                │
│   Ingestion fetchers (Solodit, Immunefi, rekt, HackLabs, C4,   │
│   Sherlock) · Embedder (sentence-transformers) · Classifier    │
│   (DistilBERT) · Recommender (LightGBM + SHAP)                 │
└────────────────────────────────────────────────────────────────┘
```

Single source of truth: Postgres. Embeddings live in pgvector in the same database. The whole stack runs locally via `docker compose up`. Local-first; deployment is optional.

---

## Methodological foundation

Six analytical methodologies, applied as overlays to every finding studied and every protocol hunted:

- **STPA (Systems-Theoretic Process Analysis)** — control structure, unsafe control actions, loss scenarios
- **FMEA (Failure Mode and Effects Analysis)** — components, failure modes, severity × occurrence × detection
- **FTA (Fault Tree Analysis)** — top event decomposition into intermediate failures
- **HAZOP (Hazard and Operability Study)** — guideword × parameter deviation analysis
- **Bow-Tie** — threats, top event, consequences, with barriers between
- **STRIDE/DREAD** — threat modelling with damage/reproducibility/exploitability scoring

These are paired with two project-specific frameworks:

- **Four-question decomposition** — aim, steps, flaws, mitigation, plus the invariant overlay (what was intended, what was checked, what was violated)
- **Five-archetype classification (A1–A5)** — dead component, wrong output, misintegrated, missing component, wrongly designed component

Methodology fills are stored as JSONB documents against a JSON Schema that lives in the database. New methodologies can be added without code changes.

---

## Design principles

Six commitments that govern day-to-day decisions:

1. **One source of truth.** Postgres holds canonical state including embeddings. No separate vector store.
2. **Idempotent ingestion.** Every fetcher is safe to re-run. Deduplication by content hash plus source URL.
3. **Methodology overlays are data, not code.** Adding a methodology is a database insert, not a deployment.
4. **Reasoning visible.** Every ranking or score is accompanied by feature attribution. No black-box outputs.
5. **Replication is a first-class action.** Reproduction status is tracked per finding; Foundry repos can be attached.
6. **Notes are sacred.** Per-entity markdown notes auto-save, are full-text indexed, and support cross-references.

The architectural commitment that makes all of these survivable: **schema flexibility over schema purity.** Discovery-phase fields live in JSONB columns; they get promoted to typed columns only after access patterns stabilise.

---

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | Next.js 15 + React 19 + TypeScript + Tailwind 4 | Industry-standard for the quant pivot, Server Components for data-heavy views |
| Auth | Auth.js v5 (next-auth@5) | Battle-tested; feature-flagged single-user mode from day one |
| Backend | FastAPI + SQLAlchemy 2.0 async + Pydantic v2 | Async-first, automatic OpenAPI, native ML integration |
| Database | Postgres 16 + pgvector | Single source of truth; full-text search and vector similarity in one query |
| Cache/Queue | Redis 7 | Job queue (LPUSH/BLPOP) and cache |
| Background jobs | APScheduler → Celery | Simple in-process now; isolated workers when scale demands |
| ML — embeddings | sentence-transformers (all-mpnet-base-v2) | Strong general-purpose 768-dim embeddings |
| ML — classifier | Rule-based → zero-shot → DistilBERT | Phases of fidelity as labelled data accumulates |
| ML — recommender | Heuristic → LightGBM + SHAP | Gradient boosting fits the data shape and the reasoning requirement |
| Reproduction | Foundry (forge) | Standard in the audit community |
| Web3 | web3.py + Alchemy/Infura RPC + Tenderly traces | Trace decoding matters for hunt workspace |
| Containerisation | Docker + docker-compose | Local-first; deployment optional |
| Monorepo | pnpm workspaces + Turborepo | Mixed JS/Python; Turborepo orchestrates both via package.json shims |
| Python tooling | uv + ruff + mypy | uv is the modern standard; ruff replaces black/isort/flake8 |
| Observability | structlog + Sentry | Structured logging; error tracking when relevant |

---

## Phase plan

The build is sequenced so each phase produces something useful on its own. ML appears late, after enough manually labelled data exists to make it work.

| Phase | Scope | Calendar target |
|---|---|---|
| **0** | Scaffolding — repo, Docker, auth flag, single-user, worker plumbing | 4–6 days |
| **1** | Manual library + finding workspace + first methodology overlays | 10–12 days |
| **2** | Full methodology overlays (STPA, FMEA, FTA, HAZOP, Bow-Tie, STRIDE) | 6–8 days |
| **3** | Ingestion (Solodit, Immunefi, rekt, HackLabs, C4, Sherlock) | 14–18 days |
| **4** | Embeddings + semantic search + related findings — *v1 useful* | 6–8 days |
| **5** | Classifier (rule-based → zero-shot → DistilBERT) | 10–14 days |
| **6** | Hunt workspace with archetype-primary cross-reference | 10–14 days |
| **7** | Recommender (heuristic → LightGBM + SHAP) with daily digest | 14–20 days |

Total to feature-complete v1: roughly four months of focused work. End of Phase 4 produces a tool that's useful daily even without ML.

Project tracking lives in Linear (workspace: Bug Bounty Platform, team: Platform). Each phase corresponds to a Linear Project; issues map to commits via the standard `Closes PLAT-N` convention.

---

## Quick start

Assumes WSL2 + Ubuntu 24.04, Docker Desktop with WSL integration, Node 20+ via nvm, Python 3.12, and uv installed. See [environment setup notes](#environment) below if any of these are missing.

```bash
# 1. Clone (use SSH; place in Linux filesystem, NOT /mnt/c/)
cd ~/projects
git clone git@github.com:<your-username>/bug-bounty-platform.git
cd bug-bounty-platform

# 2. Set up environment
cp .env.example .env
# Edit .env: set JWT_SECRET and AUTH_SECRET to random strings
# Generate with: openssl rand -hex 32

# 3. Install dependencies
pnpm install
cd apps/api && uv sync && cd ../..
cd workers/runner && uv sync && cd ../..

# 4. First-time database setup
docker compose -f infra/docker-compose.yml up -d postgres redis
cd migrations && uv run alembic upgrade head && cd ..
uv run python scripts/seed_default_user.py "Your Name" "your@email.com"

# 5. Run everything
docker compose -f infra/docker-compose.yml up

# Visit http://localhost:3000
```

### Verifying the stack works

```bash
curl http://localhost:8000/health
# {"status":"ok","version":"0.1.0"}

curl http://localhost:8000/me
# Returns the default user as JSON

curl -X POST http://localhost:8000/worker/test \
  -H "Content-Type: application/json" \
  -d '{"message":"hello"}'
# Returns {"job_id":"..."} immediately
# Within 5 seconds, worker logs: DUMMY_LOG: hello
```

---

## Project structure

```
bug-bounty-platform/
├── apps/
│   ├── web/                    # Next.js 15 frontend
│   │   ├── app/                # App Router pages
│   │   ├── lib/                # Auth.js config, API client
│   │   └── package.json
│   │
│   └── api/                    # FastAPI backend (Python)
│       ├── src/
│       │   ├── main.py         # FastAPI app entrypoint
│       │   ├── config.py
│       │   ├── db.py
│       │   ├── auth/
│       │   ├── models/
│       │   ├── routes/
│       │   └── workers/
│       ├── tests/
│       ├── pyproject.toml
│       └── package.json        # Turborepo shim
│
├── packages/
│   ├── shared-types/           # TypeScript types from OpenAPI
│   └── ui/                     # Shared React components (shadcn/ui based)
│
├── workers/
│   ├── runner/                 # Background job runner (Python)
│   │   ├── src/
│   │   │   ├── main.py         # BLPOP loop
│   │   │   └── jobs/           # Job handlers
│   │   ├── pyproject.toml
│   │   └── package.json
│   ├── ingestion/              # Source fetchers (Phase 3+)
│   └── ml/                     # ML inference jobs (Phase 4+)
│
├── migrations/                 # Alembic migrations (shared)
│   ├── alembic.ini
│   └── versions/
│
├── infra/
│   ├── docker-compose.yml
│   ├── Dockerfile.api
│   ├── Dockerfile.web
│   ├── Dockerfile.worker
│   └── postgres/init.sql       # pgvector extension setup
│
├── scripts/
│   ├── seed_default_user.py
│   └── generate_types.sh       # OpenAPI → TypeScript
│
├── docs/                       # Architecture and design notes
├── .env.example
├── pnpm-workspace.yaml
├── turbo.json
└── package.json                # Workspace root
```

---

## Development workflow

### Day-to-day

1. Pick an issue from the current Linear cycle. Read its acceptance criteria.
2. Create a branch — Linear suggests the name automatically: `kamal/plat-42-add-findings-migration`
3. Work. Commit small. Push.
4. Open a PR with `Closes PLAT-42` in the description.
5. CI runs. Self-review the diff. Merge with squash.
6. Linear issue auto-closes. Next.

Branch names containing the issue ID auto-link to Linear. PR descriptions with `Closes PLAT-N` auto-transition issues from In Review → Done on merge.

### Code conventions

- **TypeScript**: strict mode, no `any` without a comment justifying it. Imports auto-sorted by Prettier.
- **Python**: ruff for linting and formatting, mypy strict mode. Type hints on every function signature.
- **Commits**: imperative mood, present tense. "Add findings migration", not "Added findings migration."
- **PR descriptions**: what changed, why, and how to verify. The acceptance criteria from the linked issue serve as the verification list.
- **Tests**: every PR adds or modifies at least one test. Phase 0 sets the CI bar low (empty test suites pass); subsequent phases raise it.

### Database changes

All schema changes go through Alembic:

```bash
cd migrations
uv run alembic revision -m "add findings table" --autogenerate
# Review the generated migration, edit if needed
uv run alembic upgrade head
```

JSONB-heavy schema design is deliberate — fields in active discovery live in JSONB columns and graduate to typed columns only when access patterns stabilise.

### Running tests

```bash
# All tests, all packages
pnpm test

# Just the API
cd apps/api && uv run pytest

# Just the frontend
cd apps/web && pnpm test

# With coverage
cd apps/api && uv run pytest --cov=src
```

### Linting and formatting

```bash
# All packages
pnpm lint
pnpm format

# Python services specifically
cd apps/api && uv run ruff check . && uv run ruff format .
cd apps/api && uv run mypy src
```

---

## Environment

The setup assumes:

- **OS**: Windows 11 with WSL2 + Ubuntu 24.04, or native Linux/macOS
- **Editor**: Cursor (with WSL extension if on Windows)
- **Container runtime**: Docker Desktop with WSL2 integration enabled
- **Node**: v20 LTS or newer, installed via nvm
- **Python**: 3.12 (pinned via `.python-version`); uv handles the venv
- **Package managers**: pnpm 9+, uv (latest)

Full setup notes including SSH key configuration and verification commands are in `docs/environment-setup.md`.

---

## Methodological references

The framework underlying this platform draws from several disciplines and named methodologies. Worth understanding before contributing:

- **Leveson, N.** — *Engineering a Safer World* (STAMP/STPA foundation)
- **Kletz, T.** — *Hazop and Hazan* (HAZOP origins)
- **Perrow, C.** — *Normal Accidents* (systems theory)
- **NIST SP 800-160 Vol. 2** — systems security engineering
- **Solodit's structured taxonomy** — DeFi-specific vulnerability classification
- **Immunefi V2.3 severity classification** — economic-impact-based severity framework

Internal design documents in `docs/`:

- `bug-hunting-framework.html` — the conceptual framework this platform operationalises
- `platform-design-plan.md` — the architectural decisions and rationale
- `phase-0-scaffolding.md` — initial phase specification and acceptance criteria

---

## What's not here yet, by design

For clarity on scope, these are deliberately out of v1:

- Public deployment infrastructure (local-first; cloud is optional)
- Multi-user authentication flow (scaffolded but feature-flagged off)
- Submission integration with bounty platforms (manual submission only)
- Real-time collaboration features
- Mobile-responsive UI (desktop-first; mobile is post-v1)
- Custom on-chain monitoring (use existing tools like Tenderly Alerts)
- Smart contract decompilation (use existing tools like Heimdall)

The principle: this platform supports the *thinking* part of vulnerability research, not the execution part where mature tools already exist.

---

## Status

**Phase 0 — Scaffolding.** Repo structure, Docker, auth feature flag, worker plumbing. In progress.

Track current work in [Linear](https://linear.app/) under the Platform team.

---

## License

UNLICENSED — private project. Not for redistribution.

---

## Contact

Author: Kamal — pivoting from cybersecurity research into quantitative finance, building this as both working tool and portfolio artifact.

For substantial questions about the methodology or architecture, see `docs/` first. The bug-hunting framework HTML in particular contains 10 sections of conceptual grounding that this platform implements.
