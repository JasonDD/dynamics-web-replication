#!/usr/bin/env python3
"""Cross platform re-identification test (DYNAMICS-WEB, PUBLIC track).

Question: given two pieces of writing from two DIFFERENT platforms, can we decide
whether they are the same pseudonymous person, from the writing alone?

Ground truth: the internal cross site corpus. A cross site identity key (type withheld as commercial IP) that appears on 2+ distinct domains is the SAME person seen on 2+ platforms.
The table already carries the 8 axis DYNAMICS-WEB character vector (char_dweb, 7B scorer).

Signals compared:
  1. CHARACTER  : person aggregated 8 axis character vector similarity.
  2. STYLOMETRY : classic authorship features from the raw text (function words, punctuation,
                  sentence length, character trigrams, type token ratio, word length).
  3. COMBINED   : logistic fusion, plus the decomposition (what character adds over
                  stylometry and the reverse).

Everything is read only. Runs on the internal host against the local tfs DB. No scoring calls.
"""
import os, sys, json, math, random, re, time
from collections import Counter, defaultdict
import numpy as np
import psycopg2

RNG = random.Random(20260831)
np.random.seed(20260831)

MIN_UNIT_CHARS = 200        # min pooled text for a (ident, domain) unit to be usable
MAX_UNIT_CHARS = 8000       # cap pooled text per unit (stability + speed)
MAX_ROWS_PER_UNIT = 60
MAX_POS_PAIRS_PER_IDENT = 3 # cap positive pairs contributed by one person
N_TRIGRAMS = 300            # top character trigrams kept as features
NBOOT = 1000

CHAR_AXES = ["depth","affect","rigour","stance","candour","register","originality","commercial_drive"]

# A fixed English function word list (closed class + high frequency grammatical words).
FUNCTION_WORDS = """a about above after again against all am an and any are aren't as at be because
been before being below between both but by can can't cannot could couldn't did didn't do does
doesn't doing don't down during each few for from further had hadn't has hasn't have haven't having
he he'd he'll he's her here here's hers herself him himself his how how's i i'd i'll i'm i've if in
into is isn't it it's its itself let's me more most mustn't my myself no nor not of off on once only
or other ought our ours ourselves out over own same shan't she she'd she'll she's should shouldn't so
some such than that that's the their theirs them themselves then there there's these they they'd
they'll they're they've this those through to too under until up upon very was wasn't we we'd we'll
we're we've were weren't what what's when when's where where's which while who who's whom why why's
with won't would wouldn't you you'd you'll you're you've your yours yourself yourselves""".split()

PUNCT = list(".,;:!?'\"()[]{}-—…/\\&%$#@*+=~`")

def db():
    envp = os.path.expanduser("~/.kronaxis/env")
    pw = None
    for l in open(envp):
        if l.startswith("TFS_DB_PASSWORD="):
            pw = l.split("=",1)[1].strip().strip('"').strip("'"); break
    return psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={pw} dbname=tfs")

# ---------------------------------------------------------------- data load
def load_units():
    """Return dict: (key_type, ident, domain) -> {'char': meanvec8, 'text': pooled, 'nrows': k}."""
    con = db(); cur = con.cursor("csa_stream"); cur.itersize = 20000
    cur.execute("""
        SELECT key_type, ident, domain, char_dweb, left(body, 4000)
        FROM the internal cross site corpus
        WHERE char_dweb IS NOT NULL AND body IS NOT NULL AND length(body) > 100
    """)
    raw = defaultdict(lambda: {"chars": [], "bodies": []})
    n = 0
    for key_type, ident, domain, cd, body in cur:
        if not ident or not domain: continue
        try:
            vec = [float(cd.get(a, 0.5)) for a in CHAR_AXES]
        except Exception:
            continue
        u = raw[(key_type, ident, domain)]
        u["chars"].append(vec)
        u["bodies"].append(body)
        n += 1
    cur.close(); con.close()
    units = {}
    for k, v in raw.items():
        char = np.mean(np.array(v["chars"], dtype=float), axis=0)
        bodies = sorted(v["bodies"], key=len, reverse=True)[:MAX_ROWS_PER_UNIT]
        text = "\n".join(bodies)[:MAX_UNIT_CHARS]
        if len(text) < MIN_UNIT_CHARS: continue
        units[k] = {"char": char, "text": text, "nrows": len(v["bodies"])}
    return units, n

# ---------------------------------------------------------------- stylometry
_word_re = re.compile(r"[a-z']+")
_sent_re = re.compile(r"[.!?]+")

