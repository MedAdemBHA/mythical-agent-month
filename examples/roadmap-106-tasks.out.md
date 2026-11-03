# Output: `python3 skills/mythical-agent-month/scripts/totals.py examples/roadmap-106-tasks.json`

**Tasks:** 106 (40 with a reviewer agent) · parallel cap 6, effective 1.8

| Part | Value |
|------|-------|
| Agent work (all agents, incl. 20% failure tax) | 55.9 agent-hours |
| Critical path | 19.2 h over 32 tasks |
| **Agent wall-clock** | **31.1 h** (range 17-78 h) · 1.6 days at 20 h/day |
| Human: review + local setup | 7.8 h · 1.3 focus days |
| Usage | ~34% of a weekly limit (0.6 weeks of budget at 60% available) |

**Calendar to ready-to-merge:** decisions up front 2.9 days · batched 4.9 days · one by one 6.1 days
**For comparison only:** one developer without AI ~941 days · a team of 4 ~235 days

_Held-out error on the reference run: agent-hours -24%, wall-clock -37% (later phases ran slower). Until you calibrate, plan on the upper half of the range._

**Critical path:** t001 → t002 → t003 → t005 → t014 → t015 → t020 → t021 → t035 → t040 → t041 → t044 → ...

_Throughput-bound: more effective parallelism (test slots, fewer file conflicts) shortens this, not faster agents._

**Unblock first:**
- Which plan limits apply to each tier? (owner: product owner, blocks 1 task)
- Who runs the production migrations, and when? (owner: client, blocks 1 task)
