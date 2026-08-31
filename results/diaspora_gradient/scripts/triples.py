#!/usr/bin/env python3
import json, numpy as np
d = json.load(open("/home/jason/projects/kronaxis/docs/papers/dynamics_web_series/results/diaspora_gradient/diaspora_result.json"))
byk = {(r["origin"],r["host"]):r for r in d["corridors"]}
DWEB = ["rigour","depth","originality","candour","affect","commercial_drive","stance","register"]
def show(k):
    r = byk.get(k)
    if not r: print(f"\n{k}: not analysed"); return
    print(f"\n### {r['origin']} -> {r['host']}  nO={r['nO']} nD={r['nD']} nH={r['nH']}  alpha={r['alpha']:.2f} ci={[round(x,2) for x in r['alpha_ci']]} resid={r['resid_offline']:.2f} inter={r['intermediate']}")
    pc=r['pc1']; print(f"    PC1  O={pc['O']:+.2f} D={pc['D']:+.2f} H={pc['H']:+.2f}  alpha_pc1={pc['alpha_pc1']:.2f}")
    print(f"    {'axis':13s} {'O(orig)':>8s} {'D(dias)':>8s} {'H(host)':>8s}  {'D between?':>10s}")
    for a in DWEB:
        O=r['per_axis'][a]['O']; D=r['per_axis'][a]['D']; H=r['per_axis'][a]['H']
        btwn = (min(O,H) <= D <= max(O,H))
        print(f"    {a:13s} {O:8.2f} {D:8.2f} {H:8.2f}  {str(btwn):>10s}")
    # count axes where D is between O and H
    nb = sum(1 for a in DWEB if min(r['per_axis'][a]['O'],r['per_axis'][a]['H'])<=r['per_axis'][a]['D']<=max(r['per_axis'][a]['O'],r['per_axis'][a]['H']))
    print(f"    axes with D strictly between O and H: {nb}/8")

# headline named diaspora corridors (significantly intermediate)
for k in [("IN","DE"),("GR","DE"),("PL","DE"),("MX","US"),("IT","US"),("GB","US"),("HR","DE"),("CN","US")]:
    show(k)
print("\n\n================ NULL / OVERSHOOT / REVERSE EXAMPLES ================")
for k in [("IT","DE"),("NL","DE"),("ES","DE"),("AT","DE"),("RU","DE")]:
    show(k)

# for the honest gradient: report the spread of within-corridor grad r for the significantly-intermediate set
sig = [r for r in d["corridors"] if r["alpha_ci"][0]>0.05 and r["alpha_ci"][1]<0.95]
gr = [ (r["gradient"] or {}).get("r") for r in sig if r.get("gradient")]
gr=[x for x in gr if x is not None]
import numpy as np
print(f"\n\nsig-intermediate corridors: {len(sig)}; their within-corridor grad r: mean={np.mean(gr):+.3f} min={min(gr):+.3f} max={max(gr):+.3f}")
