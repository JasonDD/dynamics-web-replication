#!/usr/bin/env python3
"""analyse_african.py -- the AFRICAN LANGUAGES CHARACTER MATRIX.

Inputs (scored by cc_found_human_score.py on the free 7B , same instrument as the whole series):
  scored_news.jsonl   masakhanews, 16 languages (genre = news, held constant)
  scored_tweet.jsonl  afrisenti, 15 languages (genre = social, robustness panel)
Each row: {id, outcome, kind(lang), char:{8 axes}}.  Also reads the score_input_*.jsonl to compute
per-language COVERAGE (scored / attempted) as a direct scorer-competence proxy.

Tests:
  (1) MATTER/MANNER PC1 structure -- pooled PC1 loadings interpreted; per-language PC1 cosine to the
      pooled reference axis (does the same axis reproduce within each African language?).
  (2) WHERE languages sit -- language x mean-vector distance, hierarchical clustering, nearest
      neighbours, 2D MDS; tested against language FAMILY / REGION / COLONIAL-language metadata.
  (3) AFFECT/MANNER level vs European-language NEWS -- eng+fra configs are the genre-controlled
      European-language-news baseline (same MasakhaNEWS protocol). African-14 pooled vs eng/fra.
  CAVEAT metrics -- coverage per language, per-axis within-language variance (degeneracy flag),
      non-Latin script + smallest-corpus flags. Honest bound on low-resource scorer quality.

numpy only.
"""
import os, json, sys, collections, numpy as np

DWEB   = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
MATTER = ["rigour","depth"]
MANNER = ["affect","stance","register"]
D = "the internal corpus store/african_charmatrix"

# ---- language metadata (Africa) ----
FAMILY = {"amh":"Semitic","tir":"Semitic","orm":"Cushitic","som":"Cushitic","hau":"Chadic",
          "ibo":"VoltaNiger","yor":"VoltaNiger","lin":"Bantu","lug":"Bantu","run":"Bantu",
          "sna":"Bantu","swa":"Bantu","xho":"Bantu","kin":"Bantu","tso":"Bantu","twi":"Kwa",
          "pcm":"EnglishCreole","eng":"Germanic","fra":"Romance","por":"Romance",
          "arq":"Semitic","ary":"Semitic"}
REGION = {"amh":"Horn","tir":"Horn","orm":"Horn","som":"Horn","hau":"West","ibo":"West",
          "yor":"West","pcm":"West","twi":"West","lin":"Central","lug":"East","run":"East",
          "swa":"East","kin":"East","sna":"Southern","xho":"Southern","tso":"Southern",
          "eng":"Pan","fra":"PanFR","por":"PanPT","arq":"NorthAfr","ary":"NorthAfr"}
# European colonial language legacy (Ethiopia/Eritrea Horn = largely non-colonised, own tag)
COLON  = {"amh":"Horn","tir":"Horn","orm":"Horn","som":"Horn","hau":"Anglo","ibo":"Anglo",
          "yor":"Anglo","pcm":"Anglo","lug":"Anglo","swa":"Anglo","sna":"Anglo","xho":"Anglo",
          "twi":"Anglo","tso":"Anglo","kin":"Franco","lin":"Franco","run":"Franco","fra":"Franco",
          "eng":"Anglo","por":"Luso","arq":"Franco","ary":"Franco"}
NONLATIN = {"amh","tir"}                      # Ge'ez script
LANGNAME = {"amh":"Amharic","tir":"Tigrinya","orm":"Oromo","som":"Somali","hau":"Hausa",
            "ibo":"Igbo","yor":"Yoruba","lin":"Lingala","lug":"Luganda","run":"Kirundi",
            "sna":"Shona","swa":"Swahili","xho":"Xhosa","pcm":"Naija Pidgin","eng":"English",
            "fra":"French","kin":"Kinyarwanda","tso":"Tsonga","twi":"Twi","por":"Portuguese",
            "arq":"Alg. Arabic","ary":"Mor. Arabic"}
