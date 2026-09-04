#!/usr/bin/env python3
"""Correlate the GDELT country level tone signal against the WVS country opinion anchor.

For each WVS item x candidate GDELT theme, join on country, then report Pearson and
Spearman correlation with n and p value across the countries both cover. Higher WVS
mean directions are documented in the anchor file so the sign of an expected correlation
can be read off.

This is the validation result: does the free, no text, theme filtered GDELT tone track
the population opinion measured by the survey? A weak or wrong signed r is itself the
finding and is reported plainly.
"""
import csv, math
from collections import defaultdict

WVS = "the internal corpus store/wvs_position/wvs_country_items.csv"
GDELT = "the internal corpus store/gdelt_position/gdelt_country_tone.csv"
OUT = "the internal corpus store/gdelt_position/validation_table.csv"

def pearson(x, y):
    n = len(x)
    mx = sum(x) / n; my = sum(y) / n
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sxx = sum((a - mx) ** 2 for a in x); syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return float("nan")
    return sxy / math.sqrt(sxx * syy)

def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v); i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2.0 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r
    return pearson(rank(x), rank(y))

def pval(r, n):
    if n < 4 or math.isnan(r) or abs(r) >= 1:
        return float("nan")
    t = r * math.sqrt((n - 2) / (1 - r * r))
    # two sided p via a normal approximation (adequate for reporting magnitude)
    z = abs(t)
    p = math.erfc(z / math.sqrt(2))
    return p

def main():
    wvs = {}
    direction = {}
    for r in csv.DictReader(open(WVS)):
        wvs[(r["item"], r["fips"])] = float(r["wvs_mean"])
        direction[r["item"]] = r["higher_means"]

    gd = defaultdict(dict)  # (item,theme) -> {fips: tone}
    for r in csv.DictReader(open(GDELT)):
        v = r.get("tone_mean_nonzero", "")
        if v not in ("", None):
            gd[(r["item"], r["theme"])][r["fips"]] = float(v)

    out = [["item", "theme", "n_countries",
            "pearson_r", "pearson_p", "spearman_r", "spearman_p",
            "higher_wvs_means"]]
    print(f"{'item':32s} {'theme':16s} {'n':>3s} "
          f"{'pear_r':>7s} {'p':>7s} {'spear_r':>7s} {'p':>7s}")
    for (item, theme), tones in sorted(gd.items()):
        xs, ys = [], []
        for fips, tone in tones.items():
            w = wvs.get((item, fips))
            if w is not None:
                xs.append(tone); ys.append(w)
        n = len(xs)
        if n < 4:
            continue
        pr = pearson(xs, ys); sr = spearman(xs, ys)
        pp = pval(pr, n); sp = pval(sr, n)
        out.append([item, theme, n, round(pr, 3), round(pp, 4),
                    round(sr, 3), round(sp, 4), direction[item]])
        print(f"{item:32s} {theme:16s} {n:3d} "
              f"{pr:7.3f} {pp:7.4f} {sr:7.3f} {sp:7.4f}")

    with open(OUT, "w", newline="") as f:
        csv.writer(f).writerows(out)
    print("wrote", OUT)

if __name__ == "__main__":
    main()
