#!/usr/bin/env python3
"""cc_crosssite_fleeson.py — the FLEESON REDUCTION (INTERNAL HOLD). CPU only. ANALYSIS ONLY (no scoring).

Fleeson (2001), the density-distribution view of whole-trait theory, treats each person as a DISTRIBUTION of
momentary states. His decomposition splits the variance of a state into a BETWEEN-PERSON component (the person's
mean = the stable trait density) and a WITHIN-PERSON-ACROSS-OCCASIONS component (the spread of that person's
states around their own mean = the situation/state term). His headline finding: within-person variability is
about as large as between-person variability, so momentary behaviour is roughly HALF stable trait and HALF
situation.

This reproduces that decomposition in his own variance-component form on our cross-site corpus, where the
"occasions" a person is seen in are the separate sites they write on (the room = the situation). For each
DYNAMICS-8 disposition axis and each DYNAMICS-WEB character axis we fit the one-way random-effects model

    y_ij = mu + p_i + e_ij         p_i ~ (0, s2_between)   e_ij ~ (0, s2_within)

and report the two variance components and their shares. trait share = s2_between/(s2_between+s2_within) = ICC(1)
= Fleeson's between-person fraction; situation share = 1 - trait share = his within-person fraction. We compare
the situation share directly to his ~50%.

Two estimators, as in the coupling result:
  - all-occasions : every block is one occasion (within-site repeats fold into the situation term).
  - room-level    : average a person's blocks to one mean per site first, so the within-person term is purely
                    ACROSS SITUATIONS (rooms) — the faithful person-vs-situation split, closest to Fleeson's
                    design where each occasion is a distinct situation.

Reads cc_v3.crosssite_authorship rows carrying both disp_d8 and char_dweb. Aggregate only: no text, no key, no
name. Env: MINDOM (2, min sites/person), OUT (json path).
"""
import os, json, numpy as np, psycopg2
def _obj(x):
    """coerce a jsonb/text score cell to a dict (psycopg2 may hand back str)."""
    if isinstance(x,str):
        try: return json.loads(x)
        except Exception: return None
    return x
MINDOM=int(os.environ.get("MINDOM","2"))
OUT=os.environ.get("OUT","")
D8   = ["discipline","yielding","novelty","acuity","mercuriality","impulsivity","candour","sociability"]
DWEB = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
DSN=f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"

def var_components(values, labels, ngroups):
    """One-way random-effects variance components (Fleeson's density-distribution decomposition), vectorised.
    values: flat float array of one axis's scores; labels: int person-id per value; ngroups: number of persons.
    s2_within  = MSW                          (within-person, across occasions = the SITUATION term)
    s2_between = (MSB - MSW)/kbar              (between-person = the stable TRAIT density)
    trait_share = s2_between/(s2_between+s2_within)   (= ICC(1), Fleeson's between-person fraction)
    """
    N=values.size; g=ngroups
    if g<2 or N-g<1: return float("nan"), float("nan"), float("nan")
    n_i=np.bincount(labels, minlength=g).astype(float)
    sum_i=np.bincount(labels, weights=values, minlength=g)
    mean_i=sum_i/np.where(n_i>0,n_i,1)
    grand=values.mean()
    ssb=float(np.sum(n_i*(mean_i-grand)**2))
    sst=float(np.sum((values-grand)**2))
    ssw=sst-ssb
    msb=ssb/(g-1); msw=ssw/(N-g)
    kbar=(N-float(np.sum(n_i**2))/N)/(g-1)
    s2_within=msw
    s2_between=(msb-msw)/kbar if kbar>0 else float("nan")
    tot=s2_between+s2_within
    trait_share=s2_between/tot if tot>0 else float("nan")
    return s2_between, s2_within, trait_share

def load():
    db=psycopg2.connect(DSN); c=db.cursor()
    c.execute(f"""WITH multi AS (SELECT ident FROM cc_v3.crosssite_authorship
                                 GROUP BY ident HAVING count(distinct domain) >= {MINDOM})
                  SELECT a.ident, a.domain, a.disp_d8, a.char_dweb
                  FROM cc_v3.crosssite_authorship a JOIN multi m USING (ident)
                  WHERE a.disp_d8 IS NOT NULL AND a.char_dweb IS NOT NULL""")
    return c.fetchall()

