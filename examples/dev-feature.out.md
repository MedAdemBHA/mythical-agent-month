# Output: `python3 skills/mythical-agent-month/scripts/totals.py examples/dev-feature.json`

| # | Task | Size | Risk | Build (h) | Review & test (h) | Buffer (h) | Decision needed |
|---|------|------|------|-----------|-------------------|------------|-----------------|
| 1 | Team invites: model + API | M | high | 5.0 | 10.5 | 4.0 | Do pending invites count against the seat limit? |
| 2 | Invite email template | S | low | 1.0 | 1.0 | 0.0 | - |
| 3 | Invite screen in settings | M | normal | 4.0 | 4.0 | 2.0 | Can a member invite, or only admins? |
| 4 | Seat limit check on accept | S | high | 2.0 | 4.0 | 1.5 | Do pending invites count against the seat limit? |

| Part | Hours | Days |
|------|-------|------|
| Build with AI | 12.5 | 2.1 |
| Review and test | 19.5 | 3.2 |
| Risk buffer | 7.5 | 1.3 |
| **Effort total** (range 17.0-63.0 h) | **39.5** | **6.6** |
| Waiting on decisions | n/a | 2 decisions, see calendar |

**Calendar:** decisions up front 6.6 days · batched 8.6 days · one by one 9.3 days
**One developer without AI (approx.):** 8.9 days

**Unblock first:**
- Do pending invites count against the seat limit? (owner: product, blocks 2 tasks)
- Can a member invite, or only admins? (owner: product, blocks 1 task)
