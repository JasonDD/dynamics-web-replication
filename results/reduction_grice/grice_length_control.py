import os,json,math,numpy as np,psycopg2
DWEB=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
MAX=["quantity","quality","relation","manner"]
pw=[l.split("=",1)[1].strip().strip('"').strip("'") for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
c=psycopg2.connect(f"host=127.0.0.1 port=5432 user=titan password={pw} dbname=tfs").cursor()
c.execute(f"SELECT {','.join(DWEB)} FROM the internal reference table")
allc=np.array([[float(x) for x in r] for r in c.fetchall()],float);M=allc.mean(0);S=allc.std(0)+1e-9
_,_,Vt=np.linalg.svd((allc-M)/S,full_matrices=False);PC1=Vt[0]
if PC1[0]+PC1[1]<0:PC1=-PC1
c.execute("SELECT g.quantity,g.quality,g.relation,g.manner,w.char,length(w.body) FROM an internal table g JOIN the internal Reddit corpus w ON w.id=g.id WHERE w.char ? 'rigour'")
Q=[];PCv=[];L=[]
for q,ql,rel,man,ch,ln in c.fetchall():
    ch=ch if isinstance(ch,dict) else json.loads(ch)
    if any(a not in ch for a in DWEB):continue
    Q.append([q,ql,rel,man]);PCv.append((( np.array([ch[a] for a in DWEB],float)-M)/S)@PC1);L.append(math.log(ln))
Q=np.array(Q);PCv=np.array(PCv);L=np.array(L)
def pear(a,b):
    a=a-a.mean();b=b-b.mean();d=math.sqrt((a*a).sum()*(b*b).sum());return float((a*b).sum()/d) if d else 0.0
def resid(y,x):
    x=x-x.mean();b=(x*(y-y.mean())).sum()/(x*x).sum();return (y-y.mean())-b*x
print(f"n={len(Q)}  r(PC1,loglen)={pear(PCv,L):+.3f}")
print("maxim :  raw r(PC1)  |  length-controlled partial r")
for j,m in enumerate(MAX):
    raw=pear(PCv,Q[:,j]); part=pear(resid(PCv,L),resid(Q[:,j],L))
    print(f"  {m:<9} {raw:+.3f}      {part:+.3f}")
