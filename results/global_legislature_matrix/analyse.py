#!/usr/bin/env python3
"""Global legislature character matrix: legislature x 8-axis, clustering, universal-voice check.

Combines newly-scored world legislatures (sample_scored.jsonl) with the held references
ParlaMint (26 EU parliaments, EN-translated) and UNGD (diplomatic, EN). Emits a plain-text
report to stdout; the wrapper tees it into RESULT.md.
"""
import os, json, math
from collections import defaultdict, Counter
import numpy as np

BASE = "the internal corpus store"
NEW = f"{BASE}/results/global_legislature_matrix/sample_scored.jsonl"
PARLA = f"{BASE}/parlamint/sample_scored.jsonl"
UNGD = f"{BASE}/ungd/ungd_char8.jsonl"
AX = ["rigour", "depth", "originality", "candour", "affect", "commercial_drive", "stance", "register"]

# ---- metadata: heritage (legal/institutional lineage), region, democracy age, language of the SCORED text ----
# lang: en_native | en_translated | native_nonEN  (translation control)
META = {
    # newly scored legislatures
    "US_Congress":            ("N_America",      "CommonLaw_Presidential", "old",   "en_native",     "legislature"),
    "SCOTUS":                 ("N_America",      "CommonLaw_Court",        "old",   "en_native",     "court"),
    "Brazil_Chamber":         ("S_America",      "Napoleonic_Civil",       "young", "native_nonEN",  "legislature"),
    "Ghana_Parliament":       ("W_Africa",       "Westminster",            "young", "en_native",     "legislature"),
    "Kenya_Parliament":       ("E_Africa",       "Westminster",            "young", "en_native",     "legislature"),
    "Nigeria_NASS":           ("W_Africa",       "Westminster",            "young", "en_native",     "legislature"),
    "SouthAfrica_NA":         ("Southern_Africa","Westminster",            "young", "en_native",     "legislature"),
    "Zambia_NA":              ("Southern_Africa","Westminster",            "young", "en_native",     "legislature"),
    "Zimbabwe_Parliament":    ("Southern_Africa","Westminster",            "young", "en_native",     "legislature"),
    "Malaysia_DewanRakyat":   ("SE_Asia",        "Westminster",            "mid",   "en_native",     "legislature"),
    "Korea_NationalAssembly": ("E_Asia",         "Civil_Presidential",     "young", "native_nonEN",  "legislature"),
    "Japan_Diet":             ("E_Asia",         "Civil_Parliamentary",    "mid",   "native_nonEN",  "legislature"),
    "Pan_African_Parliament": ("Africa_Supra",   "Supranational",          "supra", "en_native",     "supra"),
}
# ParlaMint ISO2 -> heritage (EU legal lineages), all EN_translated, region Europe
PARLA_HERITAGE = {
    "GB": "Westminster", "IE": "Westminster", "MT": "Westminster", "CY": "Westminster",
    "DK": "Nordic", "SE": "Nordic", "NO": "Nordic", "FI": "Nordic", "IS": "Nordic",
    "FR": "Napoleonic_Civil", "BE": "Napoleonic_Civil", "IT": "Napoleonic_Civil",
    "ES": "Napoleonic_Civil", "PT": "Napoleonic_Civil", "GR": "Napoleonic_Civil", "NL": "Napoleonic_Civil",
    "DE": "Germanic_Civil", "AT": "Germanic_Civil",
    "PL": "PostCommunist", "CZ": "PostCommunist", "HU": "PostCommunist", "SI": "PostCommunist",
    "HR": "PostCommunist", "BG": "PostCommunist", "RS": "PostCommunist", "BA": "PostCommunist",
    "EE": "PostCommunist", "LV": "PostCommunist", "UA": "PostCommunist", "TR": "Other",
}
PARLA_AGE = {c: ("young" if h == "PostCommunist" else "old") for c, h in PARLA_HERITAGE.items()}


