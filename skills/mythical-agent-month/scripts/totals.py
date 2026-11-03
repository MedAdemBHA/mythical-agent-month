#!/usr/bin/env python3
"""Mythical Agent Month: estimate totals. Prints Markdown.

Usage:
  python3 totals.py estimate.json            # mode is read from the file ("dev" or "agent")
  python3 totals.py estimate.json --json     # machine-readable totals

Mode "dev" (a developer working with an AI assistant):
{
  "mode": "dev",
  "focus_hours_per_day": 6,
  "items": [
    {"id": 1, "task": "Stripe credit packs", "size": "M", "risk": "high",
     "build": [3, 6, 10], "test": [8, 14, 24], "buffer_pct": 0.25, "decisions": ["d1"]}
  ],
  "decisions": [{"id": "d1", "question": "Which pack sizes?", "owner": "PM", "wait_days": [1, 3]}]
}
build and test are [low, likely, high] hours. buffer_pct is a fraction.

Mode "agent" (autonomous agents build the tasks; a human decides and reviews):
{
  "mode": "agent",
  "machine": {"parallel_agents": 6, "effective_parallelism": 1.8, "agent_hours_per_day": 20},
  "review": "high-risk",          # which tasks get a separate reviewer agent: "none" | "high-risk" | "all"
  "phase_checks": 9,              # full-suite checks between phases (count)
  "failure_tax": 0.20,            # retries, reruns, broken gates (0.15-0.25)
  "human": {"focus_hours_per_day": 6, "review_minutes_per_task": 3, "local_setup_hours": [2, 3]},
  "usage": {"weekly_pct_per_agent_hour": 0.6, "weekly_pct_available": 60},
  "items": [
    {"id": "t1", "task": "Plan catalog model", "size": "M", "risk": "high", "model": "opus",
     "depends_on": [], "minutes": [10, 25, 50], "decisions": ["d1"]}
  ],
  "decisions": [...same as dev mode...]
}
"minutes" per item is optional; without it the size x risk table below is used.
All defaults are seeded from one real run (see references/real-runs.md). Calibrate them with calibrate.py.
"""
import json
import sys

# Agent minutes per task, [low (p25), likely (median), high (p90)], normal risk, incl. the agent's own gate tests.
# Measured on run 1 (references/real-runs.md), not hand-tuned. Size by file count was a weak signal there;
# risk was the strong one.
AGENT_MINUTES = {"XS": [2, 4, 15], "S": [3, 5, 25], "M": [5, 10, 35], "L": [7, 12, 40]}
RISK_MULT = {"low": 0.3, "normal": 1.0, "high": 2.7}   # measured medians vs normal risk
REVIEW_MINUTES = [4, 8, 26]      # separate reviewer agent per reviewed task (median 8.4)
MERGE_MINUTES = 1                # merge agent / scripted merge per task (mean 1.2)
PHASE_CHECK_MINUTES = 12         # full suites + fix-ups between phases (mean 12.2)
# Held-out test on run 1 (fit on phases 0-3, predict 4-9): agent-hours -24%, wall-clock -37%.
# Until calibrated, the bold "Plan" number is likely x 1.3. On run 1 that lands at +14% in-sample and -19% held-out
# (versus -12% / -37% for the raw likely value). Set "calibrated": true, or give per-task minutes, to plan on likely.
PLAN_FACTOR = 1.3
HOLDOUT_NOTE = ("Held-out error on the reference run: agent-hours -24%, wall-clock -37% (later phases ran slower). "
                "Plan = likely x 1.3 until you calibrate.")

# Developer + AI hours, [low, likely, high] (build only; test is a multiple by risk)
DEV_BUILD_HOURS = {"XS": [0.25, 0.5, 1], "S": [1, 2, 4], "M": [3, 6, 10], "L": [8, 14, 24]}
DEV_TEST_MULT = {"low": 0.5, "normal": 1.0, "high": 2.5}
# No-AI comparison, an UNMEASURED baseline: build 2-3x slower without AI, review and test 1-1.5x, plus 10-20%
# coordination. Printed as a wide range and never as the estimate.
NO_AI_LOW = (2.0, 1.0, 1.1)
NO_AI_HIGH = (3.0, 1.5, 1.2)


def pert(r):
    low, likely, high = r
    return (low + 4 * likely + high) / 6


def r1(x):
    return round(x * 2) / 2


