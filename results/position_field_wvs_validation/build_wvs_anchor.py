#!/usr/bin/env python3
"""Build the WVS Wave 7 country level opinion anchor for the position field validation.

Source: World Values Survey Wave 7 (2017-2022) respondent level data, obtained
machine readable and login free from the HuggingFace mirror
`oxford-llms/world_values_survey_2017_2022_sft` (a faithful SFT repackaging of the
official WVS7 cross national file: each row carries one held out WVS item with the
respondent's true coded answer and a respondent id whose leading digits are the ISO
numeric country code). No OCR. No survey download form.

For five contestable topics we map the raw answer to a numeric scale, drop the non
substantive codes (Don't know / No answer / Missing), and take the country mean over
respondents. Countries with fewer than MIN_N substantive responses on an item are
dropped as unreliable.

Output: the internal corpus store/wvs_position/wvs_country_items.csv (long) plus a
wide pivot, on the internal store (persistent).
"""
import os, re, pandas as pd

SRC = "/tmp"  # wvs_train.parquet + wvs_test.parquet staged here
OUT = "the internal corpus store/wvs_position"
MIN_N = 15
os.makedirs(OUT, exist_ok=True)

# ISO numeric -> (country name, GDELT FIPS 10-4 code used by the DOC API sourcecountry op)
ISO = {
 20:("Andorra","AN"),32:("Argentina","AR"),36:("Australia","AS"),50:("Bangladesh","BG"),
 51:("Armenia","AM"),68:("Bolivia","BL"),76:("Brazil","BR"),104:("Myanmar","BM"),
 124:("Canada","CA"),152:("Chile","CI"),156:("China","CH"),158:("Taiwan","TW"),
 170:("Colombia","CO"),196:("Cyprus","CY"),203:("Czechia","EZ"),218:("Ecuador","EC"),
 231:("Ethiopia","ET"),276:("Germany","GM"),300:("Greece","GR"),320:("Guatemala","GT"),
 344:("Hong Kong","HK"),356:("India","IN"),360:("Indonesia","ID"),364:("Iran","IR"),
 368:("Iraq","IZ"),392:("Japan","JA"),398:("Kazakhstan","KZ"),400:("Jordan","JO"),
 404:("Kenya","KE"),410:("South Korea","KS"),417:("Kyrgyzstan","KG"),422:("Lebanon","LE"),
 434:("Libya","LY"),446:("Macau","MC"),458:("Malaysia","MY"),462:("Maldives","MV"),
 484:("Mexico","MX"),496:("Mongolia","MG"),504:("Morocco","MO"),528:("Netherlands","NL"),
 554:("New Zealand","NZ"),558:("Nicaragua","NU"),566:("Nigeria","NI"),586:("Pakistan","PK"),
 604:("Peru","PE"),608:("Philippines","RP"),630:("Puerto Rico","RQ"),642:("Romania","RO"),
 643:("Russia","RS"),688:("Serbia","RI"),702:("Singapore","SN"),703:("Slovakia","LO"),
 704:("Vietnam","VM"),716:("Zimbabwe","ZI"),762:("Tajikistan","TI"),764:("Thailand","TH"),
 788:("Tunisia","TS"),792:("Turkey","TU"),804:("Ukraine","UP"),818:("Egypt","EG"),
 826:("Great Britain","UK"),840:("United States","US"),858:("Uruguay","UY"),
 860:("Uzbekistan","UZ"),862:("Venezuela","VE"),909:("Northern Ireland",None),  # part of UK, cannot be split in GDELT
}

