#!/usr/bin/env python3
"""Legal-systems character matrix. Reads the four scored corpora (all held/reused),
builds the system x axis matrix, tests whether legal traditions occupy different
regions of character space (length + era controlled), and where an outcome exists,
tests whether the WINNING advocacy character differs by system (does affect help in
an adversarial court but hurt in an inquisitorial one).

Instrument: identical 8-axis DWEB 7B scores across all four. matter/manner PC1 uses
the fixed series projection (the internal reference table, 2,648,406 rows).

Corpora (all pre-scored, reused; nothing rescored):
  OldBailey  568  adversarial UK criminal, verdict 1=guilty(prosecution wins)/0=acquittal, year 1674-1910
  SCOTUS     800  adversarial US appellate oral advocacy, won 1/0 (advocate on winning side)
  ECHR       700  inquisitorial EU judgments, outcome 1=violation(applicant wins)/0=no-violation
  ParlaMint  409  legislative pole (parlamint/power_scored.jsonl), no binary win outcome
"""
import json, numpy as np
from scipy import stats
import statsmodels.formula.api as smf
import statsmodels.api as sm
import pandas as pd

DWEB = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
# fixed series matter/manner projection (+ = MATTER pole)
MEAN = np.array([0.469346,0.421638,0.320522,0.566215,0.393366,0.466498,0.525924,0.281533])
STD  = np.array([0.107728,0.106233,0.067995,0.058413,0.06427,0.124805,0.049623,0.095268])
PC1  = np.array([0.442497,0.397396,0.225237,0.392281,-0.352361,-0.256375,0.369661,-0.339294])

def proj(ch):
    v = np.array([ch[a] for a in DWEB], float)
    return float(((v-MEAN)/STD) @ PC1)

def load(path, system, tradition, region, outcome_key=None, nwords_key=None, year_key=None):
    rows=[]
    for l in open(path):
        try: r=json.loads(l)
        except Exception: continue
        ch=r.get("char")
        if not ch or not all(a in ch for a in DWEB): continue
        rec={"system":system,"tradition":tradition,"region":region}
        for a in DWEB: rec[a]=float(ch[a])
        rec["pc1"]=proj(ch)
        if nwords_key and nwords_key in r:
            try: rec["nwords"]=float(r[nwords_key])
            except Exception: rec["nwords"]=np.nan
        else: rec["nwords"]=np.nan
        rec["outcome"]= (int(r[outcome_key]) if (outcome_key and outcome_key in r and r[outcome_key] not in (None,"")) else np.nan)
        if year_key and year_key in r:
            try: rec["year"]=int(str(r[year_key])[:4])
            except Exception: rec["year"]=np.nan
        else: rec["year"]=np.nan
        rows.append(rec)
    return rows

BASE="the internal corpus store"
rows=[]
rows+=load(f"{BASE}/oldbailey/oldbailey_scored.jsonl","OldBailey","adversarial","UK",
           outcome_key="verdict", nwords_key="nwords", year_key="year")
rows+=load(f"{BASE}/legal_matrix/scotus_scored.jsonl","SCOTUS","adversarial","US",
           outcome_key="won", nwords_key="n_words")
rows+=load(f"{BASE}/legal_matrix/echr_scored.jsonl","ECHR","inquisitorial","EU",
           outcome_key="outcome", nwords_key="n_words")
rows+=load(f"{BASE}/parlamint/legislative_pole_frozen.jsonl","ParlaMint","legislative","EU-multi",
           outcome_key=None, nwords_key="n_words")

df=pd.DataFrame(rows)
print("=== N per system ===")
print(df.groupby("system").size().to_string())
print()
print("=== era (year) coverage — systems are also different ERAS (unavoidable confound with system) ===")
for sy in ["OldBailey","SCOTUS","ECHR","ParlaMint"]:
    d=df[df.system==sy]
    if d["year"].notna().any():
        print(f"  {sy:<10} year {int(d['year'].min())}-{int(d['year'].max())} (median {int(d['year'].median())})")
    else:
        print(f"  {sy:<10} modern (no per-row year; corpus era: SCOTUS ~1955-2019, ECHR ~2000-2019, ParlaMint ~2015-2022)")
print("  -> OldBailey is historical (pre-1911); the other three are modern. Cross-system era is COLLINEAR with system")
print("     and cannot be regressed out at the corpus level. Era is controlled WITHIN OldBailey (year covariate) for the winner test.")
print()

df["logw"]=np.log1p(df["nwords"])
SYS=["OldBailey","SCOTUS","ECHR","ParlaMint"]

def anova_block(frame, cols, prefix=""):
    surv=0
    for a in cols:
        groups=[frame[frame.system==sy][prefix+a].dropna().values for sy in SYS]
        F,p=stats.f_oneway(*groups)
        grand=frame[prefix+a].mean(); ssb=sum(len(g)*(g.mean()-grand)**2 for g in groups)
        sst=((frame[prefix+a]-grand)**2).sum(); eta2=ssb/sst if sst>0 else 0
        star="***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else ""
        if p<0.05: surv+=1
        print(f"  {a:<16} F={F:8.1f}  p={p:9.2e}  eta^2={eta2:5.3f} {star}")
    return surv

print("="*100)
print("MATRIX 1 - system x axis: RAW mean of each axis (0..1), + matter/manner PC1 (series projection)")
print("="*100)
hdr="system      " + "".join(f"{a[:6]:>8}" for a in DWEB) + f"{'PC1':>9}{'medWords':>10}"
print(hdr)
for sy in SYS:
    d=df[df.system==sy]
    line=f"{sy:<12}"+"".join(f"{d[a].mean():>8.2f}" for a in DWEB)
    line+=f"{d['pc1'].mean():>9.2f}{int(d['nwords'].median()) if d['nwords'].notna().any() else 0:>10}"
    print(line)