def style_raw(text):
    low = text.lower()
    words = _word_re.findall(low)
    nw = max(len(words), 1)
    feats = {}
    fwc = Counter(w for w in words if w in FW_SET)
    for w in FUNCTION_WORDS:
        feats["fw_"+w] = fwc.get(w, 0) / nw
    nchar = max(len(text), 1)
    pc = Counter(text)
    for p in PUNCT:
        feats["pu_"+p] = pc.get(p, 0) / nchar
    # sentence length distribution
    sents = [s for s in _sent_re.split(text) if s.strip()]
    slen = [len(_word_re.findall(s.lower())) for s in sents] or [nw]
    feats["sent_mean"] = float(np.mean(slen))
    feats["sent_std"] = float(np.std(slen))
    feats["n_sents_per_word"] = len(sents) / nw
    # lexical
    feats["ttr"] = len(set(words)) / nw
    feats["word_len_mean"] = float(np.mean([len(w) for w in words])) if words else 0.0
    feats["upper_ratio"] = sum(1 for c in text if c.isupper()) / nchar
    feats["digit_ratio"] = sum(1 for c in text if c.isdigit()) / nchar
    return feats, low

FW_SET = set(FUNCTION_WORDS)

def build_style_matrix(units, keys):
    # first pass: raw feats + trigram corpus counts
    raw_feats = {}
    tri_counter = Counter()
    lows = {}
    for k in keys:
        f, low = style_raw(units[k]["text"])
        raw_feats[k] = f
        lows[k] = low
    for k in keys:
        low = lows[k]
        for i in range(len(low)-2):
            tg = low[i:i+3]
            tri_counter[tg] += 1
    top_tri = [t for t,_ in tri_counter.most_common(N_TRIGRAMS)]
    tri_idx = {t:i for i,t in enumerate(top_tri)}
    # second pass: assemble full vector (scalar feats + trigram rel freq)
    scalar_names = list(raw_feats[keys[0]].keys())
    m_scalar = np.array([[raw_feats[k][n] for n in scalar_names] for k in keys], dtype=float)
    m_tri = np.zeros((len(keys), len(top_tri)), dtype=float)
    for r, k in enumerate(keys):
        low = lows[k]
        cnt = Counter()
        for i in range(len(low)-2):
            tg = low[i:i+3]
            if tg in tri_idx: cnt[tg]+=1
        tot = max(len(low)-2, 1)
        for tg, c in cnt.items():
            m_tri[r, tri_idx[tg]] = c/tot
    X = np.hstack([m_scalar, m_tri])
    # z score per feature across the unit population (authorship standard)
    mu = X.mean(axis=0); sd = X.std(axis=0); sd[sd==0] = 1.0
    Z = (X - mu) / sd
    names = scalar_names + ["tri_"+t for t in top_tri]
    return Z, names

# ---------------------------------------------------------------- pairs
def make_pairs(units):
    by_ident = defaultdict(list)          # (key_type,ident) -> list of unit keys (distinct domains)
    for k in units:
        by_ident[(k[0], k[1])].append(k)
    pos = []
    qualifying = []
    for pid, klist in by_ident.items():
        # keep only distinct domains; prefer text richest per domain
        best_by_dom = {}
        for k in klist:
            dom = k[2]
            if dom not in best_by_dom or len(units[k]["text"]) > len(units[best_by_dom[dom]]["text"]):
                best_by_dom[dom] = k
        ks = list(best_by_dom.values())
        if len(ks) < 2: continue
        qualifying.append(pid)
        ks.sort(key=lambda k: len(units[k]["text"]), reverse=True)
        # up to MAX_POS_PAIRS_PER_IDENT cross domain pairs
        pairs = []
        for i in range(len(ks)):
            for j in range(i+1, len(ks)):
                pairs.append((ks[i], ks[j]))
        RNG.shuffle(pairs)
        for p in pairs[:MAX_POS_PAIRS_PER_IDENT]:
            pos.append(p)
    # negatives: random unit pairs from different idents, equal count
    all_keys = list(units.keys())
    neg = []
    tries = 0
    npos = len(pos)
    seen = set()
    while len(neg) < npos and tries < npos*20:
        tries += 1
        a = RNG.choice(all_keys)
        b = RNG.choice(all_keys)
        if (a[0],a[1]) == (b[0],b[1]): continue
        if a[2] == b[2]:  # keep it a genuine cross platform comparison
            continue
        key = (a,b) if a<b else (b,a)
        if key in seen: continue
        seen.add(key)
        neg.append((a,b))
    return pos, neg, qualifying

