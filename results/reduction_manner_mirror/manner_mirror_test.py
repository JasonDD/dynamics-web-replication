#!/usr/bin/env python3
"""manner_mirror_test.py -- the symmetric test: does the MANNER pole occupy its own nomological net?

The matter reductions showed matter loads on the substance subspaces (complexity, Grice quantity and
relation, the ELM central route, Biber's informational pole) and stays dark on the rest. The strong test
of a STRUCTURED geometry, rather than a single quality axis, is whether the manner pole occupies the
COMPLEMENTARY territory: dark where matter is bright, bright on affective and social constructs where
matter is dark or negative. The double dissociation is the result, not another positive correlation.

Predictions are written here BEFORE the numbers are read (PREDICT below), including the DARK cells:
  matter  = mean z(rigour, depth)      manner = mean z(affect, register)
  Complexity (grade, sentence and word length):  matter UP,   manner ~0 (dark)
  Cohesion (connectives, sentence overlap):       matter ~0,   manner ~0
  Grice quantity/relation VIOLATION:              matter UP,   manner ~0/down
  Grice manner VIOLATION:                          matter ~0,   manner ~0 (both dark)
  Affective/social (emotion, exclaim, pronouns):  matter DOWN, manner UP (manner's bright cell)

All external measures are surface or lexicon, no model in the loop, so they are independent of the
character scorer. Grice cells reuse the held cc_v3.reddit_grice judgements (Mistral, a different family).
Item level and within room (demeaned) correlations; analysis only.
"""
import os, re, json, math
import numpy as np, psycopg2
from collections import defaultdict

DWEB=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
OUT=os.path.expanduser("~/manner_mirror_out"); os.makedirs(OUT, exist_ok=True)
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
conn=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"); c=conn.cursor()

c.execute(f"SELECT {','.join(DWEB)} FROM cc_v3.domain_char8_expanded")
allc=np.array([[float(x) for x in r] for r in c.fetchall()],float); MEAN=allc.mean(0); STD=allc.std(0)+1e-9
def zc(ch,a): return (float(ch[a])-MEAN[DWEB.index(a)])/STD[DWEB.index(a)]

# ---- surface / lexicon external measures, independent of the scorer ----
WORD=re.compile(r"[a-z]+(?:'[a-z]+)?"); SENT=re.compile(r"[.!?]+"); VOWELG=re.compile(r"[aeiouy]+")
CONN=set("because therefore thus hence consequently so since however although though whereas nevertheless moreover furthermore then after before when while until".split())
FIRST2=set("i me my mine myself we us our ours you your yours yourself".split())
EMOTION=set(("love hate happy sad angry afraid fear joy hope scared worried excited awful terrible wonderful "
  "amazing great awesome horrible disgusting beautiful ugly cry laugh smile heart damn hell wtf omg lol lmao "
  "please thanks thank sorry wow ugh yay").split())
INTENS=set("very really so totally absolutely completely literally super extremely incredibly damn fucking".split())
EMOJI=re.compile(r"[:;=8xX][-']?[)(DPpoO/\\\[\]|]|</?3|[\U0001F300-\U0001FAFF☀-➿]")
def syll(w):
    n=len(VOWELG.findall(w));
    if w.endswith("e"): n=max(1,n-1)
    return max(1,n)
def feats(text):
    t=text.lower(); sents=[s for s in SENT.split(text) if s.strip()]
    toks=WORD.findall(t); n=len(toks)
    if n<30 or len(sents)<2: return None
    wps=n/len(sents); syl=sum(syll(w) for w in toks)
    fk=0.39*wps+11.8*(syl/n)-15.59
    mwl=float(np.mean([len(w) for w in toks]))
    conn=sum(w in CONN for w in toks)/n
    def content(s): return set(w for w in WORD.findall(s.lower()) if len(w)>3)
    cs=[content(s) for s in sents]; ov=[len(a&b)/len(a|b) if (a|b) else 0 for a,b in zip(cs,cs[1:])]
    refcoh=float(np.mean(ov)) if ov else 0.0
    exclaim=text.count("!")/max(len(sents),1)
    emoji=len(EMOJI.findall(text))/n
    pron=sum(w in FIRST2 for w in toks)/n
    emo=sum(w in EMOTION for w in toks)/n
    intens=sum(w in INTENS for w in toks)/n
    caps=sum(1 for w in re.findall(r"[A-Za-z]{3,}", text) if w.isupper())/max(len(re.findall(r"[A-Za-z]{3,}",text)),1)
    return dict(fk_grade=fk, words_per_sentence=wps, mean_word_len=mwl,
                connective_rate=conn, referential_cohesion=refcoh,
                exclaim_rate=exclaim, emoji_rate=emoji, pronoun_12_rate=pron, emotion_word_rate=emo,
                intensifier_rate=intens, allcaps_rate=caps)

GROUPS={"Complexity":["fk_grade","words_per_sentence","mean_word_len"],
        "Cohesion":["connective_rate","referential_cohesion"],
        "Affective_social":["exclaim_rate","emoji_rate","pronoun_12_rate","emotion_word_rate","intensifier_rate","allcaps_rate"]}
IDX=[k for g in GROUPS.values() for k in g]
PREDICT={"matter":{"Complexity":"UP","Cohesion":"~0","Affective_social":"DOWN","grice_QR":"UP","grice_manner":"~0"},
         "manner":{"Complexity":"~0","Cohesion":"~0","Affective_social":"UP","grice_QR":"~0/down","grice_manner":"~0"}}

