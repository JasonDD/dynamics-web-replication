#!/usr/bin/env python3
"""parse_dnm_forum.py — extract role labelled posts from a Gwern DNM forum tarball (SMF software).

Structural ROLE, never content derived: the label is the forum assigned membergroup/postgroup badge
shown beside each post. ENABLER = Vendor / Administrator / (Global) Moderator. USER = ordinary rank
(User, Newbie, Jr./Full/Sr. Member, Hero Member). Posts are deduped by SMF message id across the weekly
snapshots (the archive holds many dated mirrors of the same board), keeping the longest body seen.

Output: JSONL of {id, text, role, subgroup, user_id, username, topic_id, forum, nchars} for the 8 axis
scorer. No operational content is retained beyond what the character scorer needs; this file is a design
and measurement artefact, not a mirror of the market.

Usage: python3 parse_dnm_forum.py <extracted_forum_root> <forum_name> <out.jsonl> [min_chars=120]
"""
import sys, os, re, json, glob
from bs4 import BeautifulSoup

ROOT = sys.argv[1]
FORUM = sys.argv[2]
OUT = sys.argv[3]
MIN_CHARS = int(sys.argv[4]) if len(sys.argv) > 4 else 120

ENABLER_GROUPS = {"vendor", "administrator", "admin", "global moderator", "moderator"}
USER_GROUPS = {"user", "newbie", "jr. member", "full member", "sr. member", "hero member", "member"}

def subgroup(g):
    if g == "vendor":
        return "vendor"
    if g in ("administrator", "admin", "global moderator", "moderator"):
        return "staff"
    return "user"

topic_re = re.compile(r"index\.php\?topic=(\d+)")
uid_re = re.compile(r"action=profile;u=(\d+)")

def main():
    files = glob.glob(os.path.join(ROOT, "**", "index.php?topic=*"), recursive=True)
    print(f"topic files: {len(files)}", flush=True)
    counts = {"ENABLER": 0, "USER": 0, "short": 0}
    # dedupe by SMF message id across weekly snapshots, keep the longest body seen
    best = {}
    for i, path in enumerate(sorted(files)):
        parse_into(path, best, counts)
        if (i + 1) % 1000 == 0:
            print(f"  {i+1}/{len(files)} files, {len(best)} unique posts", flush=True)
    with open(OUT, "w") as f:
        for rec in best.values():
            f.write(json.dumps(rec) + "\n")
    en = sum(1 for r in best.values() if r["role"] == "ENABLER")
    us = sum(1 for r in best.values() if r["role"] == "USER")
    ven = sum(1 for r in best.values() if r["subgroup"] == "vendor")
    stf = sum(1 for r in best.values() if r["subgroup"] == "staff")
    print(f"UNIQUE scored-eligible posts: {len(best)} | ENABLER {en} (vendor {ven}, staff {stf}) | USER {us} | short-skipped {counts['short']}", flush=True)

def parse_into(path, best, counts):
    m = topic_re.search(os.path.basename(path))
    if not m:
        return
    topic_id = m.group(1)
    try:
        html = open(path, encoding="utf-8", errors="ignore").read()
    except Exception:
        return
    if "class=\"poster" not in html:  # loose: abraxas theme uses class="poster col-md-2"
        return
    soup = BeautifulSoup(html, "lxml")
    for wrap in soup.select("div.post_wrapper"):
        poster = wrap.select_one("div.poster")
        inner = wrap.select_one("div.post div.inner")
        if not poster or not inner or not inner.get("id"):
            continue
        mid = inner.get("id").replace("msg_", "")
        if not mid.isdigit():
            continue
        # The group badge sits in different SMF theme markup per forum: default theme uses
        # li.membergroup (primary role group: Vendor/Administrator/Global Moderator) plus li.postgroup
        # (post-count title: Newbie/Jr. Member). The Reseller theme (abraxas) renders the group in
        # li.blurb > strong instead. Collect every candidate and label ENABLER if ANY is a staff or
        # vendor group, so a moderator whose post-count title is "Jr. Member" is not miscounted.
        cands = []
        for sel in ("li.membergroup", "li.postgroup", "li.blurb"):
            el = poster.select_one(sel)
            if el:
                cands.append(el.get_text(strip=True).lower())
        en_hit = [g for g in cands if g in ENABLER_GROUPS]
        us_hit = [g for g in cands if g in USER_GROUPS]
        if en_hit:
            role = "ENABLER"; group = en_hit[0]
        elif us_hit:
            role = "USER"; group = us_hit[0]
        else:
            continue
        a = poster.select_one("h4 a[href*='action=profile']")
        uid_m = uid_re.search(a["href"]) if a and a.has_attr("href") else None
        if not uid_m:
            continue
        user_id = uid_m.group(1)
        username = a.get_text(strip=True) if a else None
        for q in inner.select("div.quote, div.quoteheader, div.code, blockquote"):
            q.decompose()
        text = re.sub(r"\s+", " ", inner.get_text(" ", strip=True)).strip()
        n = len(text)
        prev = best.get(mid)
        if prev is not None and prev["nchars"] >= n:
            continue
        if n < MIN_CHARS:
            counts["short"] += 1
            if prev is None:
                continue
        best[mid] = {"id": f"{FORUM}:{mid}", "text": text, "role": role, "subgroup": subgroup(group),
                     "user_id": f"{FORUM}:{user_id}", "username": username, "topic_id": topic_id,
                     "forum": FORUM, "nchars": n}

if __name__ == "__main__":
    main()
