# Output: `python3 skills/mythical-agent-month/scripts/totals.py examples/agent-feature.json`

**Tasks:** 8 (2 with a reviewer agent) · parallel cap 4, effective 1.5

| Part | Value |
|------|-------|
| Agent work (all agents, incl. 20% failure tax) | 4.2 agent-hours |
| Critical path | 2.8 h over 5 tasks |
| **Agent wall-clock** | **3.5 h** (range 2-5 h) · 0.2 days at 20 h/day |
| Human: review + local setup | 2.2 h · 0.4 focus days |
| Usage | ~3% of a weekly limit (0.1 weeks of budget at 50% available) |

**Calendar to ready-to-merge:** decisions up front 0.5 days · batched 2.5 days · one by one 3.3 days
**For comparison only:** one developer without AI ~28 days · a team of 4 ~7 days

**Critical path:** t1 → t2 → t4 → t7 → t8

_Path-bound: split or reorder the critical-path tasks; more agents will not help._

**Unblock first:**
- Do pending invites count against the seat limit? (owner: product, blocks 1 task)
- Can a member invite, or only admins? (owner: product, blocks 1 task)