# ---------------------------------------------------------------- metrics
def auc(scores, labels):
    """Mann Whitney U AUC. scores higher => more likely positive (label 1)."""
    scores = np.asarray(scores, float); labels = np.asarray(labels, int)
    order = np.argsort(scores, kind="mergesort")
    ranks = np.empty(len(scores), float)
    sc = scores[order]
    i = 0
    while i < len(sc):
        j = i
        while j+1 < len(sc) and sc[j+1]==sc[i]: j+=1
        r = (i+j)/2.0 + 1.0
        ranks[order[i:j+1]] = r
        i = j+1
    npos = labels.sum(); nneg = len(labels)-npos
    if npos==0 or nneg==0: return float("nan")
    sumpos = ranks[labels==1].sum()
    return (sumpos - npos*(npos+1)/2.0) / (npos*nneg)

def boot_auc_ci(scores, labels, nboot=NBOOT):
    scores = np.asarray(scores,float); labels=np.asarray(labels,int)
    n=len(scores); vals=[]
    idx_all=np.arange(n)
    for _ in range(nboot):
        bi=np.random.randint(0,n,n)
        vals.append(auc(scores[bi], labels[bi]))
    vals=np.array(vals)
    return float(np.percentile(vals,2.5)), float(np.percentile(vals,97.5))

def logistic_cv(Xfeat, y, folds=5):
    """Numpy L2 logistic regression, out of fold predicted probs. Returns oof scores."""
    y=np.asarray(y,float); n=len(y)
    Xs=np.asarray(Xfeat,float)
    mu=Xs.mean(0); sd=Xs.std(0); sd[sd==0]=1.0
    Xz=(Xs-mu)/sd
    Xz=np.hstack([Xz, np.ones((n,1))])
    idx=np.arange(n); np.random.shuffle(idx)
    oof=np.zeros(n)
    fsz=n//folds
    for f in range(folds):
        te = idx[f*fsz : (f+1)*fsz] if f<folds-1 else idx[f*fsz:]
        tr = np.setdiff1d(idx, te)
        w=np.zeros(Xz.shape[1]); lam=1.0; lr=0.5
        Xtr=Xz[tr]; ytr=y[tr]
        for it in range(400):
            p=1/(1+np.exp(-Xtr@w))
            g=Xtr.T@(p-ytr)/len(tr) + lam*np.r_[w[:-1],0]/len(tr)
            w-=lr*g
        oof[te]=1/(1+np.exp(-Xz[te]@w))
    return oof

