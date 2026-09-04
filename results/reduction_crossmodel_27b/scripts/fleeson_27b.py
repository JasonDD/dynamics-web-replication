#!/usr/bin/env python3
"""fleeson_27b.py — Fleeson reduction on the 27B re-score of cross-site DISPOSITION. SAME one-way random-effects
variance decomposition (var_components) as truthometer/scripts/cc_crosssite_fleeson.py; only the disposition
scoring model changed (7B -> 27B). Room-level estimator (occasion = a distinct site). 7B headline to beat:
room-level trait share (ICC1, mean over 8 D8 axes) = 0.516 (situation 0.484).

Reads WD/fleeson_scored.jsonl {id, ident, domain, axes(D8)}.
"""
import os, json, numpy as np
from collections import defaultdict

D8 = ["discipline","yielding","novelty","acuity","mercuriality","impulsivity","candour","sociability"]
WD = os.environ.get("WD", "the internal storecrossmodel_27b")
SCORED = os.path.join(WD, "fleeson_scored.jsonl")


def var_components(values, labels, ngroups):
    """One-way random-effects variance components (verbatim from cc_crosssite_fleeson.py)."""
    N = values.size; g = ngroups
    if g < 2 or N - g < 1:
        return float("nan"), float("nan"), float("nan")
    n_i = np.bincount(labels, minlength=g).astype(float)
    sum_i = np.bincount(labels, weights=values, minlength=g)
    mean_i = sum_i / np.where(n_i > 0, n_i, 1)
    grand = values.mean()
    ssb = float(np.sum(n_i * (mean_i - grand) ** 2))
    sst = float(np.sum((values - grand) ** 2))
    ssw = sst - ssb
    msb = ssb / (g - 1); msw = ssw / (N - g)
    kbar = (N - float(np.sum(n_i ** 2)) / N) / (g - 1)
    s2_within = msw
    s2_between = (msb - msw) / kbar if kbar > 0 else float("nan")
    tot = s2_between + s2_within
    trait_share = s2_between / tot if tot > 0 else float("nan")
    return s2_between, s2_within, trait_share


def main():
    # by[ident][domain] -> list of D8 dicts
    by = defaultdict(lambda: defaultdict(list))
    for l in open(SCORED):
        try:
            r = json.loads(l)
        except Exception:
            continue
        ch = r.get("axes")
        if not ch or not all(a in ch for a in D8):
            continue
        by[r["ident"]][r["domain"]].append({a: float(ch[a]) for a in D8})

    # room-level: average a person's blocks to one mean per site, keep persons with >=2 sites
    vals = {ax: [] for ax in D8}; labs = []
    npers = 0; nocc = 0
    for ident, doms in by.items():
        occasions = [{ax: float(np.mean([o[ax] for o in lst])) for ax in D8} for lst in doms.values()]
        if len(occasions) < 2:
            continue
        pid = npers; npers += 1; nocc += len(occasions)
        for o in occasions:
            labs.append(pid)
            for ax in D8:
                vals[ax].append(o[ax])
    labels = np.asarray(labs, dtype=np.int64)
    res = {}
    for ax in D8:
        s2b, s2w, tr = var_components(np.asarray(vals[ax], float), labels, npers)
        res[ax] = dict(s2_between=s2b, s2_within=s2w, trait_share=tr, situation_share=1 - tr)
    tr_mean = float(np.nanmean([res[ax]["trait_share"] for ax in D8]))

    print(f"=== FLEESON disposition (27B, room-level) — {npers:,} persons, {nocc:,} occasions ===")
    print(f"  {'axis':16s} {'s2_between':>12s} {'s2_within':>12s} {'trait%':>8s} {'situ%':>8s}")
    for ax, v in res.items():
        print(f"  {ax:16s} {v['s2_between']:12.4f} {v['s2_within']:12.4f} "
              f"{100*v['trait_share']:7.1f}% {100*v['situation_share']:7.1f}%")
    print(f"  ---> MEAN trait share (ICC1) {100*tr_mean:.1f}%  |  situation {100*(1-tr_mean):.1f}%   (7B: 51.6/48.4)")

    out = {"n_persons": npers, "n_occasions": nocc,
           "trait_share_icc1": tr_mean, "situation_share": 1 - tr_mean,
           "per_axis": res}
    json.dump(out, open(os.path.join(WD, "fleeson_27b_summary.json"), "w"), indent=2)
    print(f"wrote {os.path.join(WD, 'fleeson_27b_summary.json')}", flush=True)


if __name__ == "__main__":
    main()