def decompose(rows, axes, col_idx, estimator):
    """estimator: 'all' (every block an occasion) or 'room' (one mean per site first)."""
    # by[ident] -> list of block dicts ; or list of per-site mean dicts
    by={}; skipped=0
    for r in rows:
        ident=r[0]; dom=r[1]; obj=_obj(r[col_idx])
        if not isinstance(obj,dict) or any(ax not in obj for ax in axes):
            skipped+=1; continue
        by.setdefault(ident,{}).setdefault(dom,[]).append(obj)
    if skipped: print(f"  [note] {estimator}/{col_idx}: skipped {skipped:,} blocks with missing/variant axis keys")
    # build flat value + integer-label arrays per axis (occasion = block, or per-site mean)
    vals={ax:[] for ax in axes}; labs=[]
    npers=0; nocc=0
    for ident, doms in by.items():
        if estimator=="all":
            occasions=[o for lst in doms.values() for o in lst]          # every block
        else:
            occasions=[{ax:float(np.mean([o[ax] for o in lst])) for ax in axes} for lst in doms.values()]  # one per site
        if len(occasions)<2:      # need >=2 occasions to see within-person spread
            continue
        pid=npers; npers+=1; nocc+=len(occasions)
        for o in occasions:
            labs.append(pid)
            for ax in axes: vals[ax].append(float(o[ax]))
    labels=np.asarray(labs, dtype=np.int64)
    res={}
    for ax in axes:
        s2b,s2w,tr=var_components(np.asarray(vals[ax],dtype=float), labels, npers)
        res[ax]=dict(s2_between=s2b, s2_within=s2w, trait_share=tr, situation_share=1-tr)
    tr_mean=float(np.nanmean([res[ax]["trait_share"] for ax in axes]))
    return dict(estimator=estimator, n_persons=npers, n_occasions=nocc,
                per_axis=res, trait_share=tr_mean, situation_share=1-tr_mean)

def show(title, d):
    print(f"\n=== {title} [{d['estimator']}] — {d['n_persons']:,} persons, {d['n_occasions']:,} occasions ===")
    print(f"  {'axis':16s} {'s2_between(trait)':>18s} {'s2_within(situ)':>16s} {'trait%':>8s} {'situ%':>8s}")
    for ax,v in d["per_axis"].items():
        print(f"  {ax:16s} {v['s2_between']:18.4f} {v['s2_within']:16.4f} "
              f"{100*v['trait_share']:7.1f}% {100*v['situation_share']:7.1f}%")
    print(f"  ---> MEAN across axes: trait {100*d['trait_share']:.1f}%  |  situation {100*d['situation_share']:.1f}%")

def main():
    rows=load()
    print(f"[fleeson] {len(rows):,} scored cross-site blocks loaded (>= {MINDOM} sites/person)")
    out={}
    for label,axes,idx,key in [("DISPOSITION (DYNAMICS-8)",D8,2,"disposition"),
                               ("CHARACTER (DYNAMICS-WEB)",DWEB,3,"character")]:
        out[key]={}
        for est in ("all","room"):
            d=decompose(rows,axes,idx,est)
            show(label,d)
            out[key][est]=d
    # combined headline: pool disposition+character room-level trait shares
    combos=[]
    for key in ("disposition","character"):
        combos.append(out[key]["room"]["trait_share"])
    pooled=float(np.mean(combos))
    print(f"\n########## FLEESON HEADLINE (room-level, person-vs-situation) ##########")
    for key in ("disposition","character"):
        d=out[key]["room"]
        print(f"  {key:12s}: trait {100*d['trait_share']:.1f}%  situation {100*d['situation_share']:.1f}%")
    print(f"  pooled     : trait {100*pooled:.1f}%  situation {100*(1-pooled):.1f}%   (Fleeson ~50/50)")
    out["headline"]=dict(pooled_trait_share=pooled, pooled_situation_share=1-pooled)
    if OUT:
        json.dump(out, open(OUT,"w"), indent=2)
        print(f"\n[fleeson] wrote {OUT}")
    print("[fleeson] done. INTERNAL HOLD — aggregate only, no keys, no names.")

if __name__=="__main__":
    main()
