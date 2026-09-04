#!/usr/bin/env python3
"""eval_truthometer.py — held-out precision/recall/F1 evaluation of the
truthometer register-anchored FACT verifier against independent ground truth.

Ground truth used (independent of the truthometer):
  1. an internal table  (66,957) — gold claim-TYPE labels (klass): whether a
     claim is a VERIFIABLE_FACT / EMPIRICAL / OPINION / PUFFERY / SUPERLATIVE / TRIVIAL.
     Drives the COVERAGE / verifiability-gate evaluation.
  2. an internal table  (92,357) — ClaimReview / PolitiFact gold verdicts
     (rating). The public fact-check corpus (LIAR-family). Coverage stress test.
  3. an internal table (5.70M live) + an internal table (1.90M) — Companies House,
     the INDEPENDENT register that is the gold truth for the register-checkable slice.

Three legs, reported separately (coverage is NOT folded into accuracy):
  LEG A  Coverage / applicability of the register verifier over the public
         fact-check corpora — the honest bound on what it can verify at all.
  LEG B  Verifiability gate as a classifier (register-checkable vs abstain):
         precision / recall / F1 with confusion matrix.
  LEG C  Verdict accuracy on the register-checkable slice (recog_web_uk_verdict),
         held-out sample, vs a fresh authoritative Companies House re-check:
         confusion matrix + per-class precision/recall/F1 + the honest accusatory
         (NONEXISTENT-as-fraud) precision caveat + the bridge floor.
"""
import os, re, json, hashlib, random
import psycopg2

PW = [l.split("=", 1)[1].strip().strip('"').strip("'")
      for l in open(os.path.expanduser("~/.kronaxis/env")) if l.startswith("TFS_DB_PASSWORD=")][0]
DSN = f"host=127.0.0.1 port=5432 user=titan password={PW} dbname=tfs"
random.seed(20260830)

# ---------------------------------------------------------------------------
# minimal checksum validators (ported from truthometer/checks/checks.go)
# ---------------------------------------------------------------------------
def _digits(s): return s.isdigit() and len(s) > 0
def luhn(s):
    if not _digits(s) or len(s) < 2: return False
    tot, dbl = 0, False
    for ch in reversed(s):
        d = int(ch)
        if dbl:
            d *= 2
            if d > 9: d -= 9
        tot += d; dbl = not dbl
    return tot % 10 == 0
def mod9710(s):
    rem = 0
    for ch in s:
        if ch.isdigit(): rem = (rem*10 + int(ch)) % 97
        elif 'A' <= ch <= 'Z': rem = (rem*100 + (ord(ch)-55)) % 97
        else: return -1
    return rem
def valid_lei(s):
    s = re.sub(r'[^0-9A-Za-z]', '', s).upper()
    return len(s) == 20 and mod9710(s) == 1
def valid_iban(s):
    s = re.sub(r'[^0-9A-Za-z]', '', s).upper()
    if not (15 <= len(s) <= 34): return False
    if not (s[0].isalpha() and s[1].isalpha()): return False
    return mod9710(s[4:] + s[:4]) == 1
def valid_vat_gb(s):
    s = re.sub(r'[^0-9]', '', s)
    if len(s) == 12: s = s[:9]
    if len(s) != 9: return False
    d = [int(c) for c in s]
    w = [8,7,6,5,4,3,2]
    tot = sum(d[i]*w[i] for i in range(7))
    chk = d[7]*10 + d[8]
    return (tot+chk) % 97 == 0 or (tot+chk+55) % 97 == 0

# UK company number: 8 digits, or 2-letter prefix + 6 digits. Range guard mirrors
# run_verdict.sql (drop 8-digit >= 17,000,000 as extraction noise).
CH_PREFIX = r'(?:SC|NI|OC|SO|NC|FC|GE|GN|GS|IC|IP|LP|NA|NL|NO|NP|NR|NZ|RC|SA|SF|SI|SL|SP|SR|SZ|ZC)'
def ch_number_form(tok):
    tok = tok.upper()
    if re.fullmatch(CH_PREFIX + r'\d{6}', tok): return True
    if re.fullmatch(r'\d{8}', tok):
        return not (17_000_000 <= int(tok) <= 99_999_999)
    if re.fullmatch(r'\d{6,7}', tok):   # legacy short numbers, zero-padded to 8
        return True
    return False

