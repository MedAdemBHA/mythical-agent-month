# Output: `python3 skills/mythical-agent-month/scripts/totals.py examples/agent-feature.json`

**Tasks:** 8 (2 with a reviewer agent) · parallel cap 4, effective 1.5

| Part | Value |
|------|-------|
| **Agent wall-clock: Plan (likely × 1.3, not yet calibrated)** | **4 h** · likely 2.8 h · range 2-5 h · 0.2 days at 20 h/day |
| Agent work (all agents, incl. 20% failure tax) | plan 4 agent-hours · likely 3.2 |
| Critical path | 2.4 h over 5 tasks |
| Human: review + local setup | 2.2 h · 0.4 focus days |
| Usage | ~2% of a weekly limit (0.0 weeks of budget at 50% available) |

**Calendar to ready-to-merge:** decisions up front 0.5 days · batched 2.5 days · one by one 3.3 days
**For comparison only, without AI (unmeasured baseline):** one developer ~17-29 days · a team of 4 ~4-7 days

_Held-out error on the reference run: agent-hours -24%, wall-clock -37% (later phases ran slower). Plan = likely x 1.3 until you calibrate._

**Critical path:** t1 → t2 → t4 → t7 → t8

_Path-bound: split or reorder the critical-path tasks; more agents will not help._

**Unblock first:**
- Do pending invites count against the seat limit? (owner: product, blocks 1 task)
- Can a member invite, or only admins? (owner: product, blocks 1 task)
