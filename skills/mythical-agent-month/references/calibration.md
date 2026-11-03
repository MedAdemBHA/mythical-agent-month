# Calibration

Defaults are someone else's. After 5-10 tasks, your own numbers win.

## Mode A log (developer + AI)

| Date | Task | Size | Risk | Est. build h | Actual build h | Est. test h | Actual test h | Decision wait (days) | Notes |
|------|------|------|------|--------------|----------------|-------------|---------------|----------------------|-------|

After 5-10 rows: personal build multiplier = Σ actual build ÷ Σ estimated build. Same for test. Use them in later estimates and say so in Assumptions.

## Mode B log (autonomous agents)

Generate it instead of typing it:

```bash
python3 scripts/calibrate.py ~/.claude/projects/<project>/<session>/subagents --tasks tasks.json --csv runs.csv
```

`tasks.json` maps task ids to risk and size: `{"items":[{"id":"t1","risk":"high","size":"M"}]}`. Ids are matched inside the agent labels. The script only reads timestamps, labels, model names and token counts.

| Date | Task | Size | Risk | Model | Est. min | Actual min | Gate test commands | Retries | Output tokens | Notes |
|------|------|------|------|-------|----------|------------|--------------------|---------|---------------|-------|

Seed rows from the real run in `real-runs.md` (medians per group):

| Group | n | Actual min (median) | p75 | Test commands (median) | Output tokens (median) |
|-------|---|---------------------|-----|------------------------|------------------------|
| Code / high risk / big model | 54 | 30 | 39 | 19 | ~186k |
| Code / normal risk | 52 | 11 | 24 | 12 | ~44k |
| Code / low risk / small model | 17 | 3.5 | 8 | 8 | ~27k |
| Reviewer / big model | 39 | 8 | 12 | 1-2 reruns | |
| Phase check | 50 | 1-4 | 20 | full suites | |

## What to update, and where

| You measured | Put it in |
|--------------|-----------|
| Median minutes per size | `AGENT_MINUTES` in `scripts/totals.py`, or `minutes` per task in your JSON |
| Median per risk ÷ normal | `RISK_MULT` |
| Agent-hours ÷ busy hours | `machine.effective_parallelism` |
| Retry share + fix-up agents | `failure_tax` |
| Weekly % used ÷ agent-hours | `usage.weekly_pct_per_agent_hour` |
| All of the above done | `"calibrated": true`: the plan becomes likely, and the held-out warning goes away |

Add the run to `real-runs.md` so the next estimate has a reference case.
