import json, random
SRC="the internal corpus store/bible_multilingual/bible_multilingual.jsonl"
OUT="the internal corpus store/bible_multilingual/fingerprint_score_input.jsonl"
# well-populated pairs; target-language codes
WANT={"eng-deu":"deu","eng-fra":"fra","eng-spa":"spa","eng-por":"por",
      "eng-arb":"arb","eng-cmn":"cmn","eng-swh":"swh"}
N=200  # verses per pair
random.seed(11)
rows=[]
byp={}
for l in open(SRC):
    r=json.loads(l); p=r["_pair"]
    if p in WANT: byp.setdefault(p,[]).append(r["verse"])
n=0
for p,tgt in WANT.items():
    v=byp.get(p,[]); random.shuffle(v); v=v[:N]
    for i,verse in enumerate(v):
        e=verse.get("eng","").strip(); t=verse.get(tgt,"").strip()
        if len(e)<40 or len(t)<20: continue
        rows.append({"id":f"{p}__{i}__eng","text":e})
        rows.append({"id":f"{p}__{i}__{tgt}","text":t})
        n+=1
with open(OUT,"w") as f:
    for r in rows: f.write(json.dumps(r,ensure_ascii=False)+"\n")
print("pairs:",list(WANT),"paired verses:",n,"scoring rows:",len(rows),"->",OUT)