# context words that make a bare number a *register* claim (not any integer)
RE_CONO = re.compile(
    r'(?:compan(?:y|ies)\s*(?:house)?\s*(?:reg(?:istration|istered)?\.?\s*)?(?:number|no\.?|#)?'
    r'|registered\s+(?:number|no\.?|in\s+england)'
    r'|reg\.?\s*(?:no\.?|number))\s*[:#.\-]?\s*(' + CH_PREFIX + r'?\d{6,8})\b', re.I)
RE_VAT = re.compile(r'\bVAT\s*(?:reg(?:istration)?\.?\s*)?(?:number|no\.?|#)?\s*[:#.\-]?\s*((?:GB)?\s?\d[\d\s]{7,13})', re.I)
RE_LEI = re.compile(r'\b(?:LEI|legal\s+entity\s+identifier)\b[:#.\-\s]*([0-9A-Z]{20})\b', re.I)
RE_IBAN = re.compile(r'\b([A-Z]{2}\d{2}[0-9A-Z]{11,30})\b')
# a founded/incorporated date claim tied to an entity is register-settleable IF a
# company can be bridged; treat as *weakly* attemptable (structured, entity-dependent)
RE_FOUNDED = re.compile(r'\b(?:founded|established|incorporated|since|est\.?)\b[^.]{0,30}\b(1[89]\d{2}|20[0-2]\d)\b', re.I)

def register_checkable(text):
    """Independent scope decision: does this claim assert a public-register key
    the truthometer can settle? Returns (attemptable_bool, keytype_or_None)."""
    if not text: return (False, None)
    m = RE_CONO.search(text)
    if m and ch_number_form(re.sub(r'\s', '', m.group(1))):
        return (True, "company_number")
    m = RE_VAT.search(text)
    if m and valid_vat_gb(m.group(1)):
        return (True, "vat")
    m = RE_LEI.search(text)
    if m and valid_lei(m.group(1)):
        return (True, "lei")
    for m in RE_IBAN.finditer(text):
        if valid_iban(m.group(1)):
            return (True, "iban")
    return (False, None)

def held_out(key, frac_bucket=0):
    """Deterministic 20% held-out split by stable hash (bucket 0 of 5)."""
    h = int(hashlib.sha256(key.encode()).hexdigest(), 16)
    return h % 5 == frac_bucket

# ---------------------------------------------------------------------------
db = psycopg2.connect(DSN)
db.set_session(readonly=True)
cur = db.cursor()
OUT = {}

# === LEG A: coverage / applicability over the public fact-check corpora ======
print("LEG A: coverage over public fact-check corpora ...", flush=True)
def coverage(table, textcol, extracols=""):
    cur.execute(f"SELECT {textcol}{(','+extracols) if extracols else ''} FROM the internal schema.{table}")
    rows = cur.fetchall()
    n = len(rows); att = 0; bykey = {}
    tagged = []
    for r in rows:
        ok, kt = register_checkable(r[0] or "")
        if ok:
            att += 1; bykey[kt] = bykey.get(kt, 0) + 1
            tagged.append(r)
    return n, att, bykey, tagged

n_cl, att_cl, key_cl, _ = coverage("claim_label_train", "claim_text")
n_cr, att_cr, key_cr, tagged_cr = coverage("claimreview_claim", "claim_text", "rating")
OUT["legA"] = {
    "claim_label_train": {"n": n_cl, "attemptable": att_cl, "coverage": att_cl/n_cl, "by_key": key_cl},
    "claimreview_claim": {"n": n_cr, "attemptable": att_cr, "coverage": att_cr/n_cr, "by_key": key_cr},
}
print(f"  claim_label_train: {att_cl}/{n_cl} = {att_cl/n_cl:.4%} register-checkable", flush=True)
print(f"  claimreview_claim: {att_cr}/{n_cr} = {att_cr/n_cr:.4%} register-checkable", flush=True)

