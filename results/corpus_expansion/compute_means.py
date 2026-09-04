import json, glob, os
BASE="the internal corpus store"
AX=["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
CORP=["fw2_indonesian","fw2_thai","fw2_vietnamese","fw2_filipino","fw2_kazakh","fw2_uzbek",
      "fw2_samoan","fw2_maori","fw2_fijian","fw2_amharic","fw2_somali",
      "twitter_sentiment140","mastodon_toots","telegram_channels","youtube_comments","gutenberg_english"]
rows=[]
for n in CORP:
    p=os.path.join(BASE,n,"char.jsonl")
    if not os.path.exists(p):
        rows.append((n,0,None)); continue
    sums={a:0.0 for a in AX}; k=0
    for line in open(p):
        try: c=json.loads(line)["char"]
        except Exception: continue
        if all(a in c for a in AX):
            for a in AX: sums[a]+=float(c[a])
            k+=1
    means={a:(sums[a]/k if k else 0) for a in AX} if k else None
    rows.append((n,k,means))
print("corpus\tn\t"+"\t".join(AX))
for n,k,m in rows:
    if m: print(n+"\t"+str(k)+"\t"+"\t".join(f"{m[a]:.3f}" for a in AX))
    else: print(n+"\t"+str(k)+"\t(no scores yet)")
# also emit json for the RESULT writer
out={n:{"n":k,"means":m} for n,k,m in rows}
json.dump(out, open(os.path.join(BASE,"expansion_means.json"),"w"), indent=0)
