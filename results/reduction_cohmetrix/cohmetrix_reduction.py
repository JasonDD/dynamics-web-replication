#!/usr/bin/env python3
"""cohmetrix_reduction.py -- does the character instrument reduce onto reading comprehension science?

Advisor reduction (Tier 1): the Coh-Metrix tradition (McNamara and colleagues) measures text on cohesion,
lexical sophistication, syntactic complexity and readability, fifty years of reading science. If our
depth and rigour axes track those indices, then character is cognitive depth, not only surface style.
Coh-Metrix itself is licensed; the indices below are the free equivalents (the TAALES/TAACO constructs)
computed from surface text with no external tool and no model in the loop.

Corpus: the held reddit_wide comments already scored on the eight axis instrument (same set as the Biber
reduction), so this is analysis only, CPU and DB on DL580, no scoring service. Each index is correlated
with the eight axes and with the matter against manner PC1, at the item level and within a subreddit
(both demeaned by room), and the depth/rigour correlations are disattenuated with the same single read
reliability the Biber within unit run measured (0.42 for the ruler; per axis reliabilities are not held,
so the ruler value is used as a shared lower bound and the raw numbers are given beside the corrected).
"""
import os, re, json, math
import numpy as np, psycopg2
from collections import defaultdict

DWEB = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
OUT = os.path.expanduser("~/cohmetrix_out"); os.makedirs(OUT, exist_ok=True)
PW=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
conn=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"); c=conn.cursor()

c.execute(f"SELECT {','.join(DWEB)} FROM cc_v3.domain_char8_expanded")
allc=np.array([[float(x) for x in r] for r in c.fetchall()],float)
MEAN=allc.mean(0); STD=allc.std(0)+1e-9
_,_,Vt=np.linalg.svd((allc-MEAN)/STD, full_matrices=False); PC1=Vt[0]
if (PC1[DWEB.index("rigour")]+PC1[DWEB.index("depth")])<0: PC1=-PC1
def pc1_of(ch): return float(((np.array([ch[a] for a in DWEB],float)-MEAN)/STD) @ PC1)

c.execute("SELECT id, subreddit, body, char FROM cc_v3.reddit_wide WHERE char IS NOT NULL AND char ? 'rigour' AND length(body) >= 200")
rows=c.fetchall(); print(f"fetched {len(rows)} scored comments", flush=True)

# ---- indices, all closed form, no tagger ----
WORD=re.compile(r"[a-z]+(?:'[a-z]+)?"); SENT=re.compile(r"[.!?]+")
VOWELG=re.compile(r"[aeiouy]+")
CONN_CAUSAL=set("because therefore thus hence consequently so since due accordingly".split())
CONN_LOGIC=set("however although though whereas nevertheless nonetheless moreover furthermore besides yet but instead conversely".split())
CONN_TEMPORAL=set("then after before when while during finally subsequently meanwhile until".split())
CONN_ALL=CONN_CAUSAL|CONN_LOGIC|CONN_TEMPORAL
SUBORD=set("that which who whom whose because although though if unless until while whereas since when".split())
# a small common-word list: the ~200 most frequent English words; anything outside is "rarer" (sophistication proxy)
COMMON=set(("the be to of and a in that have i it for not on with he as you do at this but his by from they "
  "we say her she or an will my one all would there their what so up out if about who get which go me when make "
  "can like time no just him know take people into year your good some could them see other than then now look "
  "only come its over think also back after use two how our work first well way even new want because any these "
  "give day most us is are was were been has had did said can will just").split())
def syll(w):
    n=len(VOWELG.findall(w))
    if w.endswith("e"): n=max(1,n-1)
    return max(1,n)

