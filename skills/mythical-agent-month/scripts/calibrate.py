#!/usr/bin/env python3
"""Calibrate Mythical Agent Month from your own agent runs. Read-only.

Reads subagent transcripts (agent-*.jsonl, with optional agent-*.meta.json next to them, the
layout Claude Code writes under ~/.claude/projects/<project>/<session>/subagents/) and prints:
  - real minutes per agent kind (code / review / merge / phase checks / other), by model
  - real minutes per risk class, if you pass your task list
  - wall-clock, busy time and the effective parallelism you actually got
  - suggested values for AGENT_MINUTES / RISK_MULT / effective_parallelism

Usage:
  python3 calibrate.py ~/.claude/projects/<project>/<session>/subagents
  python3 calibrate.py <logs dir> --tasks tasks.json     # tasks.json: {"items":[{"id","risk","size"}]}
  python3 calibrate.py <logs dir> --csv runs.csv          # also write one row per agent run

Only timestamps, labels, model names and token counts are read. No message content is printed.
"""
import csv
import glob
import json
import os
import re
import sys
from datetime import datetime

KINDS = [("review", r"^review"), ("merge", r"^merge"), ("phase_check", r"^(end|phase|final)"),
         ("cleanup", r"^(reset|fail|cleanup)")]


def ts(s):
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def q(v):
    v = sorted(v)
    n = len(v)
    if not n:
        return "-"
    return f"n={n} p25={v[n // 4]:.1f} median={v[n // 2]:.1f} p75={v[(3 * n) // 4]:.1f} p90={v[int(n * 0.9)]:.1f} max={v[-1]:.1f}"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        raise SystemExit(__doc__)
    root = os.path.expanduser(args[0])
    opt = {sys.argv[i]: sys.argv[i + 1] for i in range(1, len(sys.argv) - 1) if sys.argv[i].startswith("--")}
    tasks = {}
    if "--tasks" in opt:
        for it in json.load(open(opt["--tasks"]))["items"]:
            tasks[str(it["id"])] = it
    id_re = re.compile("|".join(sorted((re.escape(k) for k in tasks), key=len, reverse=True))) if tasks else None

    runs = []
    for jl in glob.glob(os.path.join(root, "**", "agent-*.jsonl"), recursive=True):
        meta_p = jl[:-len(".jsonl")] + ".meta.json"
        meta = json.load(open(meta_p)) if os.path.exists(meta_p) else {}
        label = meta.get("description", "") or os.path.basename(jl)
        stamps, out_tok = [], 0
        with open(jl, errors="replace") as f:
            for line in f:
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                t = ts(o.get("timestamp"))
                if t:
                    stamps.append(t)
                msg = o.get("message")
                if isinstance(msg, dict) and isinstance(msg.get("usage"), dict):
                    out_tok += msg["usage"].get("output_tokens") or 0
        if len(stamps) < 2:
            continue
        kind = "code" if (id_re and id_re.search(label)) else "other"
        for k, pat in KINDS:
            if re.search(pat, label):
                kind = k
        m = id_re.search(label) if id_re else None
        task = tasks.get(m.group(0), {}) if m else {}
        runs.append({"label": label, "kind": kind, "model": meta.get("model", "?"),
                     "start": min(stamps), "end": max(stamps),
                     "minutes": (max(stamps) - min(stamps)).total_seconds() / 60,
                     "out_tokens": out_tok, "risk": task.get("risk", ""), "size": task.get("size", ""),
                     "retry": bool(re.search(r"try ?[2-9]|retry", label))})
    if not runs:
        raise SystemExit(f"no agent-*.jsonl with timestamps under {root}")

    print(f"# Calibration from {len(runs)} agent runs\n")
    print("## Minutes per agent kind\n")
    for kind in sorted({r["kind"] for r in runs}):
        for model in sorted({r["model"] for r in runs if r["kind"] == kind}):
            v = [r["minutes"] for r in runs if r["kind"] == kind and r["model"] == model]
            print(f"- {kind} / {model}: {q(v)}")

    code = [r for r in runs if r["kind"] == "code" and r["minutes"] >= 1]
    if code and tasks:
        print("\n## Code minutes per risk (runs under 1 minute dropped: skips and no-ops)\n")
        med = {}
        for risk in ("low", "normal", "medium", "high"):
            v = sorted(r["minutes"] for r in code if r["risk"] == risk)
            if v:
                med[risk] = v[len(v) // 2]
                print(f"- {risk}: {q(v)}")
        base = med.get("normal") or med.get("medium")
        if base:
            print("\nSuggested RISK_MULT: " + ", ".join(f"{k}={v / base:.2f}" for k, v in med.items()))
        print("\n## Code minutes per size\n")
        for size in ("XS", "S", "M", "L", "XL"):
            v = [r["minutes"] for r in code if r["size"] == size]
            if v:
                print(f"- {size}: {q(v)}")
        n_tasks = len({r["label"].split()[0] for r in code})
        retries = sum(1 for r in code if r["retry"])
        if n_tasks:
            print(f"\nRetries: {retries} of {n_tasks} tasks ({retries / n_tasks:.0%}). "
                  "Failure tax is usually retries + fix-up agents; start at that share + 5%.")

    iv = sorted((r["start"], r["end"]) for r in runs)
    busy, (cs, ce) = 0.0, iv[0]
    for a, b in iv[1:]:
        if a > ce:
            busy += (ce - cs).total_seconds()
            cs, ce = a, b
        else:
            ce = max(ce, b)
    busy += (ce - cs).total_seconds()
    total = sum(r["minutes"] for r in runs) * 60
    span = (max(b for _, b in iv) - iv[0][0]).total_seconds()
    print("\n## Throughput\n")
    print(f"- agent-hours: {total / 3600:.1f}")
    print(f"- span: {span / 3600:.1f} h, busy: {busy / 3600:.1f} h")
    print(f"- effective_parallelism (agent-hours / busy hours): {total / busy:.2f}  <- put this in machine.effective_parallelism")
    tok = sorted(r["out_tokens"] for r in code if r["out_tokens"])
    if tok:
        print(f"- output tokens per code run: median {tok[len(tok) // 2]:,}, p75 {tok[(3 * len(tok)) // 4]:,}")
    print("\nWeekly usage: note your % of the weekly limit before and after the run;"
          " (after - before) / agent-hours = usage.weekly_pct_per_agent_hour.")

    if "--csv" in opt:
        with open(opt["--csv"], "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["label", "kind", "model", "risk", "size", "minutes", "out_tokens", "retry"])
            w.writeheader()
            for r in runs:
                w.writerow({k: (round(r[k], 1) if k == "minutes" else r[k]) for k in w.fieldnames})
        print(f"\nwrote {opt['--csv']}")


if __name__ == "__main__":
    main()
