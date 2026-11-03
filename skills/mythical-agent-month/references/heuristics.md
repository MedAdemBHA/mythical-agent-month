# Heuristics

Starting numbers only. Replace them with your own as soon as you have 5-10 finished tasks (see `calibration.md`).

## Size

| Size | Typical scope |
|------|---------------|
| XS | Config, copy, one-line fix, a flag. 1 non-test file. |
| S | One endpoint or component, following an existing pattern. 2-4 files. |
| M | A feature slice in one service: model + route + UI, or a migration. 5-12 files. |
| L | A feature across 2+ services, or a new pattern. 13+ files. |
| XL | Split it. |

## Mode A: developer + AI, hours

Build with AI = prompting, reading the generated code, fixing and wiring it in. Not typing time.

| Size | Build [low, likely, high] h |
|------|------------------------------|
| XS | 0.25 / 0.5 / 1 |
| S | 1 / 2 / 4 |
| M | 3 / 6 / 10 |
| L | 8 / 14 / 24 |

Adjust build: unfamiliar codebase ×1.5 · no existing pattern ×1.3 · no AI ×2-3.

Review and test as a multiple of build: low risk 0.5× · normal 1× · high 2-3×. Add 2-4 h per extra service touched (integration).

Risk buffer on build + test: 10% when well known, 25% normal, 50% for many unknowns.

## Mode B: autonomous agents, minutes per task

**Measured on 398 real agent runs** (see `real-runs.md`). Each figure includes the agent's own gate tests: unit tests plus tests related to the changed files.

| Size | Agent minutes, normal risk [low, likely, high] |
|------|-----------------------------------------------|
| XS | 2 / 5 / 12 |
| S | 4 / 10 / 22 |
| M | 6 / 15 / 32 |
| L | 10 / 22 / 45 |

Risk multiplier: low 0.4 · normal 1.0 · high 2.0. The real medians were 0.3× and 2.7× of normal; high-risk tasks run more tests and get a bigger model that reads more.

| Agent kind | Real median | p75 | Max | Use |
|------------|-------------|-----|-----|-----|
| Code, high risk (big model) | 30 min | 39 | 112 | |
| Code, normal risk | 11 min | 24 | 62 | |
| Code, low risk (small model) | 3.5 min | 8 | 56 | |
| Reviewer agent (big model) | 8 min | 12 | 26 | [4, 8, 26] per reviewed task |
| Merge (scripted / small model) | <1 min | <1 | 28 | 1 min per task |
| Phase check (full suites + fix) | 4 min | 20 | 89 | 20 min per check |

The long tail is real: about 1 task in 10 takes 3× the median. Ranges matter more than medians.

### Test-run cost

Gate tests are usually most of an agent's minutes. Rough model: **suites run × minutes per suite × (1 + rerun rate)**.

- Real medians: 19 test commands per high-risk task, 12 normal, 8 low.
- A full related-test run on a large Node backend took 5-15 min. Chunk it, or it hits tool timeouts (10 min is common).
- Never run two test processes in the same working tree if they share a temp DB or port.
- Cap concurrent test runs (test slots) by RAM: about 1 slot per 8-10 GB with in-memory databases.

### Parallelism

- **Cap** = CPUs − 2, or your tool's agent limit.
- **Effective** ≈ 0.3 × cap. One real run had a cap of 6, 3 test slots and per-repo merge locks, and averaged **1.8** agents busy.
- What eats parallelism:
  - tasks touching the same files (they must serialise);
  - test-slot queues;
  - merge locks per repo;
  - phase gates (everything waits for the slowest task in the phase);
  - usage brakes.
- **Wall-clock = max(critical path, agent-hours ÷ effective parallelism).** If the critical path wins, split critical tasks; more agents won't help.

### Failure tax

Add **15-25%** to agent-hours for retries (8-13% of tasks needed a second try), fix-up agents after a phase check fails, broken gates, timeouts and orchestration bugs. Use 25% for a first run of a new workflow script.

### Usage budget

- Agent-hours × **% of weekly limit per agent-hour**. Seed value: **0.6%** (64 agent-hours used about 35-40% of one weekly limit on a high-tier plan, with a big model on high-risk tasks).
- It changes a lot with plan tier and model mix, so calibrate it: note the % before and after a run.
- If the run needs more than what's left this week, the calendar includes waiting for the reset. Keep a brake: stop cleanly at a set %, put the running tasks back to todo, and resume after the reset.

### Machine profile

Disk and RAM end runs early. Budget 5-10 GB free disk for test databases and worktrees, and clean temp DB folders between phases. A frozen Docker or a full disk cost the real run several hours. Add them to the risk list on laptops.

### Post-build human costs (often forgotten)

| Item | Default |
|------|---------|
| Human skim per task commit | 2-5 min |
| Local setup: run migrations, seed demo data, test logins | 2-3 h |
| Bugs found while clicking through locally | 1-3 small fixes, ~30 min each |
| Owner decisions | see below |

## Decision waits (calendar days, never effort)

| Kind | Wait [low, high] |
|------|------------------|
| Already decided / in docs | 0 |
| Small (copy, default value) | 0.5 / 1 |
| Product rule (limits, pricing, UX) | 1 / 3 |
| Cross-team, legal, client sign-off | 3 / 10 |

Batch decisions into one session before the run. Agents can build with an ASSUMED default and log the question, so the run isn't blocked, but count the rework risk.

## No-AI comparison

Build × 2 + test (high-risk test × 1.5, not × 2.5), + 20% coordination ÷ 6 focus hours. Show solo and for a team of 4. It's a comparison line, never the estimate.