# coverage by gold klass (claim_label_train): how does the gate treat each type?
cur.execute("SELECT klass, claim_text FROM an internal table")
byklass = {}
for klass, text in cur.fetchall():
    k = (klass or "").strip()
    ok, _ = register_checkable(text or "")
    d = byklass.setdefault(k, [0, 0]); d[0] += 1; d[1] += 1 if ok else 0
OUT["legA"]["by_gold_klass"] = {k: {"n": v[0], "attemptable": v[1]} for k, v in sorted(byklass.items(), key=lambda x:-x[1][0])}

# === LEG B: verifiability gate as a classifier ===============================
# Positive class = register-checkable. Gold positives are hard to get from the
# political corpora (they contain ~none), so the POSITIVE test set is the deployed
# verifier's own claims (recog_web_uk_verdict: every row IS a stated register key)
# and the NEGATIVE test set is the public fact-check corpora. The gate must accept
# the register keys (recall) and abstain on the political claims (specificity).
print("LEG B: verifiability gate classifier ...", flush=True)
# positives: reconstruct the natural-language claim the site made and re-detect.
cur.execute("SELECT pld, key_type, stated FROM an internal table WHERE key_type='company_number'")
pos = cur.fetchall()
tp = fn = 0
for pld, kt, stated in pos:
    claim = f"{pld} — Company registration number {stated}."
    ok, _ = register_checkable(claim)
    if ok: tp += 1
    else: fn += 1
# negatives: the two fact-check corpora (gold = not a register claim). We already
# have attemptable counts: those flagged are false positives.
fp = att_cl + att_cr
tn = (n_cl + n_cr) - fp
prec = tp / (tp + fp) if (tp+fp) else 0.0
rec = tp / (tp + fn) if (tp+fn) else 0.0
f1 = 2*prec*rec/(prec+rec) if (prec+rec) else 0.0
OUT["legB"] = {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
               "precision": prec, "recall": rec, "f1": f1,
               "specificity": tn/(tn+fp) if (tn+fp) else 0.0,
               "note": "positives = deployed register-key claims; negatives = public fact-check corpora"}
print(f"  gate P={prec:.4f} R={rec:.4f} F1={f1:.4f}  (TP={tp} FP={fp} FN={fn} TN={tn})", flush=True)

# false-positive audit: which political claims did the gate wrongly flag?
fp_samples = []
for r in tagged_cr[:20]:
    fp_samples.append({"rating": r[1], "text": (r[0] or "")[:160]})
OUT["legB"]["false_positive_samples"] = fp_samples

# === LEG C: verdict accuracy on the register-checkable slice vs CH ============
print("LEG C: verdict accuracy vs Companies House (held-out) ...", flush=True)
cur.execute("SELECT pld, stated, outcome, register_entry FROM an internal table WHERE key_type='company_number'")
allrows = cur.fetchall()
ho = [r for r in allrows if held_out(f"{r[0]}|{r[1]}")]
OUT["legC"] = {"total_company_number_verdicts": len(allrows), "held_out_n": len(ho)}

# fresh authoritative re-check of every held-out stated number
nums = sorted({r[1] for r in ho})
live, diss = set(), set()
CHUNK = 5000
for i in range(0, len(nums), CHUNK):
    batch = nums[i:i+CHUNK]
    cur.execute("SELECT company_number FROM an internal table WHERE company_number = ANY(%s)", (batch,))
    live.update(x[0] for x in cur.fetchall())
    cur.execute("SELECT company_number FROM an internal table WHERE company_number = ANY(%s)", (batch,))
    diss.update(x[0] for x in cur.fetchall())

def fresh(num):
    if num in live: return "MATCH"
    if num in diss: return "DISSOLVED"
    return "NONEXISTENT"

