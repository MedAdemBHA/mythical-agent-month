# Real runs

Reference cases with measured numbers. Add your own: one section per run, in the same shape.

## Run 1: multi-repo SaaS roadmap, autonomous build (2026)

**Scope:** plans, permissions, usage limits, billing and lifecycle for an existing multi-tenant SaaS.

- 7 repos: Node/Express API, Python AI service, three React front-ends, docs.
- 617 roadmap items, regrouped into **151 feature-sized tasks** in 9 phases. Grouping keeps one task = one feature in one repo; it cut the per-task overhead of 600+ tiny tasks.
- Scope rules: 106 tasks built; 45 deferred by the owner (out of scope for this release); 5 blocked on owner decisions.

**Setup:**

- one dependency-driven workflow script;
- one git worktree per lane, with a pool of 5 worktrees for the busiest repo;
- a file-conflict map so tasks on the same files never ran together;
- tests written first; per-task gate = unit tests + related tests;
- integration suites only at phase end;
- a big model with a reviewer agent on high-risk tasks, a small model on the rest;
- fast-forward merges behind a per-repo lock;
- limits: 6 agents max, 3 test slots, 10-min test timeout.
- Machine: one laptop (8 cores, low free disk), local Docker for DBs and cache.

**Measured** (from 398 subagent transcripts):

| Metric | Value |
|--------|-------|
| Agent-hours (all agents) | 64.2 |
| Wall-clock span | 36.5 h (35.3 h busy) |
| Effective parallelism | 1.82 (cap 6) |
| Code agents | 171 runs, 43 h; median 14 min for real work |
| Reviewer agents | 39 runs, 6.1 h, median 8 min |
| Merges | 96 runs, 2.2 h |
| Phase checks + final reviews | 50 runs, 7.6 h |
| Fix-up / orchestration agents | 25 runs, 5.2 h |
| Retries | 8-13% of tasks needed a second try |
| Critical path (estimated) | ~22 h over 32 tasks |
| Usage | ~35-40% of one weekly limit |
| Human after the build | ~3 h: migrations, seed data, test logins, 2 bug fixes |

**What a naive AI estimate said:** "about 5 months", i.e. 60-100 working days. The skill's own no-AI comparison line for this graph: ~134 days for a team of 4.

**What this skill predicts** from the same task graph (`examples/roadmap-106-tasks.json`):

- 65.5 agent-hours;
- **36.4 h wall-clock**;
- ~39% of a weekly limit;
- 3-6 calendar days to ready-to-merge.

The real run: 64.2 agent-hours, 35.3 h busy wall-clock.

**Incidents and what they cost:**

| Incident | Cost | Lesson |
|----------|------|--------|
| A loader dropped "blocked" statuses and a skip cascaded through dependents | ~2 h, and a re-run | Copy statuses exactly; "evidence pending" is not "blocked" |
| Lane-level locking serialised the busiest repo | Most of a phase at 1× parallelism | Use a worktree pool + a file-conflict map, not one lane per repo |
| Soft phase gates let tasks start before their base code existed | Retries | Keep hard deps on phase close |
| Related-test runs (245-339 suites) exceeded the 10-min tool timeout | Repeated gate failures | Chunk test runs; run long ones in the background |
| Reviewer fixes refused by a permission rule (`commit --amend`) | Re-runs | Reviewers add a separate fix commit |
| Integration regressions found only at phase end (8 suites, 3 real 500s) | 1 fix agent, ~1 h | Phase-end integration catches what per-task gates miss |
| Disk filled with 55 leftover in-memory DB folders (4 GB) | Test DB crashes, hours | Clean temp DB folders between phases; watch free disk |
| Docker froze under memory pressure | ~1 h | Budget RAM for test slots |

**Real bugs caught before merge:**

- a rollback that didn't roll back;
- a price-migration notice sent to the wrong group;
- lifecycle routes answering 500;
- an operator screen missing its DB model, found only during local click-through;
- role and filter endpoints returning 500.

All of them were in high-risk areas, which is why high-risk tasks keep the reviewer and the bigger test budget.

**Takeaways:**

1. Agents cut build time to hours; the calendar is set by tests, decisions and usage.
2. Expect effective parallelism of about 0.3 × the cap.
3. The human tail (local setup, click-through, decisions) is small in hours but sets the calendar.
