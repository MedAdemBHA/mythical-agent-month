# Output: `python3 skills/mythical-agent-month/scripts/totals.py examples/roadmap-106-tasks.json`

**Tasks:** 106 (40 with a reviewer agent) · parallel cap 6, effective 1.8

| Part | Value |
|------|-------|
| Agent work (all agents, incl. 20% failure tax) | 65.5 agent-hours |
| Critical path | 21.7 h over 32 tasks |
| **Agent wall-clock** | **36.4 h** (range 13-66 h) · 1.8 days at 20 h/day |
| Human: review + local setup | 7.8 h · 1.3 focus days |
| Usage | ~39% of a weekly limit (0.7 weeks of budget at 60% available) |

**Calendar to ready-to-merge:** decisions up front 3.1 days · batched 5.1 days · one by one 6.4 days
**For comparison only:** one developer without AI ~536 days · a team of 4 ~134 days

**Critical path:** t001 → t002 → t003 → t005 → t014 → t015 → t020 → t021 → t035 → t040 → t041 → t044 → ...

_Throughput-bound: more effective parallelism (test slots, fewer file conflicts) shortens this, not faster agents._

**Unblock first:**
- Which plan limits apply to each tier? (owner: product owner, blocks 1 task)
- Who runs the production migrations, and when? (owner: client, blocks 1 task)
