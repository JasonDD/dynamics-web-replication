#!/usr/bin/env python3
"""Translator fingerprint: per-language 8-axis character offset, variance explained,
Europarl vs Bible cross-corpus replication. Same DWEB axes + series PC1 basis."""
import os, json, numpy as np, psycopg2
from collections import defaultdict
from scipy import stats

DWEB=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
EP_LANGS=["en","de","fr","es","it","fi","pl","el"]
EP_SCORED="the internal corpus store/europarl_multiway/scored.jsonl"
BIB_SCORED="the internal corpus store/bible_multilingual/fingerprint_scored.jsonl"

# --- series PC1 basis from DB ---
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
c=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs").cursor()
c.execute(f"SELECT {','.join(DWEB)} FROM the internal reference table")
allc=np.array([[float(x) for x in r] for r in c.fetchall()],float)
MEAN=allc.mean(0); STD=allc.std(0)+1e-9
_,_,Vt=np.linalg.svd((allc-MEAN)/STD,full_matrices=False); PC1=Vt[0]
if (PC1[DWEB.index("rigour")]+PC1[DWEB.index("depth")])<0: PC1=-PC1
def pc1(ch): return float(((np.array([ch[a] for a in DWEB],float)-MEAN)/STD)@PC1)

# ================= EUROPARL =================
data=defaultdict(dict)
for l in open(EP_SCORED):
    try: r=json.loads(l)
    except: continue
    if "char" not in r or "__" not in r["id"]: continue
    item,lang=r["id"].split("__",1)
    if lang not in EP_LANGS: continue
    ch=r["char"]; data[item][lang]={a:float(ch[a]) for a in DWEB}
items=[it for it in data if all(lg in data[it] for lg in EP_LANGS)]; items.sort()
I=len(items); J=len(EP_LANGS)
print(f"[EUROPARL] complete items {I} x {J} langs")

def mat(axis,langs,dat,itms):
    return np.array([[dat[it][lg][axis] for lg in langs] for it in itms],float)

# per-axis pooled SD (over all versions) for z-scoring the offsets
allvals={a:mat(a,EP_LANGS,data,items) for a in DWEB}
axis_sd={a:allvals[a].std() for a in DWEB}
grand={a:allvals[a].mean() for a in DWEB}
lang_mean={lg:{a:allvals[a][:,j].mean() for a in DWEB} for j,lg in enumerate(EP_LANGS)}

# language main-effect share per axis (two-way random effects, item x lang)
def two_way(Y):
    I,J=Y.shape; gm=Y.mean(); ri=Y.mean(1); cj=Y.mean(0)
    SSi=J*np.sum((ri-gm)**2); SSl=I*np.sum((cj-gm)**2)
    res=Y-ri[:,None]-cj[None,:]+gm; SSr=np.sum(res**2)
    MSi=SSi/(I-1); MSl=SSl/(J-1); MSr=SSr/((I-1)*(J-1))
    vi=max((MSi-MSr)/J,0); vl=max((MSl-MSr)/I,0); vr=MSr; tot=vi+vl+vr or 1
    pl=stats.f.sf(MSl/MSr,J-1,(I-1)*(J-1))
    return 100*vi/tot,100*vl/tot,100*vr/tot,pl
print("\n[EUROPARL] per-axis language main-effect share (item x lang two-way):")
print(f"{'axis':<17}{'content%':>9}{'lang%':>7}{'resid%':>8}{'p_lang':>10}")
ep_langpct={}
for a in DWEB+["_PC1"]:
    if a=="_PC1":
        Y=np.array([[pc1(data[it][lg]) for lg in EP_LANGS] for it in items],float)
    else: Y=allvals[a]
    cpc,lpc,rpc,pl=two_way(Y); ep_langpct[a]=lpc
    print(f"{a:<17}{cpc:>9.1f}{lpc:>7.1f}{rpc:>8.1f}{pl:>10.1e}")

# FINGERPRINT: per-language 8-axis offset vs English (z-scored by pooled axis SD)
en_mean={a:lang_mean['en'][a] for a in DWEB}
def ep_fp_vs_en(lg): return np.array([(lang_mean[lg][a]-en_mean[a])/axis_sd[a] for a in DWEB])
def ep_fp_vs_grand(lg): return np.array([(lang_mean[lg][a]-grand[a])/axis_sd[a] for a in DWEB])
print("\n[EUROPARL] FINGERPRINT: per-language 8-axis offset vs ENGLISH (z units, pooled axis SD)")
print(f"{'lang':<5}"+"".join(f"{a[:5]:>8}" for a in DWEB)+f"{'||len':>8}")
ep_fp={}
for lg in EP_LANGS:
    v=ep_fp_vs_en(lg); ep_fp[lg]=v
    print(f"{lg:<5}"+"".join(f"{x:>+8.2f}" for x in v)+f"{np.linalg.norm(v):>8.2f}")

# DECOMPOSE the fingerprint: shared "translationese" direction vs language-specific residual
nonen=[lg for lg in EP_LANGS if lg!="en"]
FP=np.array([ep_fp[lg] for lg in nonen])              # 7 x 8
generic=FP.mean(0)                                    # shared translation-out-of-English direction
spec={lg:ep_fp[lg]-generic for lg in nonen}           # language-specific residual
print("\n[EUROPARL] GENERIC translationese vector (mean over 7 targets, z units) + its share:")
print(f"{'':<8}"+"".join(f"{a[:5]:>8}" for a in DWEB)+f"{'||len':>8}")
print(f"{'GENERIC':<8}"+"".join(f"{x:>+8.2f}" for x in generic)+f"{np.linalg.norm(generic):>8.2f}")
tot_ss=float((FP**2).sum()); gen_ss=float((np.tile(generic,(len(nonen),1))**2).sum())
spec_ss=float((np.array([spec[lg] for lg in nonen])**2).sum())
print(f"  share of total offset energy: GENERIC(common)={100*gen_ss/tot_ss:.0f}%  LANGUAGE-SPECIFIC={100*spec_ss/tot_ss:.0f}%")
print("\n[EUROPARL] LANGUAGE-SPECIFIC residual fingerprint (offset minus generic translationese):")
print(f"{'lang':<5}"+"".join(f"{a[:5]:>8}" for a in DWEB)+f"{'||len':>8}")
for lg in nonen:
    v=spec[lg]; print(f"{lg:<5}"+"".join(f"{x:>+8.2f}" for x in v)+f"{np.linalg.norm(v):>8.2f}")

