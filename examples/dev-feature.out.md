# Output: `python3 skills/mythical-agent-month/scripts/totals.py examples/dev-feature.json`

| # | Task | Size | Risk | Build (h) | Review & test (h) | Buffer (h) | Decision needed |
|---|------|------|------|-----------|-------------------|------------|-----------------|
| t1 | Invites: schema + migration | M | high | 6.0 | 15.5 | 5.5 | - |
| t2 | Invites: API + seat check | M | high | 6.0 | 15.5 | 5.5 | Do pending invites count against the seat limit? |
| t3 | Invite email + template | S | low | 2.0 | 1.0 | 1.0 | - |
| t4 | Settings: invite screen | M | normal | 6.0 | 6.0 | 3.0 | Can a member invite, or only admins? |
| t5 | Accept-invite page | S | normal | 2.0 | 2.0 | 1.0 | - |
| t6 | Audit log entries | XS | normal | 0.5 | 0.5 | 0.5 | - |
| t7 | E2E: invite to accept | S | normal | 2.0 | 2.0 | 1.0 | - |
| t8 | Docs + changelog | XS | low | 0.5 | 0.5 | 0.0 | - |

| Part | Hours | Days |
|------|-------|------|
| Build with AI | 26.0 | 4.3 |
| Review and test | 43.0 | 7.2 |
| Risk buffer | 17.5 | 2.9 |
| **Effort total** (range 33.5-144.5 h) | **86.5** | **14.4** |
| Waiting on decisions | n/a | 2 decisions, see calendar |

**Calendar:** decisions up front 14.4 days · batched 16.4 days · one by one 17.2 days
**For comparison only, one developer without AI:** ~17-29 days (unmeasured baseline)

**Unblock first:**
- Do pending invites count against the seat limit? (owner: product, blocks 1 task)
- Can a member invite, or only admins? (owner: product, blocks 1 task)