def load_new():
    rows = []
    for l in open(NEW, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        r = json.loads(l)
        v = [float(r["char"][a]) for a in AX]
        rows.append((r["legislature"], r["legislature"], r["n_chars"], v, r.get("lang", "")))
    return rows  # (group_key, legislature, n_chars, vec8, lang)


def load_parla():
    rows = []
    for l in open(PARLA, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        r = json.loads(l)
        c = r["country"]
        v = [float(r["char"][a]) for a in AX]
        nchars = int(r.get("n_words", 0)) * 6
        rows.append((f"EU:{c}", f"ParlaMint_{c}", nchars, v, "en_translated"))
    return rows


def load_ungd(cap=2000):
    rows = []
    for l in open(UNGD, encoding="utf-8"):
        l = l.strip()
        if not l:
            continue
        r = json.loads(l)
        v = [float(r["char"][a]) for a in AX]
        rows.append(("UNGD", f"UNGD_{r.get('iso3','')}", 0, v, "en_translated"))
    # subsample so the 10k UNGD rows don't dominate the pooled PCA / z-scoring
    import random as _rnd
    _rnd.seed(7)
    if len(rows) > cap:
        rows = _rnd.sample(rows, cap)
    return rows


def zmat(M):
    mu = M.mean(0); sd = M.std(0); sd[sd == 0] = 1
    return (M - mu) / sd, mu, sd


def pca1(Z):
    U, S, Vt = np.linalg.svd(Z - Z.mean(0), full_matrices=False)
    pc1 = Vt[0]
    # orient so + = matter (rigour+depth+candour up, affect+register down)
    matter = np.array([1, 1, 0.5, 1, -1, -0.5, 0.5, -1])
    if np.dot(pc1, matter) < 0:
        pc1 = -pc1
    return pc1


def anova(groups):
    """one-way ANOVA over group -> list of scalars. returns F, p_approx(eta), eta2."""
    allv = np.concatenate([np.array(g) for g in groups if len(g)])
    gm = allv.mean()
    ssb = sum(len(g) * (np.mean(g) - gm) ** 2 for g in groups if len(g))
    ssw = sum(((np.array(g) - np.mean(g)) ** 2).sum() for g in groups if len(g))
    k = sum(1 for g in groups if len(g)); N = len(allv)
    dfb = k - 1; dfw = N - k
    if dfw <= 0 or ssw == 0:
        return float("nan"), float("nan")
    F = (ssb / dfb) / (ssw / dfw)
    eta2 = ssb / (ssb + ssw)
    return F, eta2


def main():
    new = load_new(); parla = load_parla(); ungd = load_ungd()
    allrows = new + parla + ungd
    M = np.array([r[3] for r in allrows])
    Z, mu, sd = zmat(M)
    pc1 = pca1(Z)
    pc1_load = dict(zip(AX, pc1))
    proj = Z @ pc1

    # per-legislature aggregation (new + EU + UNGD-as-one-cloud)
    by = defaultdict(list)          # group_key -> list of vec8
    by_pc1 = defaultdict(list)      # group_key -> list of pc1 proj
    lang_of = {}; nchars_of = defaultdict(list)
    for i, r in enumerate(allrows):
        gk, leg, nch, v, lang = r
        by[gk].append(v); by_pc1[gk].append(proj[i]); lang_of[gk] = lang
        if nch:
            nchars_of[gk].append(nch)

    print("# Global Legislature Character Matrix — RESULT")
    print()
    print("Instrument: 8-axis DYNAMICS-WEB character, scored on the on-box 7B (an internal 7B instruct model, , temp 0),")
    print("identical prompt/contract to the held ParlaMint + UNGD scoring. PC1 (+ = MATTER, - = MANNER).")
    print(f"PC1 loadings: " + "  ".join(f"{a}{pc1_load[a]:+.2f}" for a in AX))
    print()
    print(f"Speeches scored: new legislatures n={len(new)} ({len(set(r[1] for r in new))} legislatures); "
          f"references ParlaMint n={len(parla)} (26 EU), UNGD n={len(ungd)}.")
    print("EXCLUDED (held corpus is metadata/index only, no speech text): Argentina_Congress, India_LokSabha.")
    print()

    # ---- MATRIX: legislature x axis (new legislatures + EU countries) ----
    print("## 1. Legislature x axis matrix (mean per axis; PC1 = matter/manner)")
    print()
    hdr = "legislature".ljust(26) + " n  " + " ".join(a[:4].rjust(5) for a in AX) + "   PC1   heritage/region"
    print(hdr)
    print("-" * len(hdr))
    def rowline(gk, label, meta):
        vs = np.array(by[gk]); m = vs.mean(0)
        p = np.mean(by_pc1[gk])
        cells = " ".join(f"{m[j]:5.2f}" for j in range(8))
        print(f"{label[:26].ljust(26)} {len(vs):>2} {cells}  {p:+5.2f}  {meta}")
        return m, p
    order = sorted([g for g in by if g in META], key=lambda g: np.mean(by_pc1[g]))
    for gk in order:
        reg, her, age, lang, branch = META[gk]
        rowline(gk, gk, f"{her}/{reg}/{age}/{lang.split('_')[0]}" + ("" if branch == "legislature" else f"/{branch.upper()}"))
    print()
    print("EU ParlaMint reference rows (>=15 speeches), by PC1:")
    eu = sorted([g for g in by if g.startswith("EU:") and len(by[g]) >= 15], key=lambda g: np.mean(by_pc1[g]))
    for gk in eu:
        c = gk[3:]; her = PARLA_HERITAGE.get(c, "?")
        rowline(gk, f"ParlaMint_{c}", f"{her}/Europe/{PARLA_AGE.get(c,'?')}/en_tr")
    ug = np.array(by["UNGD"]).mean(0); print()
    print(f"UNGD diplomatic reference (n={len(by['UNGD'])}): " +
          " ".join(f"{ug[j]:.2f}" for j in range(8)) + f"  PC1 {np.mean(by_pc1['UNGD']):+.2f}")
    print()

    # ---- 2. UNIVERSAL PARLIAMENTARY VOICE ----
    print("## 2. Universal-parliamentary-voice check")
    print()
    legkeys = [g for g in by if (g in META and META[g][4] == "legislature") or g.startswith("EU:")]
    legmeans = np.array([np.array(by[g]).mean(0) for g in legkeys])
    centroid = legmeans.mean(0)
    print("Shared centre (mean over all national legislatures), per axis:")
    print("  " + "  ".join(f"{a}={centroid[j]:.2f}" for j, a in enumerate(AX)))
    # variance decomposition per axis: between-legislature vs within (residual)
    print()
    print("Per-axis between-legislature vs within-legislature variance (ICC-like: high ICC = nationally")
    print("distinctive; low ICC = institutional invariant shared across all parliaments):")
    for j, a in enumerate(AX):
        groups = [np.array(by[g])[:, j] for g in legkeys]
        F, eta2 = anova(groups)
        tag = "INVARIANT" if eta2 < 0.10 else ("distinctive" if eta2 > 0.20 else "mixed")
        print(f"  {a:16s} between/total eta2={eta2:.3f}  centre={centroid[j]:.2f}  -> {tag}")
    # cosine of each legislature mean to centroid
    cs = [float(np.dot(m, centroid) / (np.linalg.norm(m) * np.linalg.norm(centroid))) for m in legmeans]
    print()
    print(f"Cosine(legislature mean, shared centre): min={min(cs):.3f} mean={np.mean(cs):.3f} max={max(cs):.3f}")
    print("  (all high -> one shared parliamentary voice with small national deviations)")
    print()

    # ---- 3. CLUSTERING TESTS ----
    print("## 3. What does character cluster by? (PC1 one-way ANOVA + eta^2 over legislatures)")
    print()
    # build per-legislature grouping labels (legislatures only, exclude court/supra)
    def group_labels(kind):
        lab = {}
        for g in legkeys:
            if g in META:
                reg, her, age, lang, branch = META[g]
            else:
                c = g[3:]; reg, her, age = "Europe", PARLA_HERITAGE.get(c, "Other"), PARLA_AGE.get(c, "old"); lang = "en_translated"
            lab[g] = {"region": reg, "heritage": her, "age": age, "language": lang}[kind]
        return lab

    for kind in ["heritage", "region", "age", "language"]:
        lab = group_labels(kind)
        buckets = defaultdict(list)
        for g in legkeys:
            buckets[lab[g]].extend(list(by_pc1[g]))  # speech-level PC1
        groups = list(buckets.values())
        F, eta2 = anova(groups)
        print(f"[{kind}] one-way ANOVA of PC1 across {len(buckets)} groups: F={F:.2f} eta2={eta2:.3f}")
        means = sorted(((k, np.mean(v), len(v)) for k, v in buckets.items()), key=lambda x: x[1])
        for k, m, n in means:
            print(f"    {k:22s} n={n:>4} PC1 {m:+.2f}")
        print()

    # ---- Westminster affinity (like UNGD anglosphere test) ----
    print("## 4. Heritage affinity test (within-heritage vs to-rest mean distance, standardised 8D)")
    print()
    ZL = (legmeans - legmeans.mean(0)) / (legmeans.std(0) + 1e-9)
    her_lab = group_labels("heritage")
    idx = {g: i for i, g in enumerate(legkeys)}
    for her in ["Westminster", "Napoleonic_Civil", "Nordic", "PostCommunist"]:
        members = [g for g in legkeys if her_lab[g] == her]
        if len(members) < 2:
            continue
        mi = [idx[g] for g in members]
        within = []; torest = []
        for a in range(len(mi)):
            for b in range(len(mi)):
                if a < b:
                    within.append(np.linalg.norm(ZL[mi[a]] - ZL[mi[b]]))
            others = [k for k in range(len(legkeys)) if k not in mi]
            for o in others:
                torest.append(np.linalg.norm(ZL[mi[a]] - ZL[o]))
        w = np.mean(within); t = np.mean(torest)
        verdict = "CLUSTERS" if w < t else "no cluster"
        print(f"  {her:18s} (n={len(members)}): within={w:.2f} to-rest={t:.2f} -> {verdict}")
    print()

    # ---- 5. LENGTH CONTROL ----
    print("## 5. Length control")
    print()
    nchars_all = np.array([r[2] for r in new], dtype=float)
    pc1_new = np.array([proj[i] for i, r in enumerate(allrows) if r in new]) if False else None
    # recompute pc1 for new rows by position
    newproj = []; newnch = []
    for i, r in enumerate(allrows):
        if i < len(new):
            newproj.append(proj[i]); newnch.append(r[2])
    newproj = np.array(newproj); newnch = np.array(newnch, dtype=float)
    if newnch.std() > 0:
        rho = np.corrcoef(newnch, newproj)[0, 1]
        print(f"  speech-level corr(n_chars, PC1) over new legislatures = {rho:+.3f}  (n={len(newnch)})")
    # length-matched band 1000-3000 chars: re-rank legislatures
    band = [(new[i][1], newproj[i]) for i in range(len(new)) if 1000 <= newnch[i] <= 3000]
    bl = defaultdict(list)
    for leg, p in band:
        bl[leg].append(p)
    print(f"  length-matched (1000-3000 chars, n={len(band)}) legislature PC1 rank:")
    for leg, ps in sorted(bl.items(), key=lambda x: np.mean(x[1])):
        print(f"    {leg:26s} n={len(ps):>2} PC1 {np.mean(ps):+.2f}")
    print()

    # ---- 6. TRANSLATION / LANGUAGE control ----
    print("## 6. Translation / language control")
    print()
    print("  native-non-English legislatures (7B scores these unevenly -> confound):")
    for g in legkeys:
        if g in META and META[g][3] == "native_nonEN":
            print(f"    {g:26s} PC1 {np.mean(by_pc1[g]):+.2f}  ({META[g][3]})")
    en_native = [np.mean(by_pc1[g]) for g in legkeys if g in META and META[g][3] == "en_native"]
    non_en = [np.mean(by_pc1[g]) for g in legkeys if g in META and META[g][3] == "native_nonEN"]
    en_tr = [np.mean(by_pc1[g]) for g in legkeys if g.startswith("EU:")]
    print(f"  mean PC1: en_native={np.mean(en_native):+.2f}  en_translated(EU)={np.mean(en_tr):+.2f}  "
          f"native_nonEN={np.mean(non_en):+.2f}")
    print()
    print("(verdict written in RESULT.md prose)")


if __name__ == "__main__":
    main()