# ---------------------------------------------------------------- main
def main():
    t0=time.time()
    print("[load] streaming rows ...", flush=True)
    units, nrows = load_units()
    print(f"[load] {nrows} scored rows -> {len(units)} (ident,domain) units in {time.time()-t0:.0f}s", flush=True)

    pos, neg, qualifying = make_pairs(units)
    print(f"[pairs] qualifying idents(>=2 domains): {len(qualifying)}  pos={len(pos)} neg={len(neg)}", flush=True)

    pair_keys = pos + neg
    labels = np.array([1]*len(pos) + [0]*len(neg))

    # unique units used -> style matrix
    used = sorted({k for pr in pair_keys for k in pr})
    print(f"[style] building stylometry over {len(used)} units ...", flush=True)
    Z, names = build_style_matrix(units, used)
    uidx = {k:i for i,k in enumerate(used)}
    print(f"[style] {Z.shape[1]} features", flush=True)

    # per pair scores
    char_cos=[]; char_negeuc=[]; sty_negdelta=[]; sty_cos=[]
    for a,b in pair_keys:
        ca=units[a]["char"]; cb=units[b]["char"]
        char_negeuc.append(-float(np.linalg.norm(ca-cb)))
        denom=(np.linalg.norm(ca)*np.linalg.norm(cb)) or 1.0
        char_cos.append(float(ca@cb/denom))
        za=Z[uidx[a]]; zb=Z[uidx[b]]
        sty_negdelta.append(-float(np.mean(np.abs(za-zb))))     # negative Burrows Delta
        d=(np.linalg.norm(za)*np.linalg.norm(zb)) or 1.0
        sty_cos.append(float(za@zb/d))
    char_cos=np.array(char_cos); char_negeuc=np.array(char_negeuc)
    sty_negdelta=np.array(sty_negdelta); sty_cos=np.array(sty_cos)

    res={}
    def rec(name, sc):
        a=auc(sc,labels); lo,hi=boot_auc_ci(sc,labels)
        res[name]={"auc":a,"ci":[lo,hi]}
        print(f"  {name:22s} AUC={a:.4f}  95% CI [{lo:.4f},{hi:.4f}]", flush=True)
        return a

    print("[auc] character:")
    a_cchar_e=rec("char_neg_euclid", char_negeuc)
    a_cchar_c=rec("char_cosine", char_cos)
    print("[auc] stylometry:")
    a_sty_d=rec("stylo_neg_delta", sty_negdelta)
    a_sty_c=rec("stylo_cosine", sty_cos)

    char_primary = char_negeuc if a_cchar_e>=a_cchar_c else char_cos
    char_primary_name = "char_neg_euclid" if a_cchar_e>=a_cchar_c else "char_cosine"
    sty_primary = sty_negdelta if a_sty_d>=a_sty_c else sty_cos
    sty_primary_name = "stylo_neg_delta" if a_sty_d>=a_sty_c else "stylo_cosine"

    # combined logistic fusion (out of fold)
    print("[auc] combined (logistic fusion, 5 fold oof):")
    Xc=np.column_stack([char_primary, sty_primary])
    oof=logistic_cv(Xc, labels)
    a_comb=rec("combined_char+stylo", oof)

    # decomposition: incremental value
    # char alone vs stylo alone vs combined already have AUCs.
    corr=float(np.corrcoef(char_primary, sty_primary)[0,1])
    inc_char = a_comb - max(a_sty_d,a_sty_c)   # what character adds over best stylometry
    inc_sty  = a_comb - max(a_cchar_e,a_cchar_c) # what stylometry adds over best character

    # precision at high specificity thresholds on the balanced set
    def prec_at_spec(sc, spec):
        neg_sc=sc[labels==0]; thr=np.quantile(neg_sc, spec)
        pred=sc>=thr
        tp=int(((pred)&(labels==1)).sum()); fp=int(((pred)&(labels==0)).sum())
        rec_=tp/max((labels==1).sum(),1)
        prec=tp/max(tp+fp,1)
        fpr=fp/max((labels==0).sum(),1)
        tpr=rec_
        return {"threshold":float(thr),"precision":float(prec),"recall":float(rec_),
                "tpr":float(tpr),"fpr":float(fpr)}
    prec95=prec_at_spec(oof,0.95)
    prec99=prec_at_spec(oof,0.99)
    prec999=prec_at_spec(oof,0.999)

    # base rate adjusted precision (real world false link risk)
    def prec_baserate(tpr,fpr,p):
        return (tpr*p)/(tpr*p + fpr*(1-p)) if (tpr*p+fpr*(1-p))>0 else 0.0
    base={}
    for tag,pt in [("spec99",prec99),("spec999",prec999)]:
        base[tag]={f"p={p:g}":prec_baserate(pt["tpr"],pt["fpr"],p) for p in [1e-2,1e-3,1e-4,1e-5]}

    out={
        "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runtime_s": round(time.time()-t0,1),
        "data":{"scored_rows":nrows,"units":len(units),"qualifying_idents":len(qualifying),
                "pos_pairs":len(pos),"neg_pairs":len(neg),"style_features":int(Z.shape[1])},
        "auc":res,
        "primary":{"char":char_primary_name,"stylo":sty_primary_name,
                   "char_auc":max(a_cchar_e,a_cchar_c),"stylo_auc":max(a_sty_d,a_sty_c),
                   "combined_auc":a_comb},
        "decomposition":{"corr_char_stylo":corr,
                         "combined_minus_stylo":inc_char,
                         "combined_minus_char":inc_sty},
        "precision":{"spec95":prec95,"spec99":prec99,"spec999":prec999},
        "base_rate_precision":base,
    }
    outp=os.environ.get("OUT","/home/jason/projects/kronaxis/docs/papers/dynamics_web_series/results/crossplatform_identity/stats.json")
    # if run on the internal host, write to a stable local path too
    try:
        json.dump(out, open(outp,"w"), indent=2)
    except Exception:
        outp="/tmp/crossplatform_identity_stats.json"
        json.dump(out, open(outp,"w"), indent=2)
    print("\n=== SUMMARY ===")
    print(json.dumps(out, indent=2))
    print(f"[done] stats -> {outp}")

if __name__=="__main__":
    main()
