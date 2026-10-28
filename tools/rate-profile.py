#!/usr/bin/env python3
"""Identity-log arrival rate from registry-signed checkpoints (stdlib only).

Input: countersignatures.jsonl in this repo. Each identity_events row carries the
registry's own (created_at, tree_size), signed by the registry and countersigned here,
so no timestamp in this analysis is written by the witness clock.

Prints:
  1. every ~24 h pair (second point within 15 min of t+24h) and how many land in 27-31/h
  2. hourly arrival counts per UTC hour, interpolated between checkpoints, for full UTC days
     (days with a checkpoint gap > 2.5 h are dropped), var/mean of those counts
  3. day-profile test: mean pairwise correlation of the 24-hour profiles across days,
     against 2000 within-day shuffles (seed 1028), plus a split-half profile correlation
Usage: python3 tools/rate-profile.py [countersignatures.jsonl] [end_utc_ms] [days]
"""
import json, sys, bisect, random, statistics as st, datetime as dt
path = sys.argv[1] if len(sys.argv) > 1 else "countersignatures.jsonl"
end = int(sys.argv[2]) if len(sys.argv) > 2 else 1793145600000  # 2026-10-28T00:00Z
ndays = int(sys.argv[3]) if len(sys.argv) > 3 else 14
pts = sorted({(r["created_at"], r["tree_size"]) for r in map(json.loads, open(path))
              if r.get("log") == "identity_events" and r.get("status") == "countersigned"})
ts = [p[0] for p in pts]; ns = [p[1] for p in pts]
utc = lambda ms: dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
print("checkpoints", len(pts), utc(ts[0]), "->", utc(ts[-1]),
      "non-monotone", sum(b < a for a, b in zip(ns, ns[1:])))
pairs = []
for t, n in pts:
    i = bisect.bisect_left(ts, t + 86400000)
    for j in (i - 1, i):
        if 0 <= j < len(ts) and abs(ts[j] - t - 86400000) <= 900000:
            pairs.append((t, (ns[j] - n) / ((ts[j] - t) / 3.6e6))); break
for lab, lo in (("all", 0), ("since " + utc(end - ndays * 86400000), end - ndays * 86400000)):
    r = [x for t, x in pairs if t >= lo]
    if r: print(f"24h pairs [{lab}] n={len(r)} min {min(r):.2f} median {st.median(r):.2f} max {max(r):.2f} in 27-31/h: {sum(27 <= x <= 31 for x in r)}")
def at(t):
    i = bisect.bisect_left(ts, t)
    if i == 0 or i >= len(ts) or ts[i] - ts[i - 1] > 9000000: return None
    return ns[i - 1] + (ns[i] - ns[i - 1]) * (t - ts[i - 1]) / (ts[i] - ts[i - 1])
prof = {}
for k in range(ndays, 0, -1):
    d0 = end - k * 86400000; v = [at(d0 + h * 3600000) for h in range(25)]
    if None not in v: prof[utc(d0)[:10]] = [v[h + 1] - v[h] for h in range(24)]
days = sorted(prof); c = [x for d in days for x in prof[d]]
wd = st.median(st.pvariance(prof[d]) / st.mean(prof[d]) for d in days)
print(f"full UTC days {len(days)}; hourly mean {st.mean(c):.2f} var/mean pooled {st.pvariance(c) / st.mean(c):.2f}, within-day median {wd:.2f}")
def corr(x, y):
    mx, my = st.mean(x), st.mean(y)
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y)) ** .5
mpc = lambda P: st.mean(corr(P[a], P[b]) for i, a in enumerate(days) for b in days[i + 1:])
obs = mpc(prof); random.seed(1028)
null = [mpc({d: random.sample(prof[d], 24) for d in days}) for _ in range(2000)]
print(f"day-profile corr {obs:.3f}; shuffle null mean {st.mean(null):.3f}; p(null>=obs) {sum(x >= obs for x in null) / 2000:.4f}")
A = [st.mean(prof[d][h] for d in days[0::2]) for h in range(24)]; B = [st.mean(prof[d][h] for d in days[1::2]) for h in range(24)]
print(f"split-half hour-profile corr {corr(A, B):.3f}")
print("pooled mean arrivals by UTC hour:", " ".join(f"{h:02d}:{st.mean(prof[d][h] for d in days):.1f}" for h in range(24)))
