#!/usr/bin/env python3
"""length_mechanism.py — test "MATTER NEEDS BANDWIDTH, MANNER IS INSTANT".

Hypothesis: the length of a text is the mechanism behind the matter/manner axis.
Matter axes (rigour, depth) can only express their variance once a text is long
enough to build an argument; manner axes (affect, stance, register) saturate
almost immediately in a phrase.

PURE ANALYSIS on already-scored data. No new scoring. No :8301/:8288 calls.

Sources (each already has an 8-axis char score AND a recoverable word count):
  ira        IRA troll tweets   -- scored.jsonl char x score_input.jsonl text  (SHORT)
  cmv        Reddit CMV args    -- cmv_scores.jsonl char x utterances.jsonl text (LONG)
  parlamint  parliament speech  -- sample_scored.jsonl  (char + n_words embedded)
  oldbailey  trial proceedings  -- oldbailey_scored.jsonl (char + nwords embedded)
"""
import os, json, numpy as np, psycopg2

DWEB   = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
MATTER = ["rigour","depth"]
MANNER = ["affect","stance","register"]
NASC   = "/mnt/nas/kronaxis/corpora"

# ---- matter/manner PC1 (SVD on cc_v3.domain_char8_expanded), oriented rigour+depth positive
PW = [l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
c = psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs").cursor()
c.execute(f"SELECT {','.join(DWEB)} FROM cc_v3.domain_char8_expanded")
allc = np.array([[float(x) for x in r] for r in c.fetchall()], float)
MEAN = allc.mean(0); STD = allc.std(0) + 1e-9
_,_,Vt = np.linalg.svd((allc-MEAN)/STD, full_matrices=False); PC1 = Vt[0]
if (PC1[DWEB.index("rigour")]+PC1[DWEB.index("depth")]) < 0:
    PC1 = -PC1
def pc1(ch):
    return float(((np.array([ch[a] for a in DWEB],float)-MEAN)/STD) @ PC1)
print(f"[pc1] reference n={len(allc)}  PC1 loadings: " + ", ".join(f"{a}={PC1[i]:+.2f}" for i,a in enumerate(DWEB)))

def wc(t):
    return len(t.split()) if isinstance(t,str) else 0

# ---------- load each source into (char dict, word_count) ----------
def load_ira():
    txt = {}
    for l in open(f"{NASC}/ira_troll/work/score_input.jsonl"):
        r = json.loads(l)
        if r.get("kind")=="ira": txt[r["id"]] = r.get("text","")
    out=[]
    for l in open(f"{NASC}/ira_troll/work/scored.jsonl"):
        r = json.loads(l)
        if r.get("kind")!="ira" or "char" not in r: continue
        if not all(a in r["char"] for a in DWEB): continue
        t = txt.get(r["id"])
        if t is None: continue
        n = wc(t)
        if n<1: continue
        out.append((r["char"], n))
    return out

def load_cmv():
    # word count per utterance id from the big utterances file
    txt={}
    for l in open(f"{NASC}/cmv_winning_args/winning-args-corpus/utterances.jsonl"):
        try: r=json.loads(l)
        except Exception: continue
        i=r.get("id"); t=r.get("text")
        if i is not None and isinstance(t,str): txt[i]=wc(t)
    out=[]
    for l in open(f"{NASC}/cmv_winning_args/cmv_scores.jsonl"):
        try: r=json.loads(l)
        except Exception: continue
        if r.get("skip"): continue
        ch=r.get("char")
        if not isinstance(ch,dict) or not all(a in ch for a in DWEB): continue
        n=txt.get(r.get("id"))
        if not n or n<1: continue
        out.append((ch,n))
    return out

def load_field(path, wf):
    out=[]
    for l in open(path):
        try: r=json.loads(l)
        except Exception: continue
        ch=r.get("char")
        if not isinstance(ch,dict) or not all(a in ch for a in DWEB): continue
        n=r.get(wf)
        if n is None or n<1: continue
        out.append((ch,int(n)))
    return out

SOURCES = {
    "ira":       load_ira(),
    "cmv":       load_cmv(),
    "parlamint": load_field(f"{NASC}/parlamint/sample_scored.jsonl", "n_words"),
    "oldbailey": load_field(f"{NASC}/oldbailey/oldbailey_scored.jsonl", "nwords"),
}

print("\n=== source sizes and length ranges ===")
print("  " + "source".ljust(12) + "n".rjust(7) + "  wc: min   p10   p50   p90   max")
for s,rows in SOURCES.items():
    if not rows:
        print("  "+s.ljust(12)+"   (empty)"); continue
    w=np.array([n for _,n in rows])
    q=np.percentile(w,[0,10,50,90,100])
    print("  "+s.ljust(12)+f"{len(rows):7d}"+"     "+" ".join(f"{int(x):5d}" for x in q))

# ---------- binning ----------
BINS = [(0,20),(20,50),(50,100),(100,300),(300,1000),(1000,10**9)]
BLAB = ["0-20","20-50","50-100","100-300","300-1000","1000+"]
def binof(n):
    for i,(lo,hi) in enumerate(BINS):
        if lo<=n<hi: return i
    return len(BINS)-1

def axis_arr(rows):
    return {a:np.array([ch[a] for ch,_ in rows],float) for a in DWEB}

def per_bin_stats(rows, minbin=25):
    """returns dict bin_index -> (n, median_wc, {axis: (mean,var)})"""
    buckets={}
    for ch,n in rows:
        buckets.setdefault(binof(n),[]).append((ch,n))
    res={}
    for bi,items in sorted(buckets.items()):
        if len(items)<minbin: continue
        med=np.median([n for _,n in items])
        st={}
        for a in DWEB:
            v=np.array([ch[a] for ch,_ in items],float)
            st[a]=(v.mean(),v.var())
        res[bi]=(len(items),med,st)
    return res

def report_binned(title, rows, minbin=25):
    print(f"\n{'='*78}\n{title}   (n={len(rows)})\n{'='*78}")
    st=per_bin_stats(rows,minbin)
    if len(st)<2:
        print("  too few populated bins for a slope"); return None
    bins_used=sorted(st)
    logmed=np.array([np.log10(st[b][1]) for b in bins_used])
    # ---- VARIANCE table
    print("\n-- VARIANCE (spread) of each axis per length bin --")
    hdr="  "+"bin".ljust(10)+"n".rjust(6)+"medwc".rjust(7)+"".join(a[:5].rjust(8) for a in DWEB)
    print(hdr)
    for b in bins_used:
        n,med,s=st[b]
        print("  "+BLAB[b].ljust(10)+f"{n:6d}"+f"{int(med):7d}"+"".join(f"{s[a][1]:8.3f}" for a in DWEB))
    # ---- MEAN table
    print("\n-- MEAN of each axis per length bin --")
    print(hdr)
    for b in bins_used:
        n,med,s=st[b]
        print("  "+BLAB[b].ljust(10)+f"{n:6d}"+f"{int(med):7d}"+"".join(f"{s[a][0]:8.3f}" for a in DWEB))
    # ---- correlations of per-bin variance and mean vs log median length
    print("\n-- corr(axis stat vs log10 length) across bins, + var ratio (largest bin / smallest bin) --")
    print("  "+"axis".ljust(18)+"pole".rjust(8)+"r(var~len)".rjust(12)+"r(mean~len)".rjust(12)+"varRatio".rjust(10))
    summ={}
    for a in DWEB:
        var=np.array([st[b][2][a][1] for b in bins_used])
        men=np.array([st[b][2][a][0] for b in bins_used])
        rv=np.corrcoef(logmed,var)[0,1] if var.std()>1e-12 else float("nan")
        rm=np.corrcoef(logmed,men)[0,1] if men.std()>1e-12 else float("nan")
        ratio=(var[-1]/var[0]) if var[0]>1e-9 else float("nan")
        pole="MATTER" if a in MATTER else ("MANNER" if a in MANNER else "-")
        summ[a]=(rv,rm,ratio)
        print("  "+a.ljust(18)+pole.rjust(8)+f"{rv:12.3f}"+f"{rm:12.3f}"+f"{ratio:10.2f}")
    mv=np.nanmean([summ[a][0] for a in MATTER]); nv=np.nanmean([summ[a][0] for a in MANNER])
    mr=np.nanmean([summ[a][2] for a in MATTER]); nr=np.nanmean([summ[a][2] for a in MANNER])
    print(f"\n  MATTER mean r(var~len)={mv:+.3f}  varRatio={mr:.2f}")
    print(f"  MANNER mean r(var~len)={nv:+.3f}  varRatio={nr:.2f}")
    print(f"  --> matter-minus-manner variance-slope gap = {mv-nv:+.3f}  (hypothesis predicts > 0)")
    return summ

# ---------- POOLED ----------
pooled=[]
for s,rows in SOURCES.items(): pooled+=rows
report_binned("POOLED (all sources) — composition-confounded, context only", pooled, minbin=30)

# ---------- WITHIN-SOURCE (the clean test) ----------
for s in ("parlamint","oldbailey","cmv","ira"):
    report_binned(f"WITHIN SOURCE: {s}", SOURCES[s], minbin=25)

# ---------- item-level Spearman (mean trajectory), within source ----------
def spearman(x,y):
    xr=np.argsort(np.argsort(x)); yr=np.argsort(np.argsort(y))
    return np.corrcoef(xr,yr)[0,1]
print(f"\n{'='*78}\nITEM-LEVEL Spearman(axis value ~ word count), within source (mean trajectory)\n{'='*78}")
print("  "+"source".ljust(12)+"".join(a[:5].rjust(8) for a in DWEB)+"     PC1")
for s,rows in SOURCES.items():
    if len(rows)<50: continue
    w=np.array([n for _,n in rows],float)
    line="  "+s.ljust(12)
    for a in DWEB:
        v=np.array([ch[a] for ch,_ in rows],float)
        line+=f"{spearman(w,v):8.2f}"
    p=np.array([pc1(ch) for ch,_ in rows])
    line+=f"{spearman(w,p):8.2f}"
    print(line)

# ---------- SHORT-END SWITCH-ON (the precise test) ----------
# Matter needs a minimum bandwidth before its spread can open at all; manner is
# already maxed in a phrase. So crossing from a ~12-word phrase to a ~70-word
# passage, matter VARIANCE should RISE (switch on) while manner variance, already
# saturated, only converges downward. Past ~100 words everything converges, so a
# single linear slope over the whole range is negative and misleading.
def short_end(title, rows):
    b0=[ch for ch,n in rows if binof(n)==0]      # 0-20
    b2=[ch for ch,n in rows if binof(n)==2]      # 50-100
    if len(b0)<25 or len(b2)<25:
        print(f"\n[{title}] no sub-20 + 50-100 coverage (min n) -> switch-on not observable"); return
    print(f"\n-- SHORT-END switch-on {title}: var(50-100)/var(0-20), >1 = spread opens with length --")
    print("  "+"axis".ljust(18)+"pole".rjust(8)+"var0-20".rjust(9)+"var50-100".rjust(10)+"ratio".rjust(8)+"  meanShift")
    mr=[]; nr=[]
    for a in DWEB:
        v0=np.var([ch[a] for ch in b0]); v2=np.var([ch[a] for ch in b2])
        m0=np.mean([ch[a] for ch in b0]); m2=np.mean([ch[a] for ch in b2])
        ratio=v2/v0 if v0>1e-9 else float("nan")
        pole="MATTER" if a in MATTER else ("MANNER" if a in MANNER else "-")
        if a in MATTER: mr.append(ratio)
        if a in MANNER: nr.append(ratio)
        print("  "+a.ljust(18)+pole.rjust(8)+f"{v0:9.3f}"+f"{v2:10.3f}"+f"{ratio:8.2f}"+f"   {m2-m0:+.3f}")
    print(f"  MATTER mean switch-on ratio = {np.nanmean(mr):.2f}   MANNER mean switch-on ratio = {np.nanmean(nr):.2f}")

print(f"\n{'='*78}\nSHORT-END SWITCH-ON TEST (phrase -> passage)\n{'='*78}")
short_end("POOLED", pooled)
short_end("cmv", SOURCES["cmv"])

# ---------- PC1 (matter/manner) mean trajectory by length, pooled ----------
print(f"\n{'='*78}\nmatter/manner PC1 mean by length bin (pooled) -- is the axis a length axis?\n{'='*78}")
buckets={}
for ch,n in pooled: buckets.setdefault(binof(n),[]).append(pc1(ch))
print("  "+"bin".ljust(10)+"n".rjust(7)+"medPC1".rjust(9))
for bi in sorted(buckets):
    if len(buckets[bi])<30: continue
    print("  "+BLAB[bi].ljust(10)+f"{len(buckets[bi]):7d}"+f"{np.mean(buckets[bi]):9.3f}")

print("\n[done]")
