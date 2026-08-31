#!/usr/bin/env python3
"""stylometry.py — classic Federalist authorship stylometry, blind to the Gutenberg byline.

Two independent classic methods on function-word frequencies:
  (A) Burrows's Delta   — the standard stylometric distance, nearest-author over z-scored MFW.
  (B) Multinomial Naive Bayes on function-word counts (Mosteller & Wallace family) + LOO CV.
Also logistic regression with LOO CV as a third check.

Train set: known Hamilton (51) vs known Madison (14). Apply to the 12 disputed.
Consensus to match: all 12 disputed are MADISON.
"""
import json, os, re, math
import numpy as np
from collections import Counter
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import LeaveOneOut

HERE = os.path.dirname(os.path.abspath(__file__))
PAPERS = os.path.join(HERE, "..", "papers.jsonl")

# Classic function words / high-frequency non-contextual markers.
# Includes the celebrated Hamilton/Madison discriminators (upon, whilst, while, on, there, ...).
FUNC_WORDS = """a all also an and any are as at be been but by can do down even every
for from had has have her his if in into is it its may more must my no not now
of on one only or our shall should so some such than that the their then there
things this to up upon was were what when which who will with would your
while whilst though although both because between during each here how many much
nor off out over own same too under until very well what whatever whenever whether
against about above after among around before behind below beneath beside besides
beyond concerning considering despite except inside near since throughout toward
towards underneath unlike within without""".split()
FUNC_WORDS = sorted(set(FUNC_WORDS))

WORD_RE = re.compile(r"[a-z]+")

def tokens(text):
    return WORD_RE.findall(text.lower())

def load():
    recs = [json.loads(l) for l in open(PAPERS)]
    return recs

def feat_counts(text):
    toks = tokens(text)
    c = Counter(toks)
    n = len(toks)
    counts = np.array([c.get(w,0) for w in FUNC_WORDS], float)
    rel = counts / n if n else counts
    return counts, rel, n