def decision_calendar(decisions):
    waits = [(d["wait_days"][0] + d["wait_days"][1]) / 2 for d in decisions.values()]
    return (max(waits) if waits else 0), sum(waits), waits


def unblock_first(items, decisions):
    blocks = {}
    for it in items:
        for d in it.get("decisions", []):
            blocks[d] = blocks.get(d, 0) + 1
    out = []
    for did, n in sorted(blocks.items(), key=lambda x: -x[1]):
        d = decisions.get(did)
        if d:
            out.append(f"- {d['question']} (owner: {d.get('owner', '?')}, blocks {n} task{'s' if n > 1 else ''})")
    return out


def human_team_days(items, team_size=1):
    """No-AI comparison range (low, high) in days, never the estimate. One baseline for both modes: it uses only
    each task's size and risk (never the input build/test hours, which are AI-assisted), so the same task list
    gives the same range in dev mode and agent mode. Unmeasured: show it as a range, keep it out of headlines."""
    out = []
    for bx, tx, cx in (NO_AI_LOW, NO_AI_HIGH):
        total = 0
        for it in items:
            size = it.get("size", "M")
            if size not in DEV_BUILD_HOURS:
                size = "L"
            b = pert(DEV_BUILD_HOURS[size])
            t = b * DEV_TEST_MULT.get(it.get("risk", "normal"), 1)
            total += (b * bx + t * tx) * cx
        out.append(total / 6 / team_size)
    return tuple(out)


# ---------------------------------------------------------------- dev mode
def mode_dev(data, as_json):
    fh = data.get("focus_hours_per_day", 6)
    items = data["items"]
    decisions = {d["id"]: d for d in data.get("decisions", [])}
    rows, tb, tt, tbuf = [], 0, 0, 0
    lo = hi = 0
    for it in items:
        size = it.get("size", "M")
        build = it.get("build", DEV_BUILD_HOURS.get(size, DEV_BUILD_HOURS["L"]))
        test = it.get("test", [x * DEV_TEST_MULT.get(it.get("risk", "normal"), 1) for x in build])
        b, t = pert(build), pert(test)
        buf = (b + t) * it.get("buffer_pct", 0.25)
        tb, tt, tbuf = tb + b, tt + t, tbuf + buf
        lo += build[0] + test[0]
        hi += build[2] + test[2]
        qs = "; ".join(decisions[d]["question"] for d in it.get("decisions", []) if d in decisions)
        rows.append(f"| {it['id']} | {it['task']} | {size} | {it.get('risk', '')} | {r1(b)} | {r1(t)} | {r1(buf)} | {qs or '-'} |")
    effort_h = tb + tt + tbuf
    effort_d = effort_h / fh
    batched_w, serial_w, _ = decision_calendar(decisions)
    human = human_team_days(items)
    res = {"effort_hours": round(effort_h, 1), "effort_days": round(effort_d, 1),
           "calendar_days": [round(effort_d, 1), round(effort_d + batched_w, 1), round(effort_d + serial_w, 1)],
           "solo_no_ai_days_range": [round(human[0]), round(human[1])]}
    if as_json:
        print(json.dumps(res, indent=1))
        return
    print("| # | Task | Size | Risk | Build (h) | Review & test (h) | Buffer (h) | Decision needed |")
    print("|---|------|------|------|-----------|-------------------|------------|-----------------|")
    print("\n".join(rows))
    print()
    print("| Part | Hours | Days |")
    print("|------|-------|------|")
    print(f"| Build with AI | {r1(tb)} | {tb / fh:.1f} |")
    print(f"| Review and test | {r1(tt)} | {tt / fh:.1f} |")
    print(f"| Risk buffer | {r1(tbuf)} | {tbuf / fh:.1f} |")
    print(f"| **Effort total** (range {r1(lo)}-{r1(hi * 1.25)} h) | **{r1(effort_h)}** | **{effort_d:.1f}** |")
    print(f"| Waiting on decisions | n/a | {len(decisions)} decisions, see calendar |")
    print()
    print(f"**Calendar:** decisions up front {effort_d:.1f} days · batched {effort_d + batched_w:.1f} days · "
          f"one by one {effort_d + serial_w:.1f} days")
    print(f"**For comparison only, one developer without AI:** ~{human[0]:.0f}-{human[1]:.0f} days (unmeasured baseline)")
    ub = unblock_first(items, decisions)
    if ub:
        print("\n**Unblock first:**")
        print("\n".join(ub))


