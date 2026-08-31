#!/usr/bin/env python3
"""third_outcome_spread.py -- the persuasion funnel's missing THIRD outcome: SPREAD.

Paper 4B measures two funnel outcomes:
  ATTENTION  (does it get looked at)   -- Upworthy headline clicks, UK petition signatures
  CONVICTION (does it change a mind)   -- ChangeMyView deltas, StackExchange accepted answers
The third distinct outcome is SPREAD / virality: what travels, what gets amplified.

SPREAD data (already scored, DL580):
  reddit_wide   score (net upvotes) of a comment, cc_v3.reddit_wide, 80k with 8-axis char,
                400 subreddits, ~47k authors, thread ids (link_id).   PRIMARY spread corpus.
  reddit_char   an independent 18k reddit sample (cc_v3.reddit_char) with score + char.  REPLICATION.

Reddit score is the closest available spread proxy: a highly upvoted comment is surfaced to
more readers = it travels. NOTE (honest): the FiveThirtyEight IRA troll dump carries NO
per-post retweet/share count (its `retweet` column is a 0/1 is-a-retweet flag; followers/updates
are account-level), so it cannot supply a spread OUTCOME and is not used here.

PURE ANALYSIS on already-scored character. No new scoring, no :8301/:8288.

Method (mirrors funnel_by_medium.py):
  8 axes standardised within corpus; matter=mean(rigour,depth), manner=mean(affect,stance,register);
  PC1 = a single fixed matter/manner loading fit on the 80k reddit sample and reused everywhere.
  Spread is heavy-tailed and can be negative, so the outcome is the within-community FRACTIONAL
  RANK of score (robust, uniform); a signed-log score is reported as robustness.
  Predictors and outcome demeaned within a design group (subreddit / test / OP / question),
  cluster-robust SEs. For reddit, clustering is reported by BOTH author and subreddit.
  Every beta is standardised: outcome SD per predictor SD, comparable across corpora and stages.
"""
import os, json, math
import numpy as np
from collections import defaultdict
from scipy import stats
import psycopg2

AXES   = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
MATTER = ["rigour","depth"]
MANNER = ["affect","stance","register"]
NASC   = "/mnt/nas/kronaxis/corpora"
KCDW   = os.path.expanduser("~/kc-dwpaper")

def matter_of(ch): return float(np.mean([ch[a] for a in MATTER]))
def manner_of(ch): return float(np.mean([ch[a] for a in MANNER]))
def wc(t):         return len(t.split()) if isinstance(t,str) else 0

# ---------------------------------------------------------------- DB
def tfs_conn():
    url=None
    for l in open(os.path.expanduser("~/.kronaxis/env")):
        if l.startswith("TFS_DATABASE_URL="):
            url=l.split("=",1)[1].strip().strip('"').strip("'"); break
    # postgres://user:pw@host:port/db?sslmode=disable  -> swap db to tfs
    from urllib.parse import urlparse, unquote
    p=urlparse(url)
    return psycopg2.connect(host=p.hostname, port=p.port or 5432,
                            user=unquote(p.username), password=unquote(p.password), dbname="tfs")

# ---------------------------------------------------------------- loaders (spread)
def load_reddit(table, limit=None):
    """cc_v3.<table>: score = spread; group = subreddit; cluster by author & subreddit; thread=link_id."""
    has_author = (table=="reddit_wide")
    cols = "id, subreddit, score, char, "+("author, link_id, " if has_author else "NULL author, NULL link_id, ")+\
           "coalesce(array_length(regexp_split_to_array(btrim(body),'\\s+'),1),0) AS nw"
    q=f"SELECT {cols} FROM cc_v3.{table} WHERE char IS NOT NULL AND score IS NOT NULL"
    if limit: q+=f" LIMIT {limit}"
    rows=[]
    with tfs_conn() as c, c.cursor() as cur:
        cur.execute(q)
        for _id,sub,score,ch,author,link,nw in cur:
            if not isinstance(ch,dict) or not all(a in ch for a in AXES): continue
            if nw is None or nw<1: continue
            # skip deleted/removed stubs
            rows.append(dict(id=_id, group=sub or "?", subreddit=sub or "?",
                             author=author or _id, thread=link or _id,
                             score=float(score), wc=int(nw), ch=ch))
    return rows