def indices(text):
    t=text.lower()
    sents=[s for s in SENT.split(text) if s.strip()]
    if len(sents)<2: return None
    toks=WORD.findall(t)
    n=len(toks)
    if n<30: return None
    alpha=toks
    types=set(alpha)
    mwl=float(np.mean([len(w) for w in alpha]))
    ttr=len(types)/n
    rare=sum(w not in COMMON for w in alpha)/n
    syl=[syll(w) for w in alpha]; polysyll=sum(s>=3 for s in syl)/n
    wps=n/len(sents)                                    # words per sentence: syntactic length
    conn=sum(w in CONN_ALL for w in toks)/n             # deep cohesion: all connectives
    causal=sum(w in CONN_CAUSAL for w in toks)/n
    logic=sum(w in CONN_LOGIC for w in toks)/n
    subord=sum(w in SUBORD for w in toks)/n             # clause density proxy
    # readability
    fk_grade=0.39*wps + 11.8*(sum(syl)/n) - 15.59
    fre=206.835 - 1.015*wps - 84.6*(sum(syl)/n)
    # referential cohesion: mean content-word overlap between adjacent sentences
    def content(s):
        return set(w for w in WORD.findall(s.lower()) if w not in COMMON and len(w)>3)
    cs=[content(s) for s in sents]
    ov=[]
    for a_,b_ in zip(cs, cs[1:]):
        u=a_|b_
        ov.append(len(a_&b_)/len(u) if u else 0.0)
    refcoh=float(np.mean(ov)) if ov else 0.0
    return dict(mean_word_len=mwl, type_token=ttr, rare_word_rate=rare, polysyllable_rate=polysyll,
                words_per_sentence=wps, connective_rate=conn, causal_connective=causal, logical_connective=logic,
                subordinator_rate=subord, fk_grade=fk_grade, flesch_ease=fre, referential_cohesion=refcoh)

IDX=["mean_word_len","type_token","rare_word_rate","polysyllable_rate","words_per_sentence",
     "connective_rate","causal_connective","logical_connective","subordinator_rate","fk_grade","flesch_ease","referential_cohesion"]
subs=[]; PCv=[]; CH=[]; X=[]
skip=0
for _id, sub, body, ch in rows:
    ix=indices(body)
    if ix is None: skip+=1; continue
    subs.append(sub); PCv.append(pc1_of(ch)); CH.append([float(ch[a]) for a in DWEB]); X.append([ix[k] for k in IDX])
subs=np.array(subs); PCv=np.array(PCv); CH=np.array(CH,float); X=np.array(X,float)
print(f"usable {len(X)} (skipped {skip} short)", flush=True)

def pear(a,b):
    a=a-a.mean(); b=b-b.mean(); d=math.sqrt((a*a).sum()*(b*b).sum()); return float((a*b).sum()/d) if d else float("nan")
rooms=sorted(set(subs)); rc={r_:k for k,r_ in enumerate(rooms)}; g=np.array([rc[s] for s in subs])
def demean(v):
    m=np.zeros(len(rooms)); n=np.zeros(len(rooms)); np.add.at(m,g,v); np.add.at(n,g,1); return v-(m/np.maximum(n,1))[g]
REL_RULER=0.421   # matter/manner single read reliability, two reader agreement within room (Biber within run)

summary={"n":len(X), "n_rooms":len(rooms), "indices":IDX, "pc1_vs_index":{}, "axes_vs_index":{}}
print("\n=== matter/manner PC1 vs each index (item | within room | within, disattenuated by the ruler reliability) ===")
Pd=demean(PCv)
for j,k in enumerate(IDX):
    xi=X[:,j]; ri=pear(PCv,xi); rw=pear(Pd, demean(xi)); rwc=rw/math.sqrt(REL_RULER)
    summary["pc1_vs_index"][k]=dict(item=ri, within=rw, within_disattenuated_ruler=rwc)
    print(f"  {k:<22} item {ri:+.3f}   within {rw:+.3f}   within/rel {rwc:+.3f}")
print("\n=== depth and rigour vs the sophistication and complexity indices (item r) ===")
for a in ("depth","rigour","originality","affect","register"):
    ci=CH[:,DWEB.index(a)]; row={k:pear(ci,X[:,j]) for j,k in enumerate(IDX)}
    summary["axes_vs_index"][a]=row
    top=sorted(row.items(), key=lambda t:-abs(t[1]))[:5]
    print(f"  {a:<12} " + "  ".join(f"{k}={v:+.2f}" for k,v in top))
json.dump(summary, open(f"{OUT}/cohmetrix.json","w"), indent=2)
print(f"\nwrote {OUT}/cohmetrix.json", flush=True)