# ---------------------------------------------------------------- agent mode
def agent_minutes(it):
    if "minutes" in it:
        return pert(it["minutes"]), it["minutes"][0], it["minutes"][2]
    size = it.get("size", "M")
    if size == "XL":
        print(f"warning: {it['id']} is XL; split it. Counted as 2 x L.", file=sys.stderr)
        base = [2 * x for x in AGENT_MINUTES["L"]]
    else:
        base = AGENT_MINUTES.get(size, AGENT_MINUTES["M"])
    m = RISK_MULT.get(it.get("risk", "normal"), 1.0)
    rng = [x * m for x in base]
    return pert(rng), rng[0], rng[2]


def mode_agent(data, as_json):
    items = data["items"]
    byid = {it["id"]: it for it in items}
    decisions = {d["id"]: d for d in data.get("decisions", [])}
    machine = data.get("machine", {})
    cap = machine.get("parallel_agents", 6)
    eff = min(cap, machine.get("effective_parallelism", max(1.0, 0.3 * cap)))
    agent_h_day = machine.get("agent_hours_per_day", 20)
    review = data.get("review", "high-risk")
    tax = data.get("failure_tax", 0.20)
    human = data.get("human", {})
    fh = human.get("focus_hours_per_day", 6)
    usage = data.get("usage", {})

    dur, lo_sum, hi_sum, code_m, review_m = {}, 0, 0, 0, 0
    reviewed = 0
    for it in items:
        m, lo, hi = agent_minutes(it)
        r = 0
        if review == "all" or (review == "high-risk" and it.get("risk") == "high"):
            r = pert(REVIEW_MINUTES)
            reviewed += 1
        code_m += m
        review_m += r
        lo_sum += lo
        hi_sum += hi
        dur[it["id"]] = (m + r + MERGE_MINUTES) * (1 + tax)

    missing = sorted({d for it in items for d in it.get("depends_on", []) if d not in byid})
    if missing:
        print(f"warning: unknown depends_on ids ignored: {', '.join(missing[:10])}", file=sys.stderr)

    # earliest finish per task, in topological order (Kahn), so big DAGs stay linear
    deps_of = {t: [d for d in byid[t].get("depends_on", []) if d in byid] for t in byid}
    indeg = {t: len(deps_of[t]) for t in byid}
    users = {t: [] for t in byid}
    for t, ds in deps_of.items():
        for d in ds:
            users[d].append(t)
    ready = [t for t in byid if indeg[t] == 0]
    fin = {}
    while ready:
        t = ready.pop()
        fin[t] = dur[t] + max((fin[d] for d in deps_of[t]), default=0)
        for u in users[t]:
            indeg[u] -= 1
            if indeg[u] == 0:
                ready.append(u)
    if len(fin) != len(byid):
        raise SystemExit("dependency cycle among: " + ", ".join(t for t in byid if t not in fin)[:200])
    finish = fin.__getitem__
    cp_min = max(fin.values(), default=0)
    end = max(byid, key=finish) if byid else None
    path = []
    while end:
        path.append(end)
        deps = [d for d in byid[end].get("depends_on", []) if d in byid]
        end = max(deps, key=finish) if deps else None
    path.reverse()

    merge_m = MERGE_MINUTES * len(items)
    phase_m = data.get("phase_checks", 0) * PHASE_CHECK_MINUTES
    work_m = (code_m + review_m + merge_m) * (1 + tax) + phase_m
    work_h = work_m / 60
    wall_h = max(cp_min / 60 + phase_m / 60, work_h / eff)
    # same formula at the low and high ends: every agent kind is in both, only task minutes and tax move
    lo_work_h = ((lo_sum + REVIEW_MINUTES[0] * reviewed + merge_m) * (1 + tax * 0.5) + phase_m) / 60
    hi_work_h = ((hi_sum + REVIEW_MINUTES[2] * reviewed + merge_m) * (1 + max(tax, 0.25)) + phase_m) / 60
    wall_lo = max(cp_min / 60 * 0.7 + phase_m / 60, lo_work_h / eff)
    wall_hi = max(cp_min / 60 * 1.6 + phase_m / 60, hi_work_h / eff)
    calibrated = bool(data.get("calibrated")) or (bool(items) and all("minutes" in it for it in items))
    pf = 1.0 if calibrated else PLAN_FACTOR
    plan_h = min(max(wall_h * pf, wall_lo), wall_hi)
    plan_work_h = work_h * pf
    agent_days = plan_h / agent_h_day

    rev_h = human.get("review_minutes_per_task", 3) * len(items) / 60
    setup = human.get("local_setup_hours", [2, 3])
    human_h = rev_h + (setup[0] + setup[1]) / 2
    human_d = human_h / fh

    batched_w, serial_w, _ = decision_calendar(decisions)
    cal = [agent_days + human_d, agent_days + human_d + batched_w, agent_days + human_d + serial_w]

    pct_h = usage.get("weekly_pct_per_agent_hour", 0.6)
    pct = plan_work_h * pct_h
    avail = usage.get("weekly_pct_available", 100)
    weeks = pct / avail if avail else 0
    usage_wait_days = max(0, -(-pct // avail) - 1) * 7 if avail and pct > avail else 0

    solo = human_team_days(items)
    team = data.get("human_team_size", 4)

    res = {"tasks": len(items), "calibrated": calibrated, "plan_wall_clock_hours": round(plan_h, 1),
           "plan_agent_hours": round(plan_work_h, 1), "agent_hours": round(work_h, 1), "wall_clock_hours": round(wall_h, 1),
           "wall_clock_range_hours": [round(wall_lo, 1), round(wall_hi, 1)],
           "critical_path_hours": round(cp_min / 60, 1), "critical_path_tasks": len(path),
           "human_hours": round(human_h, 1), "calendar_days": [round(c, 1) for c in cal],
           "weekly_usage_pct": round(pct), "weeks_of_usage": round(weeks, 2),
           "usage_wait_days": usage_wait_days, "solo_no_ai_days_range": [round(solo[0]), round(solo[1])],
           f"team_of_{team}_no_ai_days_range": [round(solo[0] / team), round(solo[1] / team)]}
    if as_json:
        print(json.dumps(res, indent=1))
        return

    print(f"**Tasks:** {len(items)} ({reviewed} with a reviewer agent) · parallel cap {cap}, effective {eff:g}")
    print()
    print("| Part | Value |")
    print("|------|-------|")
    plan_lbl = "Plan" if calibrated else f"Plan (likely × {PLAN_FACTOR:g}, not yet calibrated)"
    print(f"| **Agent wall-clock: {plan_lbl}** | **{(f"{plan_h:.1f}" if plan_h < 10 else f"{plan_h:.0f}")} h** · likely {wall_h:.1f} h · range {wall_lo:.0f}-{wall_hi:.0f} h · {agent_days:.1f} days at {agent_h_day} h/day |")
    print(f"| Agent work (all agents, incl. {int(tax * 100)}% failure tax) | plan {plan_work_h:.0f} agent-hours · likely {work_h:.1f} |")
    print(f"| Critical path | {cp_min / 60:.1f} h over {len(path)} tasks |")
    print(f"| Human: review + local setup | {human_h:.1f} h · {human_d:.1f} focus days |")
    print(f"| Usage | ~{pct:.0f}% of a weekly limit ({weeks:.1f} weeks of budget at {avail}% available) |")
    print()
    print(f"**Calendar to ready-to-merge:** decisions up front {cal[0]:.1f} days · batched {cal[1]:.1f} days · "
          f"one by one {cal[2]:.1f} days" + (f" · +{usage_wait_days} days waiting for usage resets" if usage_wait_days else ""))
    print(f"**For comparison only, without AI (unmeasured baseline):** one developer ~{solo[0]:.0f}-{solo[1]:.0f} days · "
          f"a team of {team} ~{solo[0] / team:.0f}-{solo[1] / team:.0f} days")
    if not calibrated:
        print(f"\n_{HOLDOUT_NOTE}_")
    if len(path) > 1:
        shown = " → ".join(path[:12]) + (" → ..." if len(path) > 12 else "")
        print(f"\n**Critical path:** {shown}")
    if wall_h > cp_min / 60 * 1.5:
        print("\n_Throughput-bound: more effective parallelism (test slots, fewer file conflicts) shortens this, not faster agents._")
    else:
        print("\n_Path-bound: split or reorder the critical-path tasks; more agents will not help._")
    ub = unblock_first(items, decisions)
    if ub:
        print("\n**Unblock first:**")
        print("\n".join(ub))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    with open(args[0]) as f:
        data = json.load(f)
    as_json = "--json" in sys.argv
    mode = data.get("mode") or ("agent" if any("depends_on" in i for i in data.get("items", [])) else "dev")
    (mode_agent if mode == "agent" else mode_dev)(data, as_json)


if __name__ == "__main__":
    main()