c.execute("SELECT w.id, w.subreddit, w.body, w.char, g.quantity, g.relation, g.manner "
          "FROM cc_v3.reddit_wide w LEFT JOIN cc_v3.reddit_grice g ON g.id=w.id "
          "WHERE w.char IS NOT NULL AND w.char ? 'rigour' AND length(w.body)>=200")
rows=c.fetchall(); print(f"fetched {len(rows)}", flush=True)
subs=[]; matter=[]; manner=[]; aff=[]; reg=[]; X=[]; GQR=[]; GMAN=[]; hasg=[]
skip=0
for _id, sub, body, ch, gq, gr, gm in rows:
    ch=ch if isinstance(ch,dict) else json.loads(ch)
    if any(a not in ch for a in DWEB): skip+=1; continue
    f=feats(body)
    if f is None: skip+=1; continue
    subs.append(sub)
    matter.append((zc(ch,"rigour")+zc(ch,"depth"))/2.0)
    manner.append((zc(ch,"affect")+zc(ch,"register"))/2.0)
    aff.append(zc(ch,"affect")); reg.append(zc(ch,"register"))
    X.append([f[k] for k in IDX])
    if gq is not None and gr is not None:
        GQR.append(((gq+gr)/2.0)); GMAN.append(gm if gm is not None else np.nan); hasg.append(len(subs)-1)
subs=np.array(subs); matter=np.array(matter); manner=np.array(manner); aff=np.array(aff); reg=np.array(reg)
X=np.array(X,float); hasg=np.array(hasg,int); GQR=np.array(GQR); GMAN=np.array(GMAN)
print(f"usable {len(X)} (skipped {skip}); grice subset {len(hasg)}", flush=True)

def pear(a,b):
    a=a-a.mean(); b=b-b.mean(); d=math.sqrt((a*a).sum()*(b*b).sum()); return float((a*b).sum()/d) if d else float("nan")
rooms=sorted(set(subs)); rc={r_:k for k,r_ in enumerate(rooms)}; g=np.array([rc[s] for s in subs])
def dm(v, gg=None):
    gg=g if gg is None else gg
    m=np.zeros(len(rooms)); nn=np.zeros(len(rooms)); np.add.at(m,gg,v); np.add.at(nn,gg,1); return v-(m/np.maximum(nn,1))[gg]

def group_r(score, idxlist):
    # mean absolute-signed correlation across the group's indices, sign kept per index then averaged
    rs=[pear(score, X[:,IDX.index(k)]) for k in idxlist]
    return float(np.mean(rs)), {k:round(pear(score,X[:,IDX.index(k)]),3) for k in idxlist}

summary={"n":len(X), "n_rooms":len(rooms), "grice_n":len(hasg), "predictions":PREDICT, "matter":{}, "manner":{}}
print("\n=== MATTER vs MANNER nomological net (item r; group = mean of member indices) ===")
print(f"{'construct group':<20} {'matter':>8} {'manner':>8}   predicted (matter/manner)")
for name in GROUPS:
    mr,_=group_r(matter, GROUPS[name]); nr,_=group_r(manner, GROUPS[name])
    summary["matter"][name]=mr; summary["manner"][name]=nr
    print(f"{name:<20} {mr:+8.3f} {nr:+8.3f}   {PREDICT['matter'][name]:>5} / {PREDICT['manner'][name]}")
# Grice cells on the judged subset
gm_matter=matter[hasg]; gm_manner=manner[hasg]
qr_m=pear(gm_matter,GQR); qr_n=pear(gm_manner,GQR)
okm=~np.isnan(GMAN)
man_m=pear(gm_matter[okm],GMAN[okm]); man_n=pear(gm_manner[okm],GMAN[okm])
summary["matter"]["grice_QR"]=qr_m; summary["manner"]["grice_QR"]=qr_n
summary["matter"]["grice_manner"]=man_m; summary["manner"]["grice_manner"]=man_n
print(f"{'Grice quant+relat':<20} {qr_m:+8.3f} {qr_n:+8.3f}   {PREDICT['matter']['grice_QR']:>5} / {PREDICT['manner']['grice_QR']}")
print(f"{'Grice manner':<20} {man_m:+8.3f} {man_n:+8.3f}   {PREDICT['matter']['grice_manner']:>5} / {PREDICT['manner']['grice_manner']}")
# the double dissociation, the headline: matter->complexity vs manner->affective, and the cross cells
cm,_=group_r(matter,GROUPS["Complexity"]); ca,_=group_r(manner,GROUPS["Affective_social"])
xm,_=group_r(manner,GROUPS["Complexity"]); xa,_=group_r(matter,GROUPS["Affective_social"])
summary["double_dissociation"]=dict(matter_complexity=cm, manner_affective=ca, manner_complexity=xm, matter_affective=xa)
print(f"\nDOUBLE DISSOCIATION: matter->complexity {cm:+.3f}  manner->affective {ca:+.3f}   |"
      f"  OFF cells: manner->complexity {xm:+.3f}  matter->affective {xa:+.3f}")
# per axis detail for affective, so the manner bright cell is legible
print("\naffective/social detail (matter | manner | affect axis | register axis):")
for k in GROUPS["Affective_social"]:
    xi=X[:,IDX.index(k)]
    print(f"  {k:<20} {pear(matter,xi):+.3f}  {pear(manner,xi):+.3f}  {pear(aff,xi):+.3f}  {pear(reg,xi):+.3f}")
json.dump(summary, open(f"{OUT}/manner_mirror.json","w"), indent=2)
print(f"\nwrote {OUT}/manner_mirror.json", flush=True)