EUROBASE = {"eng","fra"}                       # within-corpus European-language-news control

def vec(ch): return np.array([ch[a] for a in DWEB], float)
def load(p):
    out=[]
    if not os.path.exists(p): return out
    for l in open(p, encoding="utf-8"):
        try: r=json.loads(l)
        except Exception: continue
        if isinstance(r.get("char"),dict) and all(a in r["char"] for a in DWEB):
            out.append(r)
    return out
def input_counts(p):
    c=collections.Counter()
    if not os.path.exists(p): return c
    for l in open(p, encoding="utf-8"):
        try: c[json.loads(l)["kind"]]+=1
        except Exception: pass
    return c

def cohend(a,b):
    a,b=np.asarray(a,float),np.asarray(b,float)
    na,nb=len(a),len(b)
    sp=np.sqrt(((na-1)*a.var(ddof=1)+(nb-1)*b.var(ddof=1))/(na+nb-2)+1e-12)
    return (a.mean()-b.mean())/sp

def ward(Ms,labels):
    from scipy.cluster.hierarchy import linkage, dendrogram
    Z=linkage(Ms,method="ward"); dn=dendrogram(Z,labels=labels,no_plot=True); return dn["ivl"]

def analyse(scored_path, input_path, panel):
    rows=load(scored_path)
    inc=input_counts(input_path)
    by=collections.defaultdict(list)
    for r in rows: by[r["kind"]].append(r["char"])
    langs=sorted(by)
    print("="*100)
    print(f"PANEL {panel}  --  {scored_path.split('/')[-1]}  ({len(rows)} scored rows, {len(langs)} languages)")
    print("="*100)

    # ---- language x axis matrix + caveat metrics ----
    print(f"\n[{panel}] LANGUAGE x AXIS matrix (mean per axis) + coverage + degeneracy")
    hdr = f"{'lang':13s} {'n':>4s} {'cov%':>5s} " + " ".join(f"{a[:4]:>5s}" for a in DWEB) + f" {'meanVar':>7s}"
    print(hdr); print("-"*len(hdr))
    means={}; varflag={}
    for lg in langs:
        V=np.array([vec(c) for c in by[lg]])
        m=V.mean(0); means[lg]=m
        att=inc.get(lg,0); cov=100.0*len(by[lg])/att if att else float("nan")
        mv=float(V.var(0).mean()); varflag[lg]=mv
        flag = ""
        if lg in NONLATIN: flag+=" [Ge'ez]"
        if mv < 0.010: flag+=" [LOW-VAR]"
        print(f"{LANGNAME.get(lg,lg):13s} {len(by[lg]):4d} {cov:5.1f} " +
              " ".join(f"{x:5.2f}" for x in m) + f" {mv:7.4f}{flag}")

    # ---- matter/manner summary per language ----
    def mm(m):
        mat=np.mean([m[DWEB.index(a)] for a in MATTER]); man=np.mean([m[DWEB.index(a)] for a in MANNER])
        return mat, man, m[DWEB.index("affect")]-mat
    print(f"\n[{panel}] matter / manner / affect-gap per language (sorted by manner-minus-matter)")
    order=sorted(langs, key=lambda lg:(mm(means[lg])[1]-mm(means[lg])[0]))
    print(f"{'lang':13s} {'matter':>7s} {'manner':>7s} {'man-mat':>8s} {'affgap':>7s}  fam/region/colon")
    for lg in order:
        mat,man,ag=mm(means[lg])
        print(f"{LANGNAME.get(lg,lg):13s} {mat:7.3f} {man:7.3f} {man-mat:+8.3f} {ag:+7.3f}"
              f"  {FAMILY.get(lg,'?')}/{REGION.get(lg,'?')}/{COLON.get(lg,'?')}")

    # ---- (1) PC1 matter/manner structure ----
    print(f"\n[{panel}] (1) PC1 STRUCTURE  (pooled reference PC1 + per-language cosine to it)")
    A=np.array([vec(c) for lg in langs for c in by[lg]])
    mu=A.mean(0); sd=A.std(0)+1e-9
    As=(A-mu)/sd
    U,S,Vt=np.linalg.svd(As-As.mean(0), full_matrices=False)
    pc1=Vt[0]; ev=(S**2)/np.sum(S**2)
    # sign so matter loads positive
    if pc1[DWEB.index("rigour")]<0: pc1=-pc1
    print(f"  pooled PC1 explains {ev[0]*100:.1f}% (PC2 {ev[1]*100:.1f}%). Loadings:")
    for a,w in zip(DWEB,pc1): print(f"    {a:16s} {w:+.3f}")
    matter_axes=[DWEB.index(a) for a in MATTER]; manner_axes=[DWEB.index(a) for a in MANNER]
    is_mm = (np.mean([pc1[i] for i in matter_axes])>0) and (np.mean([pc1[i] for i in manner_axes])<0)
    print(f"  matter loads {'+' if np.mean([pc1[i] for i in matter_axes])>0 else '-'}, "
          f"manner loads {'+' if np.mean([pc1[i] for i in manner_axes])>0 else '-'}  "
          f"=> pooled PC1 {'IS' if is_mm else 'is NOT'} matter-vs-manner")
    # a-priori matter/manner contrast
    con=np.zeros(8)
    for a in MATTER: con[DWEB.index(a)]=+1
    for a in MANNER: con[DWEB.index(a)]=-1
    con/=np.linalg.norm(con)
    print(f"  cos(pooled PC1, a-priori matter-minus-manner contrast) = {abs(float(pc1@con)):.3f}")
    print(f"\n  per-language PC1 (standardised WITHIN language) cosine to pooled reference PC1:")
    print(f"  {'lang':13s} {'n':>4s} {'PC1%var':>7s} {'|cos(PC1,ref)|':>14s} {'|cos(PC1,contrast)|':>19s}")
    holds=0; tested=0
    for lg in langs:
        V=np.array([vec(c) for c in by[lg]])
        if len(V)<30:
            print(f"  {LANGNAME.get(lg,lg):13s} {len(V):4d}   too few"); continue
        Vs=(V-V.mean(0))/(V.std(0)+1e-9)
        u,s,vt=np.linalg.svd(Vs-Vs.mean(0), full_matrices=False)
        p=vt[0]
        if p[DWEB.index("rigour")]<0: p=-p
        cref=abs(float(p@pc1)); ccon=abs(float(p@con)); pv=(s[0]**2)/np.sum(s**2)
        tested+=1; holds+= int(cref>=0.80)
        print(f"  {LANGNAME.get(lg,lg):13s} {len(V):4d} {pv*100:7.1f} {cref:14.3f} {ccon:19.3f}")
    print(f"  => per-language PC1 aligns with pooled matter/manner axis (|cos|>=0.80) in {holds}/{tested} languages")

    # ---- (2) clustering ----
    print(f"\n[{panel}] (2) WHERE THEY SIT  (language mean vectors, standardised across languages)")
    ls=[lg for lg in langs if len(by[lg])>=30]
    if len(ls)<3:
        print(f"  too few languages with n>=30 ({len(ls)}) for clustering; skipping.");
        return means, {lg:mm(means[lg]) for lg in langs}, by
    M=np.array([means[lg] for lg in ls]); Ms=(M-M.mean(0))/(M.std(0)+1e-9)
    from scipy.spatial.distance import pdist, squareform
    Dm=squareform(pdist(Ms))
    def nn(lg,k=3):
        i=ls.index(lg); return [ls[j] for j in np.argsort(Dm[i]) if j!=i][:k]
    print("  nearest neighbours (character space):")
    for lg in ls:
        print(f"    {LANGNAME.get(lg,lg):13s} -> {', '.join(LANGNAME.get(x,x) for x in nn(lg))}")
    try:
        leaf=ward(Ms,[LANGNAME.get(x,x) for x in ls])
        print("  ward leaf order: " + " | ".join(leaf))
    except Exception as e:
        print(f"  (ward skipped: {e})")
    # MDS 2D
    B=-0.5*(Dm**2); J=np.eye(len(ls))-np.ones((len(ls),)*2)/len(ls); B=J@B@J
    w,Vv=np.linalg.eigh(B); idx=np.argsort(w)[::-1][:2]; xy=Vv[:,idx]*np.sqrt(np.abs(w[idx]))
    print("  2D MDS coords (lang x y  fam/region/colon):")
    for i,lg in enumerate(ls):
        print(f"    {LANGNAME.get(lg,lg):13s} {xy[i,0]:+.3f} {xy[i,1]:+.3f}   "
              f"{FAMILY.get(lg,'?')}/{REGION.get(lg,'?')}/{COLON.get(lg,'?')}")
    # within vs between for each grouping
    print("  do languages cluster by metadata? (mean within-group vs between-group distance, smaller within = clusters)")
    def within_between(tagmap):
        wi=[]; be=[]
        for i in range(len(ls)):
            for j in range(i+1,len(ls)):
                if tagmap.get(ls[i])==tagmap.get(ls[j]): wi.append(Dm[i,j])
                else: be.append(Dm[i,j])
        return (np.mean(wi) if wi else float('nan'), np.mean(be) if be else float('nan'), len(wi))
    for name,tm in [("FAMILY",FAMILY),("REGION",REGION),("COLONIAL-lang",COLON)]:
        wi,be,npair=within_between(tm)
        print(f"    {name:14s}: within {wi:.2f}  between {be:.2f}  ratio {wi/be:.2f}  (n_within_pairs {npair})")

    return means, {lg:mm(means[lg]) for lg in langs}, by