# ---------------------------------------------------------------- loaders (attention / conviction) -- as funnel
def load_upworthy():
    sc={}
    for f in (f"{KCDW}/upworthy_scores_full.jsonl", f"{KCDW}/upworthy_scores.jsonl"):
        if os.path.exists(f):
            for line in open(f):
                try: r=json.loads(line); sc[r["headline"]]=r["scores"]
                except Exception: pass
    agg=defaultdict(lambda:[0.0,0.0])
    for line in open(f"{KCDW}/upworthy.jsonl"):
        try: r=json.loads(line)
        except Exception: continue
        h=r.get("headline")
        if h not in sc: continue
        a=agg[(r["test_id"],h)]; a[0]+=float(r.get("impressions",0)); a[1]+=float(r.get("clicks",0))
    rows=[]
    for (t,h),(imp,clk) in agg.items():
        if imp<=0: continue
        ch=sc[h]
        if not all(x in ch for x in AXES): continue
        rows.append(dict(group=t, y=clk/imp, wc=max(1,wc(h)), ch=ch,
                         author=t, thread=t, score=None))
    return rows

def load_paired(scores_path, utter_path):
    txt={}
    for l in open(utter_path):
        try: r=json.loads(l)
        except Exception: continue
        i=r.get("id"); t=r.get("text")
        if i is not None and isinstance(t,str): txt[i]=wc(t)
    rows=[]
    for l in open(scores_path):
        try: r=json.loads(l)
        except Exception: continue
        if r.get("kind")!="arg" or r.get("skip"): continue
        ch=r.get("char")
        if not isinstance(ch,dict) or not all(a in ch for a in AXES): continue
        n=txt.get(r.get("id"))
        if not n or n<1: continue
        root=r.get("root")
        if root is None: continue
        rows.append(dict(group=root, y=float(r.get("success",0)), wc=n, ch=ch,
                         author=root, thread=root, score=None))
    return rows

def load_petitions():
    txt={}
    for l in open(f"{NASC}/uk_petitions/petitions.jsonl"):
        try: r=json.loads(l)
        except Exception: continue
        i=r.get("id")
        if i is None: continue
        body=" ".join(str(r.get(k,"") or "") for k in ("action","background","additional_details"))
        txt[i]=wc(body)
    rows=[]
    for l in open(f"{NASC}/uk_petitions/cluster_members_scored.jsonl"):
        try: r=json.loads(l)
        except Exception: continue
        ch=r.get("char")
        if not isinstance(ch,dict) or not all(a in ch for a in AXES): continue
        if not r.get("opened_at"): continue
        sig=r.get("signature_count")
        if sig is None: continue
        n=txt.get(r.get("id"),0)
        if n<1: continue
        rows.append(dict(group=r.get("cluster_id"), y=math.log10(1.0+float(sig)),
                         wc=n, ch=ch, author=r.get("cluster_id"), thread=r.get("cluster_id"), score=None))
    return rows

# ---------------------------------------------------------------- stats
def zc(a):
    a=np.asarray(a,float); s=a.std()
    return (a-a.mean())/s if s>1e-12 else a-a.mean()

def demean_within(vals, groups):
    vals=np.asarray(vals,float); out=vals.copy()
    idx=defaultdict(list)
    for i,g in enumerate(groups): idx[g].append(i)
    for g,ix in idx.items():
        ix=np.array(ix); out[ix]=vals[ix]-vals[ix].mean()
    return out

def frac_rank_within(vals, groups):
    """fractional rank in [0,1] of vals within each group (robust heavy-tail outcome)."""
    vals=np.asarray(vals,float); out=np.zeros_like(vals)
    idx=defaultdict(list)
    for i,g in enumerate(groups): idx[g].append(i)
    for g,ix in idx.items():
        ix=np.array(ix); r=stats.rankdata(vals[ix],method="average")
        out[ix]= (r-0.5)/len(ix) if len(ix)>1 else 0.5
    return out

def cluster_robust(X, y, cl):
    XtXi=np.linalg.pinv(X.T@X); beta=XtXi@(X.T@y); u=y-X@beta
    K=X.shape[1]; N=X.shape[0]; meat=np.zeros((K,K))
    ug=np.unique(cl); G=len(ug)
    for g in ug:
        ix=np.where(cl==g)[0]; s=X[ix].T@u[ix]; meat+=np.outer(s,s)
    dof=(G/max(1,G-1))*((N-1)/max(1,N-K))
    V=dof*(XtXi@meat@XtXi); se=np.sqrt(np.clip(np.diag(V),0,None))
    t=beta/(se+1e-30); p=2*stats.t.sf(np.abs(t),df=max(1,G-1))
    return beta,se,t,p,G

def stars(p): return "***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else ""

