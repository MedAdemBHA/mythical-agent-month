# Held-out test on run 1

The question: do the defaults predict work they weren't fit on? There's only one run so far, so this test splits that run by phase. It's weaker than an independent run, but it's honest.

## Method

1. **Split** the 106 built tasks by phase: **train** = phases 0-3 (66 tasks), **test** = phases 4-9 (40 tasks). Each agent run is assigned to a phase by the task id or phase tag in its label. 25 orchestration runs with no task or phase were left out of both sides.
2. **Fit on train only**, with the same procedure that produced the shipped defaults:
   - **risk multipliers** = median code minutes per risk ÷ the normal-risk median;
   - **size table** = [p25, median, p90] of risk-normalised minutes per size, where size comes from the count of non-test files;
   - **reviewer** = median minutes; **merge** and **phase check** = mean minutes;
   - **failure tax** = actual train agent-minutes ÷ the model's untaxed minutes − 1;
   - **effective parallelism** = train agent-hours ÷ train busy hours.
3. **Predict test blind** with `totals.py`'s formulas: agent-hours, and wall-clock = max(critical path + phase checks, agent-hours ÷ parallelism).
4. **Compare** against the real test agents. Busy hours = the union of their run intervals.

## Fitted on train

| Parameter | Value |
|---|---|
| Risk multipliers | low 0.27 · normal 1.0 · high 2.28 |
| Minutes XS / S / M / L (p25, median, p90) | 4/7/32 · 3.5/4.6/29.5 · 6/13/43 · 11/14/26 |
| Reviewer / merge / phase check | 8.6 / 1.9 / 6.5 min |
| Failure tax | 14% |
| Effective parallelism | 1.69 |

## Result on test (phases 4-9)

| | Predicted | Real | Error |
|---|---|---|---|
| Agent-hours | 20.9 | 27.6 | **-24%** |
| Wall-clock | 12.4 h | 19.8 h | **-37%** |
| Effective parallelism | 1.69 (from train) | 1.40 | |

## What it says

- **The model is optimistic.** Medians understate a long tail, and late phases were slower. The skill tells the agent to present the upper half of its range until the user calibrates.
- **Parallelism isn't constant.** It degraded as the machine filled up. With the real 1.4, the wall-clock error would be about -25%.
- **It's still n = 1.** Same project, same laptop, same orchestration. An independent run, especially from someone else, is the evidence that's missing.
- **You can't re-run it yet.** The per-run timing data comes from a client project and isn't published. An anonymised timing file (task id, phase, risk, size, model, start and end offsets; no content) will be added if the client agrees.