def main():
    means_n, mm_n, by_n = analyse(f"{D}/scored_news.jsonl", f"{D}/score_input_news.jsonl", "A/NEWS")
    # ---- (3) African vs European-language NEWS (within-corpus eng/fra) ----
    print("\n"+"="*100)
    print("(3) AFFECT / MANNER LEVEL: African languages vs European-language NEWS (eng+fra, same corpus/genre)")
    print("="*100)
    afr=[lg for lg in by_n if lg not in EUROBASE]
    def pool(langs, fn):
        return [fn(c) for lg in langs for c in by_n[lg]]
    def matter_c(c): return float(np.mean([c[a] for a in MATTER]))
    def manner_c(c): return float(np.mean([c[a] for a in MANNER]))
    def affect_c(c): return float(c["affect"])
    def affgap_c(c): return affect_c(c)-matter_c(c)
    for name,fn in [("matter",matter_c),("manner",manner_c),("affect",affect_c),("affect-gap",affgap_c)]:
        A=pool(afr,fn); E=pool([lg for lg in EUROBASE if lg in by_n],fn)
        if not E: print(f"  {name}: no eng/fra baseline scored yet"); continue
        d=cohend(A,E)
        print(f"  {name:11s}: African-14 mean {np.mean(A):.3f}  vs eng+fra {np.mean(E):.3f}  "
              f"delta {np.mean(A)-np.mean(E):+.3f}  Cohen d {d:+.2f}")
    print("  (eng here = African-outlet English news = scorer's high-resource CEILING reference)")

    # ---- tweet robustness panel ----
    if os.path.exists(f"{D}/scored_tweet.jsonl"):
        print("\n")
        analyse(f"{D}/scored_tweet.jsonl", f"{D}/score_input_tweet.jsonl", "B/TWEET")

if __name__=="__main__":
    main()
