# Output: `python3 skills/mythical-agent-month/scripts/totals.py examples/roadmap-106-tasks.json`

**Tasks:** 106 (40 with a reviewer agent) · parallel cap 6, effective 1.8

| Part | Value |
|------|-------|
| **Agent wall-clock: Plan (likely × 1.3, not yet calibrated)** | **40 h** · likely 31.1 h · range 17-78 h · 2.0 days at 20 h/day |
| Agent work (all agents, incl. 20% failure tax) | plan 73 agent-hours · likely 55.9 |
| Critical path | 19.2 h over 32 tasks |
| Human: review + local setup | 7.8 h · 1.3 focus days |
| Usage | ~44% of a weekly limit (0.7 weeks of budget at 60% available) |

**Calendar to ready-to-merge:** decisions up front 3.3 days · batched 5.3 days · one by one 6.6 days
**For comparison only, without AI (unmeasured baseline):** one developer ~575-941 days · a team of 4 ~144-235 days

_Held-out error on the reference run: agent-hours -24%, wall-clock -37% (later phases ran slower). Plan = likely x 1.3 until you calibrate._

**Critical path:** t001 → t002 → t003 → t005 → t014 → t015 → t020 → t021 → t035 → t040 → t041 → t044 → ...

_Throughput-bound: more effective parallelism (test slots, fewer file conflicts) shortens this, not faster agents._

**Unblock first:**
- Which plan limits apply to each tier? (owner: product owner, blocks 1 task)
- Who runs the production migrations, and when? (owner: client, blocks 1 task)