# ---------------------------------------------------------------- fixed PC1 (matter/manner)
# canonical series reference: SVD on the web character space cc_v3.domain_char8_expanded
# (2.65M domains), NOT any outcome corpus, so PC1 is defined independently of spread/attention.
def fit_pc1_canonical(sample=400000):
    with tfs_conn() as c, c.cursor() as cur:
        cur.execute(f"SELECT {','.join(AXES)} FROM cc_v3.domain_char8_expanded "
                    f"WHERE rigour IS NOT NULL ORDER BY domain LIMIT {sample}")
        M=np.array(cur.fetchall(),float)
    mu=M.mean(0); sd=M.std(0); sd[sd<1e-12]=1
    Z=(M-mu)/sd
    U,S,Vt=np.linalg.svd(Z-Z.mean(0),full_matrices=False)
    load=Vt[0]
    mi=[AXES.index(a) for a in MATTER]; ni=[AXES.index(a) for a in MANNER]
    if load[mi].mean() < load[ni].mean(): load=-load
    return load, mu, sd

def pc1_score(rows, load):
    Z=np.column_stack([zc([r["ch"][a] for r in rows]) for a in AXES])
    return Z@load

# ---------------------------------------------------------------- per-corpus analysis
def analyse(name, rows, stage, outcome="y", demean_group="group", cluster="group",
            second_cluster=None):
    if len(rows)<40:
        print(f"[{name}] only {len(rows)} rows -- skip"); return None
    groups=np.array([r[demean_group] for r in rows])
    cl    =np.array([r[cluster] for r in rows])
    # outcome
    if outcome=="rank":
        yraw=frac_rank_within([r["score"] for r in rows], np.array([r["group"] for r in rows]))
    elif outcome=="signedlog":
        s=np.array([r["score"] for r in rows],float); yraw=np.sign(s)*np.log10(1.0+np.abs(s))
    else:
        yraw=np.array([r["y"] for r in rows],float)
    axz={a: zc([r["ch"][a] for r in rows]) for a in AXES}
    matter=zc([matter_of(r["ch"]) for r in rows])
    manner=zc([manner_of(r["ch"]) for r in rows])
    pc1   =zc([r["pc1"] for r in rows])
    logwc =np.log10(np.array([r["wc"] for r in rows],float))

    # within-group demean of y, axes, length
    yD=demean_within(yraw,groups)
    L =zc(demean_within(logwc,groups))
    Y =zc(yD)
    A ={a: zc(demean_within(axz[a],groups)) for a in AXES}
    Mt=zc(demean_within(matter,groups)); Mn=zc(demean_within(manner,groups)); P1=zc(demean_within(pc1,groups))

    # 8-axis model
    X8=np.column_stack([A[a] for a in AXES]+[L])
    b8,s8,t8,p8,G=cluster_robust(X8,Y,cl)
    axis_beta={AXES[i]:(b8[i],p8[i]) for i in range(len(AXES))}
    len_beta=(b8[8],p8[8])
    # second clustering for the 8-axis model (reddit: subreddit as well as author)
    axis_p2=None
    if second_cluster is not None:
        cl2=np.array([r[second_cluster] for r in rows])
        _,_,_,p8b,G2=cluster_robust(X8,Y,cl2)
        axis_p2={AXES[i]:p8b[i] for i in range(len(AXES))}

    # matter/manner/PC1 headline model
    Xh=np.column_stack([Mt,Mn,L])
    bh,sh,th,ph,_=cluster_robust(Xh,Y,cl)
    Xp=np.column_stack([P1,L])
    bp,sp,tp,pp,_=cluster_robust(Xp,Y,cl)

    n=len(rows); wcv=np.array([r["wc"] for r in rows],float)
    print(f"\n{'='*90}\n{name}  [{stage}]  n={n:,}  demean={demean_group}({len(set(groups))})  "
          f"cluster={cluster}({G:,})  medWC={np.median(wcv):.0f}")
    print("  per-axis beta (outcome SD / axis SD), within-group, cluster-robust:")
    for a in AXES:
        b,p=axis_beta[a]; extra=f"  [p_{second_cluster}={stars(axis_p2[a]) or f'{axis_p2[a]:.2f}'}]" if axis_p2 else ""
        print(f"     {a:18s} {b:+.3f} {stars(p):3s}{extra}")
    print(f"     {'log_wc':18s} {len_beta[0]:+.3f} {stars(len_beta[1])}")
    print(f"  matter {bh[0]:+.3f}{stars(ph[0])}  manner {bh[1]:+.3f}{stars(ph[1])}  "
          f"PC1(matter/manner) {bp[0]:+.3f}{stars(pp[0])}")
    return dict(name=name, stage=stage, n=n, G=int(G), medwc=float(np.median(wcv)),
                axis=axis_beta, axis_p2=axis_p2, length=len_beta,
                matter=(float(bh[0]),float(ph[0])), manner=(float(bh[1]),float(ph[1])),
                pc1=(float(bp[0]),float(pp[0])), cluster=cluster, second_cluster=second_cluster)

