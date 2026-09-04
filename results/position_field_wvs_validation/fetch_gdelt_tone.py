#!/usr/bin/env python3
"""Fetch GDELT country level average tone per WVS topic, over the WVS Wave 7 window.

FREE access only: GDELT DOC 2.0 API (api.gdeltproject.org), mode=TimelineTone, filtered
by a GKG theme and by sourcecountry (the FIPS country of the news outlet). No BigQuery,
no billed access, no article text fetch, no scoring. This is pass one: GDELT's own theme
filtered average tone is used as the cheapest position proxy.

Tone is a sentiment score (roughly -10..+10), NOT a for/against stance. That caveat is
carried through to the result.

Empty time bins are returned by GDELT as value 0; we average over the non-zero bins so
that quiet periods do not pull every country toward zero.

Window: 2017-01-01 .. 2022-12-31 (covers WVS7 fieldwork 2017-2022; GDELT DOC starts 2017).

Resumable: rows already in the output CSV are skipped, so a killed run can be restarted.
Paced at PACE seconds per call: the DOC API rate limits aggressively and returns an empty
body when tripped, so retries back off hard and a bin count of zero is retried.
"""
import os, sys, time, json, csv, urllib.request, urllib.parse

WVS = "the internal corpus store/wvs_position/wvs_country_items.csv"
OUT = "the internal corpus store/gdelt_position"
os.makedirs(OUT, exist_ok=True)
OUTCSV = f"{OUT}/gdelt_country_tone.csv"
# The DOC API cannot serve a single 6-year TimelineTone call (it times out well past
# 120s). It serves a one-year window fast, so each pair is fetched year by year and the
# daily tone bins are concatenated across 2017..2022, then averaged. Window still covers
# the WVS7 fieldwork span.
YEARS = list(range(2017, 2023))
PACE = 20.0
TIMEOUT = 90
API = "https://api.gdeltproject.org/api/v2/doc/doc"

# WVS item -> candidate GKG themes. Where a topic has no single clean theme we fetch a
# couple of candidates and let the analysis pick the better behaved mapping.
THEME_MAP = {
    "immigration_restrictiveness":  ["IMMIGRATION"],
    "religiosity_importance_of_god":["RELIGION"],
    "democracy_importance":         ["DEMOCRACY"],
    "confidence_in_government":      ["CORRUPTION", "GENERAL_GOVERNMENT"],
    "gender_men_better_leaders":    ["DISCRIMINATION", "SOC_GENDEREQUALITY"],
}

def get_json(url, tries=6):
    """Return parsed JSON, or None if every attempt failed (network reset / rate block /
    empty body). None means 'could not reach the API' and the caller must NOT mark the
    pair done, so a later run retries it."""
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "kronaxis-research/1.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                raw = r.read().decode("utf-8", "replace").strip()
            if not raw:
                sys.stderr.write(f"  empty body, backoff (try {k+1})\n")
                time.sleep(PACE * (k + 2)); continue
            return json.loads(raw)
        except Exception as e:
            sys.stderr.write(f"  retry {k+1}: {str(e)[:80]}\n")
            time.sleep(PACE * (k + 2))
    return None

def timeline_scalar(mode, theme, fips):
    """Fetch the tone timeline year by year over YEARS and concatenate the daily bins.
    Returns (data_list_or_None, n_bins). None means at least one year's call failed at
    the API level (network reset / rate block) so the caller must NOT record the pair and
    a later run retries the whole pair. A genuine empty result is ([], 0)."""
    q = urllib.parse.quote(f"theme:{theme} sourcecountry:{fips}")
    allbins = []
    for yr in YEARS:
        start = f"{yr}0101000000"
        end = f"{yr}1231235959"
        url = f"{API}?query={q}&mode={mode}&startdatetime={start}&enddatetime={end}&format=json"
        d = get_json(url)
        if d is None:
            return None, 0
        if d.get("timeline"):
            allbins.extend(d["timeline"][0].get("data", []))
        time.sleep(PACE)
    return allbins, len(allbins)

def main():
    need = []
    with open(WVS) as f:
        for row in csv.DictReader(f):
            if not row["fips"] or row["fips"] == "None":
                continue
            for th in THEME_MAP[row["item"]]:
                need.append((row["item"], th, row["fips"], row["country"]))

    done = set()
    if os.path.exists(OUTCSV):
        with open(OUTCSV) as f:
            for r in csv.DictReader(f):
                done.add((r["item"], r["theme"], r["fips"]))
    new = os.path.getsize(OUTCSV) == 0 if os.path.exists(OUTCSV) else True
    fh = open(OUTCSV, "a", newline="")
    w = csv.writer(fh)
    if new:
        w.writerow(["item", "theme", "fips", "country",
                    "tone_mean_nonzero", "n_bins", "n_nonzero"])
        fh.flush()

    total = len(need)
    print(f"pairs needed={total} already done={len(done)}", flush=True)
    for i, (item, theme, fips, country) in enumerate(need, 1):
        if (item, theme, fips) in done:
            continue
        tdata, nb = timeline_scalar("TimelineTone", theme, fips)
        if tdata is None:
            # API unreachable / rate blocked for this pair — do NOT record it, so a
            # rerun retries it. Pause longer to let a block clear.
            print(f"[{i}/{total}] {item} {theme} {fips} SKIP (api fail, will retry)",
                  flush=True)
            time.sleep(PACE * 3)
            continue
        tone_mean = ""
        n_nonzero = 0
        if tdata:
            nz = [p["value"] for p in tdata if p["value"] != 0]
            n_nonzero = len(nz)
            if nz:
                tone_mean = round(sum(nz) / len(nz), 4)
        w.writerow([item, theme, fips, country, tone_mean, nb, n_nonzero])
        fh.flush()
        print(f"[{i}/{total}] {item:32s} {theme:18s} {fips:3s} "
              f"tone={tone_mean} nz={n_nonzero}", flush=True)
        time.sleep(PACE)
    fh.close()
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