# confusion matrix: truthometer outcome (rows) vs fresh CH re-check (cols)
labels = ["MATCH", "DISSOLVED", "NONEXISTENT"]
cm = {a: {b: 0 for b in labels} for a in labels}
for pld, stated, outcome, name in ho:
    o = outcome if outcome in labels else "NONEXISTENT"
    cm[o][fresh(stated)] += 1
OUT["legC"]["confusion_matrix_verdict_vs_freshCH"] = cm
# per-class P/R/F1 (agreement between deployed verdict and a fresh authoritative check)
perclass = {}
for lab in labels:
    tp_ = cm[lab][lab]
    fp_ = sum(cm[lab][c] for c in labels if c != lab)
    fn_ = sum(cm[o][lab] for o in labels if o != lab)
    p = tp_/(tp_+fp_) if (tp_+fp_) else 0.0
    r = tp_/(tp_+fn_) if (tp_+fn_) else 0.0
    perclass[lab] = {"precision": p, "recall": r,
                     "f1": 2*p*r/(p+r) if (p+r) else 0.0, "support": tp_+fn_}
OUT["legC"]["per_class"] = perclass
overall_agree = sum(cm[l][l] for l in labels) / max(1, len(ho))
OUT["legC"]["overall_agreement"] = overall_agree
print(f"  register-join agreement (held-out) = {overall_agree:.4%} over {len(ho)} verdicts", flush=True)

# --- bridge floor: does a MATCH mean the SITE owns the number? name overlap ---
# KEY_RESOLVES does not claim ownership; this measures how often it would be WRONG
# if (mis)read as ownership — the honest bridge ceiling.
def dom_tokens(pld):
    core = re.sub(r'\.(co\.uk|org\.uk|ltd\.uk|uk|com|co|net|org|io|digital)$', '', pld.lower())
    return set(re.findall(r'[a-z]{3,}', core))
STOP = {"ltd","limited","the","and","llp","plc","company","co","uk","group","holdings","services","holdco"}
def name_tokens(nm):
    return {t for t in re.findall(r'[a-z]{3,}', (nm or "").lower()) if t not in STOP}
match_rows = [r for r in ho if r[2] == "MATCH" and r[3]]
own_hit = 0
for pld, stated, outcome, name in match_rows:
    dt, nt = dom_tokens(pld), name_tokens(name)
    if dt & nt: own_hit += 1
OUT["legC"]["bridge_floor"] = {
    "match_with_name_n": len(match_rows),
    "domain_name_token_overlap": own_hit,
    "ownership_consistent_rate": own_hit/len(match_rows) if match_rows else 0.0,
    "note": "proxy: fraction of MATCH where the domain shares a token with the CH registered name. KEY_RESOLVES does NOT assert ownership; this is the ceiling if it were (mis)read as ownership."}
print(f"  bridge floor: {own_hit}/{len(match_rows)} MATCH have domain~name token overlap = {own_hit/max(1,len(match_rows)):.2%}", flush=True)

# --- accusatory (NONEXISTENT) precision: is absence evidence of fabrication? ---
# The design abstains on UNcorroborated mismatches. Measure how many NONEXISTENT
# have independent name corroboration (stated_identity_v2) that they are genuine.
ne_rows = [r for r in ho if r[2] == "NONEXISTENT"]
OUT["legC"]["accusatory"] = {"nonexistent_held_out": len(ne_rows)}
try:
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='the internal schema' AND table_name='stated_identity_v2'")
    si_cols = [c[0] for c in cur.fetchall()]
    OUT["legC"]["accusatory"]["stated_identity_v2_cols"] = si_cols
    # tier distribution overall (context on how rare a corroborated nonexistent is)
    if "tier" in si_cols:
        cur.execute("SELECT tier, count(*) FROM an internal table GROUP BY tier ORDER BY 2 DESC")
        OUT["legC"]["accusatory"]["stated_identity_v2_tiers"] = dict(cur.fetchall())
except Exception as e:
    OUT["legC"]["accusatory"]["stated_identity_v2_error"] = str(e)

print(json.dumps(OUT, indent=2, default=str))
db.close()