# raw (0-1) offsets vs English too, for readability
print("\n[EUROPARL] raw mean per axis per language (0-1 scale):")
print(f"{'lang':<5}"+"".join(f"{a[:5]:>8}" for a in DWEB))
for lg in EP_LANGS:
    print(f"{lg:<5}"+"".join(f"{lang_mean[lg][a]:>8.3f}" for a in DWEB))

# ================= BIBLE =================
if os.path.exists(BIB_SCORED):
    bib=defaultdict(dict)  # bib[(pair,idx)][lang]=axes
    for l in open(BIB_SCORED):
        try: r=json.loads(l)
        except: continue
        if "char" not in r: continue
        parts=r["id"].split("__")
        if len(parts)!=3: continue
        pair,idx,lg=parts
        bib[(pair,idx)][lg]={a:float(r["char"][a]) for a in DWEB}
    # paired offset target-minus-eng per language
    PAIR_TGT={"eng-deu":"deu","eng-fra":"fra","eng-spa":"spa","eng-por":"por",
              "eng-arb":"arb","eng-cmn":"cmn","eng-swh":"swh"}
    # map bible lang codes to europarl 2-letter where they overlap
    MAP={"deu":"de","fra":"fr","spa":"es","por":"pt","arb":"ar","cmn":"zh","swh":"sw"}
    print(f"\n[BIBLE] scored versions loaded, verse-cells {len(bib)}")
    # per-pair pooled SD from all bible versions of eng+target for z-scoring
    # gather all axis values (eng + targets pooled) for pooled SD
    allb={a:[] for a in DWEB}
    for cell in bib.values():
        for lg,ax in cell.items():
            for a in DWEB: allb[a].append(ax[a])
    bib_sd={a:(np.std(allb[a]) or 1e-9) for a in DWEB}
    bib_fp={}; bib_n={}
    print("\n[BIBLE] FINGERPRINT: paired (target - English) 8-axis offset (z units, pooled bible SD)")
    print(f"{'lang':<6}"+"".join(f"{a[:5]:>8}" for a in DWEB)+f"{'||len':>8}{'nPairs':>8}")
    for pair,tgt in PAIR_TGT.items():
        diffs={a:[] for a in DWEB}
        for (p,idx),cell in bib.items():
            if p!=pair: continue
            if "eng" in cell and tgt in cell:
                for a in DWEB: diffs[a].append(cell[tgt][a]-cell["eng"][a])
        n=len(diffs[DWEB[0]])
        if n<20: continue
        v=np.array([np.mean(diffs[a])/bib_sd[a] for a in DWEB])
        bib_fp[MAP[tgt]]=v; bib_n[MAP[tgt]]=n
        print(f"{MAP.get(tgt,tgt):<6}"+"".join(f"{x:>+8.2f}" for x in v)+f"{np.linalg.norm(v):>8.2f}{n:>8}")

    # ---- CROSS-CORPUS REPLICATION (overlap: de, fr, es) ----
    # Bible offsets are vs-English (paired); compare to Europarl vs-English offsets.
    overlap=[lg for lg in ["de","fr","es"] if lg in bib_fp and lg in ep_fp]
    print("\n[CROSS-CORPUS] per-language fingerprint agreement Europarl vs Bible (both vs English, 8-axis z-vectors)")
    print(f"{'lang':<5}{'cosine':>9}{'pearson_r':>11}")
    for lg in overlap:
        e=ep_fp[lg]; b=bib_fp[lg]
        cos=float(e@b/(np.linalg.norm(e)*np.linalg.norm(b)+1e-9))
        pr=float(stats.pearsonr(e,b)[0])
        print(f"{lg:<5}{cos:>9.3f}{pr:>11.3f}")
    # pooled: stack overlap langs and correlate the full offset picture
    if overlap:
        E=np.concatenate([ep_fp[lg] for lg in overlap]); Bv=np.concatenate([bib_fp[lg] for lg in overlap])
        cos=float(E@Bv/(np.linalg.norm(E)*np.linalg.norm(Bv)+1e-9)); pr=float(stats.pearsonr(E,Bv)[0])
        print(f"{'POOL':<5}{cos:>9.3f}{pr:>11.3f}   (langs {','.join(overlap)}, {8*len(overlap)} axis-cells)")
    # also: do languages have DISTINCT fingerprints? cross-lang cosine within each corpus
    print("\n[EUROPARL] between-language fingerprint distinctness (cosine of vs-English offset vectors, non-en):")
    nl=[lg for lg in EP_LANGS if lg!="en"]
    for i,a in enumerate(nl):
        row=[]
        for b in nl:
            cs=ep_fp[a]@ep_fp[b]/(np.linalg.norm(ep_fp[a])*np.linalg.norm(ep_fp[b])+1e-9)
            row.append(f"{cs:+.2f}")
        print(f"  {a}: "+" ".join(row))
else:
    print("\n[BIBLE] fingerprint_scored.jsonl not present yet; run scorer first.")
