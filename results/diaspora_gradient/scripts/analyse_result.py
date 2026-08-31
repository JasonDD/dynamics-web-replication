#!/usr/bin/env python3
import json, numpy as np
d = json.load(open("/home/jason/projects/kronaxis/docs/papers/dynamics_web_series/results/diaspora_gradient/diaspora_result.json"))
print("n_corridors:", d["n_corridors"], "n_intermediate:", d["n_intermediate"], "mean_alpha:", round(d["mean_alpha"],3))
print("pooled_gradient:", d["pooled_gradient"])
print("params:", d["params"])
C = d["corridors"]
# sort by nD desc
C.sort(key=lambda r: -r["nD"])
print("\n=== TOP CORRIDORS BY n (diaspora domains) ===")
print(f"{'orig->host':12s} {'nD':>5s} {'nO':>6s} {'nH':>6s} {'alpha':>6s} {'ci':>16s} {'resid':>6s} {'a_pc1':>7s} {'grad_r':>7s} {'inter':>5s}")
for r in C[:40]:
    ci = r["alpha_ci"]; g = r["gradient"] or {}
    print(f"{r['origin']+'->'+r['host']:12s} {r['nD']:5d} {r['nO']:6d} {r['nH']:6d} {r['alpha']:6.2f} "
          f"[{ci[0]:5.2f},{ci[1]:5.2f}] {r['resid_offline']:6.2f} {r['pc1']['alpha_pc1']:7.2f} "
          f"{g.get('r',float('nan')):7.3f} {str(r['intermediate']):>5s}")

# classic diaspora corridors of interest
CLASSIC = [("TR","DE"),("PL","DE"),("PL","GB"),("IT","DE"),("IT","CH"),("RU","DE"),("IN","GB"),
           ("PT","FR"),("GR","DE"),("RO","IT"),("ES","FR"),("PL","NL"),("HR","DE"),("CZ","DE"),
           ("TR","NL"),("IE","GB"),("MX","US")]
byk = {(r["origin"],r["host"]):r for r in C}
print("\n=== CLASSIC DIASPORA CORRIDORS ===")
for k in CLASSIC:
    r = byk.get(k)
    if not r: print(f"{k[0]}->{k[1]}: (below n threshold / not analysed)"); continue
    ci=r["alpha_ci"]; g=r["gradient"] or {}
    print(f"{r['origin']+'->'+r['host']:8s} nD={r['nD']:4d} alpha={r['alpha']:5.2f} ci=[{ci[0]:.2f},{ci[1]:.2f}] "
          f"resid={r['resid_offline']:.2f} a_pc1={r['pc1']['alpha_pc1']:.2f} grad_r={g.get('r',float('nan')):.3f} inter={r['intermediate']}")

# distribution of alpha across all corridors
al = np.array([r["alpha"] for r in C])
print("\n=== ALPHA DISTRIBUTION ===")
print(f"n={len(al)} mean={al.mean():.3f} median={np.median(al):.3f}")
print(f"  alpha in (0,1) [strictly between]: {int(((al>0)&(al<1)).sum())}")
print(f"  alpha in (0.05,0.95): {int(((al>0.05)&(al<0.95)).sum())}")
print(f"  alpha <= 0 (at/below origin, no host pull): {int((al<=0).sum())}")
print(f"  alpha >= 1 (at/beyond host): {int((al>=1).sum())}")
# residual distribution
res = np.array([r["resid_offline"] for r in C])
print(f"  resid offline: mean={res.mean():.2f} median={np.median(res):.2f} (>1 = far off the O->H line)")
# gradient r distribution
gr = np.array([ (r["gradient"] or {}).get("r",np.nan) for r in C], float)
gr = gr[~np.isnan(gr)]
print(f"\n=== WITHIN-CORRIDOR GRADIENT r (position vs host_frac), n={len(gr)} ===")
print(f"  mean r={gr.mean():.3f} median={np.median(gr):.3f}  positive: {int((gr>0).sum())}  |r|>0.2: {int((np.abs(gr)>0.2).sum())}")
# how many corridors have CI excluding 0 and 1 (significantly intermediate)
sig_inter = [r for r in C if r["alpha_ci"][0]>0.05 and r["alpha_ci"][1]<0.95]
print(f"\ncorridors with 95% CI strictly inside (0.05,0.95) [SIGNIFICANTLY intermediate]: {len(sig_inter)}")
for r in sorted(sig_inter,key=lambda x:-x['nD'])[:20]:
    ci=r['alpha_ci']
    print(f"  {r['origin']}->{r['host']:3s} nD={r['nD']:4d} alpha={r['alpha']:.2f} ci=[{ci[0]:.2f},{ci[1]:.2f}]")
