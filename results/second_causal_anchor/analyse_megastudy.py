#!/usr/bin/env python3
"""analyse_megastudy.py - Paper 4B second causal anchor.

Milkman et al. 2021 PNAS flu vaccination megastudy: 19 text nudge arms assigned at random,
per arm causal uplift vs usual care (Efficacy.csv, Beta ALL = Figure 1 / Table S1). Objective
message features per arm (ObjectiveAttributes.csv). We test whether message CHARACTER predicts
the per arm CAUSAL uplift, in the funnel direction that held on Upworthy clicks (manner earns
attention, matter earns the action).

Data provenance (all FREE, OSF osf.io/tucjs, deposited by the authors):
  Efficacy.csv           osf.io/download/a2pbh   per arm N, % vaccinated, Beta (causal uplift)
  ObjectiveAttributes.csv osf.io/download/ekxsd   per arm objective message features
Both joined on Intervention ID (== Team). n = 19 arms.

No verbatim SMS text is in the free deposit (it is in message mockup images and the paywalled
SSRN working paper 10.2139/ssrn.3780267), so the 8 axis model instrument is NOT scored here;
this run uses the authors' objective coding and triangulates against their published human
rater PCA. See RESULT.md.
"""
import csv, json
from statistics import mean

def load(path):
    return list(csv.DictReader(open(path, encoding="utf-8-sig")))

def rank(v):
    idx = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0]*len(v); i = 0
    while i < len(v):
        j = i
        while j+1 < len(v) and v[idx[j+1]] == v[idx[i]]: j += 1
        avg = (i+j)/2 + 1
        for k in range(i, j+1): r[idx[k]] = avg
        i = j+1
    return r

def pearson(x, y):
    mx, my = mean(x), mean(y)
    num = sum((a-mx)*(b-my) for a, b in zip(x, y))
    den = (sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y))**0.5
    return num/den if den else float("nan")

def spearman(x, y):
    return pearson(rank(x), rank(y))

def main():
    eff = {r["Intervention ID"].strip(): r for r in load("Efficacy.csv")}
    obj = {r["Team"].strip(): r for r in load("ObjectiveAttributes.csv")}
    rows = [(tid, eff[tid], obj[tid]) for tid in eff if tid in obj]
    beta = [float(e["Beta (ALL)"]) for _, e, _ in rows]
    print(f"joined arms: {len(rows)}   Beta min {min(beta):.3f} max {max(beta):.3f} mean {mean(beta):.3f}")

    feats = ["Words_First", "FR_ReadingEase_First", "Imperative_FullConvo", "Interrogative_FullConvo",
             "ExclamationMarks", "Multimedia", "AnyInteractive", "ReservedforYou", "Total_Messages"]
    role = {"ExclamationMarks": "MANNER", "Multimedia": "MANNER", "AnyInteractive": "MANNER",
            "FR_ReadingEase_First": "MANNER casual", "Interrogative_FullConvo": "MANNER chatty",
            "ReservedforYou": "MATTER reserved"}
    print(f"\n{'feature':22s} {'spearman':>9s} {'pearson':>9s}   role")
    for f in feats:
        x = [float(o[f]) for _, _, o in rows]
        print(f"{f:22s} {spearman(x, beta):+9.3f} {pearson(x, beta):+9.3f}   {role.get(f,'')}")

    def z(v):
        m = mean(v); s = (sum((a-m)**2 for a in v)/len(v))**0.5 or 1.0
        return [(a-m)/s for a in v]
    manner = ["ExclamationMarks", "Multimedia", "AnyInteractive", "FR_ReadingEase_First", "Interrogative_FullConvo"]
    Z = [z([float(o[f]) for _, _, o in rows]) for f in manner]
    midx = [sum(Z[k][i] for k in range(len(manner))) for i in range(len(rows))]
    print(f"\nMANNER composite vs Beta: spearman {spearman(midx, beta):+.3f} pearson {pearson(midx, beta):+.3f}")

if __name__ == "__main__":
    main()
