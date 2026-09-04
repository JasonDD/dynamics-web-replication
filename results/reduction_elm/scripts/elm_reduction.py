#!/usr/bin/env python3
"""elm_reduction.py — ELM reduction test on IBM ArgQ.

Does our MATTER reading track ARGUMENT QUALITY (the Elaboration Likelihood Model's
central route) while MANNER does not?

ANALYSIS ONLY: reuses the held 8-axis character scores from the instrument
external-validity run (/mnt/external/benchmarks/scored/ibm_argq.jsonl). No scoring.

Anchors the matter/manner split on the SAME PC1 the rest of the series uses
(SVD on the internal reference table). Reports:
  1. per-axis Spearman/Pearson/partial-for-length vs the human quality label
  2. matter-composite vs manner-composite (PC1 sign groups)
  3. the theory-clean central pair (rigour+depth) vs peripheral pair (affect)
  4. PC1 itself (the single matter-minus-manner ruler)
"""
import os, json
import numpy as np
import psycopg2
from scipy.stats import spearmanr, pearsonr

DWEB = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
SCORED = "/mnt/external/benchmarks/scored/ibm_argq.jsonl"
INPUT = "/mnt/external/benchmarks/ibm_argq.jsonl"
OUT = os.environ.get("OUT", "/tmp/elm_out")
os.makedirs(OUT, exist_ok=True)


def db_pw():
    for line in open(os.path.expanduser("~/.kronaxis/env")):
        if line.startswith("TFS_DB_PASSWORD="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("TFS_DB_PASSWORD not found")


def build_pc1():
    conn = psycopg2.connect(host="127.0.0.1", port=5432, user="titan", dbname="tfs", password=db_pw())
    c = conn.cursor()
    c.execute(f"SELECT {','.join(DWEB)} FROM the internal reference table")
    allc = np.array(c.fetchall(), float)
    conn.close()
    MEAN = allc.mean(0); STD = allc.std(0) + 1e-9
    _, _, Vt = np.linalg.svd((allc - MEAN) / STD, full_matrices=False); PC1 = Vt[0]
    if (PC1[DWEB.index("rigour")] + PC1[DWEB.index("depth")]) < 0:
        PC1 = -PC1
    print(f"PC1 built on the internal reference table n={len(allc)}", flush=True)
    load = {a: float(PC1[i]) for i, a in enumerate(DWEB)}
    print("  PC1 loadings: " + ", ".join(f"{a}={v:+.2f}" for a, v in load.items()), flush=True)
    return MEAN, STD, PC1, load


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
    MEAN, STD, PC1, load = build_pc1()
    lenmap = {}
    for l in open(INPUT):
        r = json.loads(l); lenmap[r["id"]] = len(r.get("text", ""))
    outc, ax = [], {a: [] for a in DWEB}
    pc1v, lens = [], []
    for l in open(SCORED):
        r = json.loads(l); ch = r.get("char")
        if not ch or not all(a in ch for a in DWEB):
            continue
        outc.append(float(r["outcome"]))
        vec = np.array([ch[a] for a in DWEB], float)
        for i, a in enumerate(DWEB):
            ax[a].append(vec[i])
        pc1v.append(float(((vec - MEAN) / STD) @ PC1))
        lens.append(float(lenmap.get(r["id"], np.nan)))
    y = np.array(outc); L = np.array(lens); n = len(y)
    for a in DWEB:
        ax[a] = np.array(ax[a])
    pc1v = np.array(pc1v)

    # z-score axes for composites
    z = {a: (ax[a] - ax[a].mean()) / (ax[a].std() + 1e-9) for a in DWEB}
    matter_axes = [a for a in DWEB if load[a] > 0]   # PC1 positive loaders
    manner_axes = [a for a in DWEB if load[a] < 0]   # PC1 negative loaders
    matter_comp = np.mean([z[a] for a in matter_axes], axis=0)
    manner_comp = np.mean([z[a] for a in manner_axes], axis=0)  # high = more manner
    central_pair = np.mean([z["rigour"], z["depth"]], axis=0)   # ELM central route core
    periph_affect = z["affect"]                                 # ELM peripheral core cue

    # per-axis rows sorted by |rho|
    rows = [corr_row(a, ax[a], y, L) for a in DWEB]
    rows.append(corr_row("matter_manner_PC1", pc1v, y, L))
    rows.append(corr_row("text_length", L.astype(float), y, L))
    rows.sort(key=lambda t: -(abs(t[1]) if not np.isnan(t[1]) else -1))

    comp = [
        corr_row(f"MATTER composite ({'+'.join(matter_axes)})", matter_comp, y, L),
        corr_row(f"MANNER composite ({'+'.join(manner_axes)})", manner_comp, y, L),
        corr_row("central pair (rigour+depth)", central_pair, y, L),
        corr_row("peripheral cue (affect)", periph_affect, y, L),
    ]

    def fmt(rows):
        out = ["| feature | Spearman rho | Pearson r | partial rho (ctrl length) |",
               "|---|---|---|---|"]
        for name, rho, prho, r_, pr, pp in rows:
            ppf = "-" if (isinstance(pp, float) and np.isnan(pp)) else f"{pp:+.3f}"
            out.append(f"| {name} | {rho:+.3f}{stars(prho)} | {r_:+.3f}{stars(pr)} | {ppf} |")
        return "\n".join(out)

    txt = [f"IBM ArgQ ELM reduction  n={n}",
           f"quality label range {y.min():.3f}..{y.max():.3f}  mean {y.mean():.3f}  sd {y.std():.3f}",
           f"length rho with quality = {spearmanr(L,y).correlation:+.3f}",
           "",
           "matter axes (PC1 positive): " + ", ".join(matter_axes),
           "manner axes (PC1 negative): " + ", ".join(manner_axes),
           "",
           "== PER AXIS ==", fmt(rows),
           "",
           "== COMPOSITES / ELM CENTRAL vs PERIPHERAL ==", fmt(comp)]
    body = "\n".join(txt)
    print(body, flush=True)
    open(os.path.join(OUT, "elm_reduction.txt"), "w").write(body + "\n")
    print("\nWROTE", os.path.join(OUT, "elm_reduction.txt"), flush=True)


if __name__ == "__main__":
    main()