# ---------------------------------------------------------------- main
def main():
    print("third_outcome_spread -- character of SPREAD vs attention vs conviction")
    print("betas standardised (outcome SD / predictor SD); within-group demeaned; cluster-robust SE\n")

    # canonical PC1 from the web character space (independent of every outcome corpus)
    load,_,_=fit_pc1_canonical()
    print("[canonical PC1 loading fit on cc_v3.domain_char8_expanded, oriented matter-positive]:")
    for a,l in zip(AXES,load): print(f"     {a:18s} {l:+.3f}")
    # PRIMARY spread corpus
    rw=load_reddit("reddit_wide")
    print(f"[load] reddit_wide spread rows: {len(rw):,}")
    # attach pc1 to every corpus using the SAME loading
    def attach_pc1(rows):
        p=pc1_score(rows,load)
        for r,v in zip(rows,p): r["pc1"]=float(v)
    attach_pc1(rw)

    rc=load_reddit("reddit_char"); attach_pc1(rc)
    up=load_upworthy(); attach_pc1(up)
    pe=load_petitions(); attach_pc1(pe)
    cmv=load_paired(f"{NASC}/cmv_winning_args/cmv_scores.jsonl",
                    f"{NASC}/cmv_winning_args/winning-args-corpus/utterances.jsonl"); attach_pc1(cmv)
    se=load_paired(f"{NASC}/stackexchange_args/se_scores.jsonl",
                   f"{NASC}/stackexchange_args/combined/winning-args-corpus/utterances.jsonl"); attach_pc1(se)

    res=[]
    # SPREAD  (rank primary; demean within subreddit; cluster by author, 2nd by subreddit)
    res.append(analyse("reddit_wide", rw, "spread", outcome="rank",
                       demean_group="group", cluster="author", second_cluster="group"))
    res.append(analyse("reddit_char", rc, "spread", outcome="rank",
                       demean_group="group", cluster="group"))
    # SPREAD robustness: signed-log outcome + within-thread demean
    res.append(analyse("reddit_wide_signedlog", rw, "spread(log)", outcome="signedlog",
                       demean_group="group", cluster="author", second_cluster="group"))
    res.append(analyse("reddit_wide_within_thread", [r for r in rw], "spread(thread)", outcome="rank",
                       demean_group="thread", cluster="author"))
    # ATTENTION
    res.append(analyse("upworthy", up, "attention", outcome="y", demean_group="group", cluster="group"))
    res.append(analyse("petitions", pe, "attention", outcome="y", demean_group="group", cluster="group"))
    # CONVICTION
    res.append(analyse("cmv", cmv, "conviction", outcome="y", demean_group="group", cluster="group"))
    res.append(analyse("se",  se,  "conviction", outcome="y", demean_group="group", cluster="group"))

    res=[r for r in res if r]
    # ---- contrast table: per-axis beta by stage (headline corpora)
    print(f"\n\n{'#'*90}\nCONTRAST -- per-axis standardised beta by funnel stage\n{'#'*90}")
    headline={"reddit_wide":"SPREAD","upworthy":"ATTN","petitions":"ATTN","cmv":"CONV","se":"CONV"}
    order=["reddit_wide","upworthy","petitions","cmv","se"]
    byname={r["name"]:r for r in res}
    print(f"  {'axis':18s}"+"".join(f"{headline[n]+':'+n.split('_')[0]:>16s}" for n in order))
    for a in AXES+["__matter","__manner","__pc1"]:
        row=f"  {a:18s}"
        for n in order:
            r=byname[n]
            if a=="__matter": b,p=r["matter"]
            elif a=="__manner": b,p=r["manner"]
            elif a=="__pc1": b,p=r["pc1"]
            else: b,p=r["axis"][a]
            row+=f"{b:+9.3f}{stars(p):3s}    "[:16]
        print(row)

    import pickle
    with open(os.path.expanduser("~/third_outcome_spread_res.pkl"),"wb") as f: pickle.dump(res,f)
    with open(os.path.expanduser("~/third_outcome_spread_res.json"),"w") as f:
        json.dump({"pc1_loading":dict(zip(AXES,[float(x) for x in load])),"res":res}, f, indent=1)
    print("\n[done] pickled to ~/third_outcome_spread_res.pkl and .json")

if __name__=="__main__":
    main()
