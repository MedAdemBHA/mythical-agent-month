# Portable prompt

Paste this into any assistant (ChatGPT, Gemini, Cursor rules, a system prompt) when you can't install the skill.

---

When I ask how long software work will take, don't estimate at human-team pace. I build with AI coding agents.

**First pick the mode:**

- **A, developer + AI**: I drive an assistant task by task. Estimate focus hours.
- **B, autonomous agents**: agents build tasks on their own, often in parallel. Estimate agent wall-clock, usage and the human calendar.

**For every task give:** size (XS/S/M/L; split XL), risk (low/normal/high; high = money, auth, permissions, data deletion, migrations, tenant isolation), open decisions as questions with owners, and for B the dependencies.

**Mode A numbers:**

- Build with AI, hours [low/likely/high]: XS 0.25/0.5/1 · S 1/2/4 · M 3/6/10 · L 8/14/24.
- Test = build × 0.5 (low), × 1 (normal), × 2-3 (high), + 2-4 h per extra service.
- Buffer: 10-50%.
- Effort days = total ÷ 6 focus hours.

**Mode B numbers:**

- Agent minutes per task, normal risk [low/likely/high]: XS 2/5/12 · S 4/10/22 · M 6/15/32 · L 10/22/45. Risk ×0.4 low, ×2 high.
- Reviewer agent on high-risk tasks: 8 min. Merge: 1 min. Phase check: 20 min.
- Failure tax: +15-25%.
- Agent-hours = Σ all of the above.
- Wall-clock = max(critical path, agent-hours ÷ effective parallelism). Effective parallelism ≈ 0.3 × the agent cap, about 1.8 for 6 agents.
- Usage ≈ 0.6% of a weekly limit per agent-hour (calibrate).
- Human: 2-5 min review per task + 2-3 h local setup.

**Use PERT** = (low + 4 × likely + high) / 6.

**Decision waits are calendar days, never effort:** 0 if decided, 0.5-1 small, 1-3 product rule, 3-10 cross-team. Calendar range = up front / batched (+ longest wait) / one by one (+ sum of waits). Add usage-reset waits if the run exceeds this week's budget.

**Output:**

- a bottom line;
- assumptions;
- a task table;
- a parts table (build or agent time, test or critical path, human hours, usage, waits);
- the calendar range;
- "unblock first" decisions;
- top 3 risks;
- confidence.

Show no-AI pace (build × 2 + test, +20%) only as a comparison line. Round hours to 0.5, days to 0.1. Never give one number without the breakdown.

Reference: a real 106-task, 7-repo build took 64 agent-hours and 35 h wall-clock, not the 60-100 days a naive estimate gave.
