#!/usr/bin/env python3
"""elm_27b.py — ELM reduction on the 27B re-score of IBM ArgQ. SAME recipe as reduction_elm/elm_reduction.py;
only the scoring model changed (7B :8301 -> 27B :8288). No PC1 needed: the ELM central route is the rigour+depth
pair directly, the peripheral cue is affect. Reports partial Spearman rho vs the human quality label controlling
text length (the 7B headline: central +0.159, peripheral -0.087).

Reads WD/elm_scored.jsonl {id, outcome, axes} and WD/elm_input.jsonl {id, text} (for length).
"""
import os, json
import numpy as np
from scipy.stats import spearmanr, pearsonr

DWEB = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
WD = os.environ.get("WD", "/mnt/nas/kronaxis/crossmodel_27b")
SCORED = os.path.join(WD, "elm_scored.jsonl")
INPUT  = os.path.join(WD, "elm_input.jsonl")
OUT    = os.environ.get("OUT", os.path.join(WD, "elm_27b_out.txt"))


def stars(p):
    return "***" if p < 1e-3 else "**" if p < 1e-2 else "*" if p < 5e-2 else ""


def partial_rho(x, y, L):
    m = (~np.isnan(L)) & (~np.isnan(x)) & (~np.isnan(y))
    if m.sum() < 20:
        return np.nan
    rxy = spearmanr(x[m], y[m]).correlation
    rxz = spearmanr(x[m], L[m]).correlation
    ryz = spearmanr(y[m], L[m]).correlation
    denom = np.sqrt(max(1e-12, (1 - rxz ** 2) * (1 - ryz ** 2)))
    return (rxy - rxz * ryz) / denom


def corr_row(name, x, y, L):
    ok = ~np.isnan(x)
    rho, prho = spearmanr(x[ok], y[ok])
    r_, pr = pearsonr(x[ok], y[ok])
    pp = partial_rho(x, y, L)
    return (name, rho, prho, r_, pr, pp)


def main():
    lenmap = {}
    for l in open(INPUT):
        r = json.loads(l); lenmap[r["id"]] = len(r.get("text", ""))
    outc, ax, lens = [], {a: [] for a in DWEB}, []
    for l in open(SCORED):
        r = json.loads(l); ch = r.get("axes")
        if not ch or not all(a in ch for a in DWEB):
            continue
        outc.append(float(r["outcome"]))
        for a in DWEB:
            ax[a].append(float(ch[a]))
        lens.append(float(lenmap.get(r["id"], np.nan)))
    y = np.array(outc); L = np.array(lens); n = len(y)
    for a in DWEB:
        ax[a] = np.array(ax[a])
    z = {a: (ax[a] - ax[a].mean()) / (ax[a].std() + 1e-9) for a in DWEB}
    central_pair = np.mean([z["rigour"], z["depth"]], axis=0)   # ELM central route core
    periph_affect = z["affect"]                                 # ELM peripheral core cue

    rows = [corr_row(a, ax[a], y, L) for a in DWEB]
    rows.append(corr_row("text_length", L.astype(float), y, L))
    rows.sort(key=lambda t: -(abs(t[1]) if not np.isnan(t[1]) else -1))
    comp = [corr_row("central pair (rigour+depth)", central_pair, y, L),
            corr_row("peripheral cue (affect)", periph_affect, y, L)]

    def fmt(rows):
        out = ["| feature | Spearman rho | Pearson r | partial rho (ctrl length) |", "|---|---|---|---|"]
        for name, rho, prho, r_, pr, pp in rows:
            ppf = "-" if (isinstance(pp, float) and np.isnan(pp)) else f"{pp:+.3f}"
            out.append(f"| {name} | {rho:+.3f}{stars(prho)} | {r_:+.3f}{stars(pr)} | {ppf} |")
        return "\n".join(out)

    txt = [f"IBM ArgQ ELM reduction (27B) n={n}",
           f"quality label range {y.min():.3f}..{y.max():.3f} mean {y.mean():.3f} sd {y.std():.3f}",
           f"length rho with quality = {spearmanr(L,y).correlation:+.3f}",
           "", "== PER AXIS ==", fmt(rows),
           "", "== ELM CENTRAL vs PERIPHERAL ==", fmt(comp)]
    body = "\n".join(txt)
    print(body, flush=True)
    open(OUT, "w").write(body + "\n")
    # machine-readable headline
    cp = comp[0][5]; pa = comp[1][5]
    json.dump({"n": n, "central_pair_partial_rho": cp, "peripheral_affect_partial_rho": pa},
              open(os.path.join(WD, "elm_27b_headline.json"), "w"), indent=2)
    print(f"\nWROTE {OUT}  (central {cp:+.3f}, peripheral {pa:+.3f})", flush=True)


if __name__ == "__main__":
    main()