def main():
    recs = load()
    for r in recs:
        cnt, rel, n = feat_counts(r["text"])
        r["_cnt"], r["_rel"], r["_ntok"] = cnt, rel, n

    ham = [r for r in recs if r["label"]=="HAMILTON"]
    mad = [r for r in recs if r["label"]=="MADISON"]
    disp= [r for r in recs if r["label"]=="DISPUTED"]
    joint=[r for r in recs if r["label"]=="JOINT_HM"]
    print(f"train: Hamilton {len(ham)}  Madison {len(mad)}   disputed {len(disp)}  joint {len(joint)}")
    print(f"mean tokens/paper: H={np.mean([r['_ntok'] for r in ham]):.0f}  M={np.mean([r['_ntok'] for r in mad]):.0f}  D={np.mean([r['_ntok'] for r in disp]):.0f}")

    train = ham + mad
    ytr = np.array([0]*len(ham) + [1]*len(mad))   # 0=Hamilton 1=Madison
    Xrel_tr = np.array([r["_rel"] for r in train])
    Xcnt_tr = np.array([r["_cnt"] for r in train])

    # ---------- (A) Burrows's Delta ----------
    # z-score MFW rel-freqs on the TRAINING corpus, author centroid = mean z, classify by min |delta|
    mu = Xrel_tr.mean(0); sd = Xrel_tr.std(0); sd[sd==0]=1e-9
    def z(r): return (r["_rel"]-mu)/sd
    hz = np.mean([z(r) for r in ham], 0)
    mz = np.mean([z(r) for r in mad], 0)
    def delta_call(r):
        zr = z(r)
        dh = np.mean(np.abs(zr-hz)); dm = np.mean(np.abs(zr-mz))
        return ("MADISON" if dm<dh else "HAMILTON"), dh, dm
    # LOO CV on known
    def delta_call_cv(target, pool_ham, pool_mad):
        mu2 = np.array([r["_rel"] for r in pool_ham+pool_mad])
        m2 = mu2.mean(0); s2 = mu2.std(0); s2[s2==0]=1e-9
        hz2 = np.mean([(r["_rel"]-m2)/s2 for r in pool_ham],0)
        mz2 = np.mean([(r["_rel"]-m2)/s2 for r in pool_mad],0)
        zr = (target["_rel"]-m2)/s2
        return "MADISON" if np.mean(np.abs(zr-mz2))<np.mean(np.abs(zr-hz2)) else "HAMILTON"
    correct=0
    for r in train:
        ph = [x for x in ham if x is not r]; pm=[x for x in mad if x is not r]
        pred = delta_call_cv(r, ph, pm)
        truth = "HAMILTON" if r["label"]=="HAMILTON" else "MADISON"
        correct += (pred==truth)
    print(f"\n[A] Burrows Delta  LOO-CV accuracy on known: {correct}/{len(train)} = {correct/len(train):.3f}")
    dcall = {}
    for r in disp:
        call, dh, dm = delta_call(r)
        dcall[r["paper"]] = (call, dh, dm)

    # ---------- (B) Multinomial NB on counts ----------
    nb = MultinomialNB(alpha=1.0).fit(Xcnt_tr, ytr)
    loo = LeaveOneOut(); ok=0
    for tr_i, te_i in loo.split(Xcnt_tr):
        m = MultinomialNB(alpha=1.0).fit(Xcnt_tr[tr_i], ytr[tr_i])
        ok += (m.predict(Xcnt_tr[te_i])[0]==ytr[te_i][0])
    print(f"[B] Multinomial NB LOO-CV accuracy on known: {ok}/{len(train)} = {ok/len(train):.3f}")
    Xcnt_d = np.array([r["_cnt"] for r in disp])
    nb_pred = nb.predict(Xcnt_d); nb_prob = nb.predict_proba(Xcnt_d)[:,1]

    # ---------- (C) Logistic regression on rel-freq (standardised) ----------
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    def lr(): return make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=2000))
    ok2=0
    for tr_i, te_i in loo.split(Xrel_tr):
        m = lr().fit(Xrel_tr[tr_i], ytr[tr_i])
        ok2 += (m.predict(Xrel_tr[te_i])[0]==ytr[te_i][0])
    lrm = lr().fit(Xrel_tr, ytr)
    Xrel_d = np.array([r["_rel"] for r in disp])
    lr_pred = lrm.predict(Xrel_d); lr_prob = lrm.predict_proba(Xrel_d)[:,1]
    print(f"[C] LogReg (rel-freq) LOO-CV accuracy on known: {ok2}/{len(train)} = {ok2/len(train):.3f}")

    LAB = {0:"HAMILTON",1:"MADISON"}
    print("\n=== DISPUTED PAPER CALLS (0=Hamilton 1=Madison; prob = P(Madison)) ===")
    print(f"{'No.':>4} {'Delta':>9} {'NB':>9} {'P(M)_NB':>8} {'LogReg':>9} {'P(M)_LR':>8}")
    rows=[]
    all_madison = True
    for i,r in enumerate(disp):
        p = r["paper"]
        dc = dcall[p][0]
        nbc = LAB[nb_pred[i]]; lrc = LAB[lr_pred[i]]
        print(f"{p:>4} {dc:>9} {nbc:>9} {nb_prob[i]:8.3f} {lrc:>9} {lr_prob[i]:8.3f}")
        agree_mad = (dc=="MADISON" and nbc=="MADISON" and lrc=="MADISON")
        if not agree_mad: all_madison=False
        rows.append({"paper":p,"delta":dc,"nb":nbc,"nb_pmad":round(float(nb_prob[i]),4),
                     "logreg":lrc,"lr_pmad":round(float(lr_prob[i]),4)})
    n_mad_delta = sum(1 for r in disp if dcall[r["paper"]][0]=="MADISON")
    n_mad_nb = int((nb_pred==1).sum()); n_mad_lr=int((lr_pred==1).sum())
    print(f"\nDisputed called MADISON:  Delta {n_mad_delta}/12   NB {n_mad_nb}/12   LogReg {n_mad_lr}/12")
    print(f"ALL THREE call all 12 disputed = Madison: {all_madison}")

    # famous discriminators
    print("\n=== famous discriminators (per-1000-words mean) ===")
    def per1000(group, w):
        idx = FUNC_WORDS.index(w)
        return np.mean([r["_cnt"][idx]/r["_ntok"]*1000 for r in group])
    for w in ["upon","while","whilst","on","there","by"]:
        if w in FUNC_WORDS:
            print(f"  {w:8} Hamilton {per1000(ham,w):6.2f}  Madison {per1000(mad,w):6.2f}  Disputed {per1000(disp,w):6.2f}")

    out = {"train":{"hamilton":len(ham),"madison":len(mad)},
           "loo_cv":{"delta":correct/len(train),"nb":ok/len(train),"logreg":ok2/len(train)},
           "disputed":rows,
           "disputed_madison_counts":{"delta":n_mad_delta,"nb":n_mad_nb,"logreg":n_mad_lr,"of":12},
           "all_three_unanimous_madison":all_madison}
    with open(os.path.join(HERE,"..","stylometry_result.json"),"w") as f:
        json.dump(out,f,indent=2)
    print("\nwrote stylometry_result.json")

if __name__ == "__main__":
    main()
