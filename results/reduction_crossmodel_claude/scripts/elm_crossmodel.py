#!/usr/bin/env python3
"""elm_crossmodel.py — independent second-lineage re-score of the ELM reduction on IBM ArgQ.

Same rubric, same 8 axes, same partial-Spearman analysis as
../reduction_elm/scripts/elm_reduction.py, but the character scores are produced by
an independent frontier model family (a different scorer lineage from the 7B teacher),
by reading each text. Tests whether the ELM central-route result (rigour+depth track
argument quality; the peripheral affect cue does not) survives a change of scorer lineage.

Inputs (on DL580):
  SCORES  = second-lineage scores jsonl {id, c:[8 in DWEB order]}
  SAMPLE  = {id, text, outcome} for the scored sample
  QWEN    = held 7B scores /mnt/external/benchmarks/scored/ibm_argq.jsonl (for agreement)
"""
import os, json
import numpy as np
import psycopg2
from scipy.stats import spearmanr, pearsonr

DWEB = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]
SCORES = os.environ["SCORES"]
SAMPLE = os.environ["SAMPLE"]
QWEN = os.environ.get("QWEN", "/mnt/external/benchmarks/scored/ibm_argq.jsonl")
OUT = os.environ.get("OUT", os.path.dirname(SCORES))


def db_pw():
    for line in open(os.path.expanduser("~/.kronaxis/env")):
        if line.startswith("TFS_DB_PASSWORD="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("TFS_DB_PASSWORD not found")


def build_pc1():
    conn = psycopg2.connect(host="127.0.0.1", port=5432, user="titan", dbname="tfs", password=db_pw())
    c = conn.cursor()
    c.execute(f"SELECT {','.join(DWEB)} FROM cc_v3.domain_char8_expanded")
    allc = np.array(c.fetchall(), float)
    conn.close()
    MEAN = allc.mean(0); STD = allc.std(0) + 1e-9
    _, _, Vt = np.linalg.svd((allc - MEAN) / STD, full_matrices=False); PC1 = Vt[0]
    if (PC1[DWEB.index("rigour")] + PC1[DWEB.index("depth")]) < 0:
        PC1 = -PC1
    load = {a: float(PC1[i]) for i, a in enumerate(DWEB)}
    return MEAN, STD, PC1, load, len(allc)


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


def fmt(rows):
    out = ["| feature | Spearman rho | Pearson r | partial rho (ctrl length) |",
           "|---|---|---|---|"]
    for name, rho, prho, r_, pr, pp in rows:
        ppf = "-" if (isinstance(pp, float) and np.isnan(pp)) else f"{pp:+.3f}"
        out.append(f"| {name} | {rho:+.3f}{stars(prho)} | {r_:+.3f}{stars(pr)} | {ppf} |")
    return "\n".join(out)


def main():
    MEAN, STD, PC1, load, nref = build_pc1()

    sample = {}
    for l in open(SAMPLE):
        r = json.loads(l)
        sample[r["id"]] = (r["text"], float(r["outcome"]))

    ids, outc, lens = [], [], []
    ax = {a: [] for a in DWEB}
    pc1v = []
    my_ch = {}
    for l in open(SCORES):
        r = json.loads(l)
        _id = r["id"]
        if _id not in sample:
            continue
        vec = np.array(r["c"], float)
        my_ch[_id] = {a: float(vec[i]) for i, a in enumerate(DWEB)}
        text, o = sample[_id]
        ids.append(_id); outc.append(o); lens.append(float(len(text)))
        for i, a in enumerate(DWEB):
            ax[a].append(vec[i])
        pc1v.append(float(((vec - MEAN) / STD) @ PC1))

    y = np.array(outc); L = np.array(lens); n = len(y)
    for a in DWEB:
        ax[a] = np.array(ax[a])
    pc1v = np.array(pc1v)
    z = {a: (ax[a] - ax[a].mean()) / (ax[a].std() + 1e-9) for a in DWEB}
    matter_axes = [a for a in DWEB if load[a] > 0]
    manner_axes = [a for a in DWEB if load[a] < 0]
    matter_comp = np.mean([z[a] for a in matter_axes], axis=0)
    manner_comp = np.mean([z[a] for a in manner_axes], axis=0)
    central_pair = np.mean([z["rigour"], z["depth"]], axis=0)
    periph_affect = z["affect"]

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

    # --- inter-lineage agreement on raw axes (shared ids with 7B) ---
    qwen_ch = {}
    for l in open(QWEN):
        r = json.loads(l)
        ch = r.get("char")
        if ch and all(a in ch for a in DWEB):
            qwen_ch[r["id"]] = ch
    shared = [i for i in ids if i in qwen_ch]
    agree_lines = []
    if shared:
        for a in DWEB:
            cv = np.array([my_ch[i][a] for i in shared])
            qv = np.array([float(qwen_ch[i][a]) for i in shared])
            pear = pearsonr(cv, qv)[0]
            spear = spearmanr(cv, qv).correlation
            mad = float(np.mean(np.abs(cv - qv)))
            agree_lines.append(f"| {a} | {pear:+.3f} | {spear:+.3f} | {mad:.3f} | {cv.mean():.2f} / {qv.mean():.2f} |")

    txt = [f"IBM ArgQ ELM reduction — second-lineage re-score  n={n}",
           f"quality label range {y.min():.3f}..{y.max():.3f}  mean {y.mean():.3f}  sd {y.std():.3f}",
           f"length rho with quality = {spearmanr(L, y).correlation:+.3f}",
           f"PC1 built on cc_v3.domain_char8_expanded n={nref}",
           "matter axes (PC1 positive): " + ", ".join(matter_axes),
           "manner axes (PC1 negative): " + ", ".join(manner_axes),
           "",
           "== PER AXIS (second-lineage scores vs human quality) ==", fmt(rows),
           "",
           "== COMPOSITES / ELM CENTRAL vs PERIPHERAL ==", fmt(comp),
           "",
           f"== INTER-LINEAGE AGREEMENT (second lineage vs 7B, shared ids n={len(shared)}) ==",
           "| axis | Pearson | Spearman | mean abs diff | mean 2nd / mean 7B |",
           "|---|---|---|---|---|",
           *agree_lines]
    body = "\n".join(txt)
    print(body, flush=True)
    open(os.path.join(OUT, "elm_crossmodel.txt"), "w").write(body + "\n")

    summary = {
        "scorer": "independent frontier model family (second lineage)",
        "n": n, "n_reference_domains": nref,
        "central_pair_partial_rho": corr_row("central", central_pair, y, L)[5],
        "affect_partial_rho": corr_row("affect", periph_affect, y, L)[5],
        "matter_comp_partial_rho": corr_row("m", matter_comp, y, L)[5],
        "manner_comp_partial_rho": corr_row("m", manner_comp, y, L)[5],
        "pc1_partial_rho": corr_row("pc1", pc1v, y, L)[5],
        "qwen7b_central_pair_partial_rho": 0.159,
        "qwen7b_affect_partial_rho": -0.087,
        "interlineage_shared_n": len(shared),
    }
    json.dump(summary, open(os.path.join(OUT, "elm_crossmodel_summary.json"), "w"), indent=2)
    print("\nWROTE elm_crossmodel.txt + summary.json", flush=True)


if __name__ == "__main__":
    main()