# Each item: substring key that must appear (lowercased) in the WVS question text,
# and an answer->numeric map. Numeric string answers ("5","8") pass through for 1-10 scales.
ITEMS = {
 "immigration_restrictiveness": dict(
    key="which one of the following do you think the government should do",
    scale={"let anyone come who wants to":1,
           "let people come as long as there are jobs available":2,
           "place strict limits on the number of foreigners who can come here":3,
           "prohibit people coming here from other countries":4},
    higher="more restrictive on immigration"),
 "religiosity_importance_of_god": dict(
    key="how important is god in your life",
    scale={"very important":10,"not at all important":1}, numeric10=True,
    higher="more religious"),
 "democracy_importance": dict(
    key="how important is it for you to live in a country that is governed democratically",
    scale={"absolutely important":10,"not at all important":1}, numeric10=True,
    higher="more pro democracy"),
 "confidence_in_government": dict(
    key="how much confidence do you have in the government",
    scale={"a great deal":4,"quite a lot":3,"not very much":2,"none at all":1},
    higher="more trust in government"),
 "gender_men_better_leaders": dict(
    key="men make better political leaders than women do",
    scale={"agree strongly":4,"agree":3,"disagree":2,"strongly disagree":1},
    higher="more traditional gender attitudes"),
}

def qstem(s):
    # The held out WVS item always sits at the end, after a marker. Two phrasings occur:
    #   "... Question: <item>"  and  "... please answer the following question: <item>".
    # Both end in "question:", so splitting on the last case insensitive "question:" works.
    ql = s.lower()
    i = ql.rfind("question:")
    return s[i+len("question:"):].strip() if i >= 0 else ""

def to_num(ans, spec):
    a = str(ans).strip()
    al = a.lower()
    if al in spec["scale"]:
        return spec["scale"][al]
    if spec.get("numeric10"):
        # pure integer answers 1..10
        if re.fullmatch(r"\d+", a):
            v = int(a)
            return v if 1 <= v <= 10 else None
    return None

def main():
    t = pd.read_parquet(f"{SRC}/wvs_train.parquet")
    e = pd.read_parquet(f"{SRC}/wvs_test.parquet")
    df = pd.concat([t, e], ignore_index=True)
    df["q"] = df["question"].map(qstem)
    df["ql"] = df["q"].str.lower()
    df["cc"] = df["id"] // 1000000

    rows = []
    for item, spec in ITEMS.items():
        sub = df[df["ql"].str.contains(re.escape(spec["key"]), na=False)].copy()
        # guard: gender key 'agree'/'disagree' scale also needs its own item only
        sub["val"] = sub["answer"].map(lambda a: to_num(a, spec))
        sub = sub.dropna(subset=["val"])
        matched_q = sub["q"].value_counts().index.tolist()
        print(f"[{item}] matched {len(matched_q)} question string(s); {len(sub)} scored responses")
        for q in matched_q[:3]:
            print(f"    <- {q[:110]}")
        g = sub.groupby("cc")["val"].agg(["mean", "count"]).reset_index()
        g = g[g["count"] >= MIN_N]
        for _, r in g.iterrows():
            cc = int(r["cc"])
            if cc not in ISO:
                continue
            name, fips = ISO[cc]
            rows.append(dict(item=item, iso_num=cc, country=name, fips=fips,
                             wvs_mean=round(r["mean"], 4), wvs_n=int(r["count"]),
                             higher_means=spec["higher"]))

    out = pd.DataFrame(rows)
    long_p = f"{OUT}/wvs_country_items.csv"
    out.to_csv(long_p, index=False)
    print("wrote", long_p, out.shape)
    if out.empty:
        print("NO ROWS survived MIN_N; nothing to pivot"); return
    print("per country n: median=%.0f min=%d max=%d" % (
        out["wvs_n"].median(), out["wvs_n"].min(), out["wvs_n"].max()))

    wide = out.pivot_table(index=["iso_num", "country", "fips"], columns="item",
                           values="wvs_mean").reset_index()
    wide_p = f"{OUT}/wvs_country_wide.csv"
    wide.to_csv(wide_p, index=False)
    print("wrote", wide_p, wide.shape)
    print("\ncountries per item:")
    print(out.groupby("item")["iso_num"].nunique())

if __name__ == "__main__":
    main()