print()
print("per-axis one-way ANOVA across the 4 systems (do traditions differ on each axis?) + eta^2")
anova_block(df, DWEB+["pc1"])
print()

print("="*100)
print("MATRIX 2 - LENGTH CONTROLLED: per-axis system means after regressing out log(words) (pooled residuals)")
print("="*100)
res=df.copy()
for a in DWEB+["pc1"]:
    ok=res["logw"].notna()
    X=sm.add_constant(res.loc[ok,"logw"])
    b=sm.OLS(res.loc[ok,a],X).fit()
    res.loc[ok,"r_"+a]=res.loc[ok,a]-b.predict(X)
print("system      " + "".join(f"{a[:6]:>8}" for a in DWEB) + f"{'PC1':>9}")
for sy in SYS:
    d=res[res.system==sy]
    print(f"{sy:<12}"+"".join(f"{d['r_'+a].mean():>8.2f}" for a in DWEB)+f"{d['r_pc1'].mean():>9.2f}")
print("  (values are residual axis means: 0 = the pooled length-predicted level; sign shows the tradition's tilt beyond length)")
print()
print("does the system separation SURVIVE length control? per-axis ANOVA on residuals:")
surv=anova_block(res, DWEB+["pc1"], prefix="r_")
print(f"  -> {surv}/9 axes still separate systems after length control")
print()

print("SEPARATION STRENGTH - predict system from the 8 axes (multinomial logistic, 5-fold CV)")
try:
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.pipeline import make_pipeline
    X=df[DWEB].values; y=df["system"].values
    pipe=make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
    acc=cross_val_score(pipe,X,y,cv=5,scoring="accuracy").mean()
    print(f"  8-axis accuracy = {acc:.3f}  (chance = 0.250)")
    Xl=df[["logw"]].fillna(df["logw"].mean()).values
    accl=cross_val_score(make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000)),Xl,y,cv=5).mean()
    print(f"  length-only accuracy = {accl:.3f}  (how much is just length)")
except Exception as e:
    print("  sklearn unavailable:",e)
print()

print("="*100)
print("WINNING CHARACTER BY SYSTEM - does the character of the WINNER differ, and does AFFECT help or hurt?")
print("="*100)
print("winner defn: OldBailey verdict=1 (conviction, prosecution wins) | SCOTUS won=1 (advocate on winning side) | ECHR outcome=1 (violation, applicant wins)")
print("NOTE asymmetry: only SCOTUS isolates ADVOCATE speech; OldBailey=whole-trial report, ECHR=court judgment. Affect there is the court's/report's, not a clean advocate signal.\n")
for sy in ["OldBailey","SCOTUS","ECHR"]:
    d=df[(df.system==sy) & df.outcome.notna()].copy()
    if len(d)<20:
        print(f"{sy}: too few outcome-labelled rows"); continue
    w=d[d.outcome==1]; lo=d[d.outcome==0]
    print(f"--- {sy} ({d.tradition.iloc[0]}, {d.region.iloc[0]}) | winners={len(w)} losers={len(lo)} ---")
    for a in ["pc1","affect","rigour","depth","stance"]:
        t,p=stats.ttest_ind(w[a],lo[a],equal_var=False)
        dsd=np.sqrt((w[a].var()+lo[a].var())/2); dc=(w[a].mean()-lo[a].mean())/(dsd if dsd>1e-9 else 1)
        star="***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else ""
        print(f"    {a:<8} winner={w[a].mean():.3f} loser={lo[a].mean():.3f}  d(win-lose)={w[a].mean()-lo[a].mean():+.3f} (cohen={dc:+.2f}) p={p:.3g} {star}")
    d["z_affect"]=(d.affect-d.affect.mean())/d.affect.std(ddof=0)
    d["z_pc1"]=(d.pc1-d.pc1.mean())/d.pc1.std(ddof=0)
    d["z_logw"]=(d.logw-d.logw.mean())/d.logw.std(ddof=0)
    has_year = d["year"].notna().sum() > 20
    if has_year:
        d["z_year"]=(d.year-d.year.mean())/d.year.std(ddof=0)
    forms = ["outcome ~ z_affect + z_logw","outcome ~ z_pc1 + z_logw"]
    if has_year:
        forms += ["outcome ~ z_affect + z_logw + z_year","outcome ~ z_pc1 + z_logw + z_year"]
    for form in forms:
        try:
            m=smf.logit(form,data=d).fit(disp=0)
            key=form.split("~")[1].split("+")[0].strip()
            coef=m.params[key]; p=m.pvalues[key]; star="***" if p<0.001 else "**" if p<0.01 else "*" if p<0.05 else ""
            extra=""
            if "z_year" in form: extra=f"  year coef={m.params['z_year']:+.3f}"
            print(f"    [{form}]  {key} coef={coef:+.3f} (odds/SD={np.exp(coef):.2f}) p={p:.3g} {star}  logw coef={m.params['z_logw']:+.3f}{extra}")
        except Exception as e:
            print(f"    [{form}] fit failed: {e}")
    print()
print("READ: affect coef > 0 = affect HELPS the winner in that system; < 0 = affect HURTS. Compare adversarial (OldBailey,SCOTUS) vs inquisitorial (ECHR).")
print("For OldBailey the '+ z_year' forms show whether the affect/pc1 effect survives ERA control (year 1674-1910).")
