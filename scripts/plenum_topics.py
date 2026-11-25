"""Map of economic-policy debates in the Bundestag, 1949-2026, and their relation to unemployment and inflation.

Corpus: CPP-BT (Fobbe 2026), all plenary records (data/raw/cppbt, not checked in). Text lower-cased, line-end
hyphenation removed. Hits per million words per year for the topic dictionaries in TOPICS. Kündigungsschutz
hits within 100 characters of tenancy vocabulary are dropped. Precision of the dictionaries is not yet
hand-validated except for unemployment, labour reform and location (results/plenum_kwic_precision.md).

Outputs:
- results/plenum_topics.csv: hits per million words, topic x year
- results/plenum_topics.md: levels in selected years; correlation of each topic with the registered unemployment
  rate and CPI inflation, 1950-2025 and 1950-2002 vs 2003-2025; topic shares in downturns

Run from repository root:  python3 scripts/plenum_topics.py   (about 10 minutes on 4 cores)
"""
import glob
import os
import re
import sys
from multiprocessing import Pool

import pandas as pd

sys.path.insert(0, "scripts")
RAW = "data/raw/cppbt"
TENANCY = re.compile(r"miet|wohnraum|vermiet|wohnung")

TOPICS = {
    # economy as outcome
    "unemployment": r"\b(?:massen|langzeit|jugend)?(?:arbeitslos(?:igkeit|e|en|er|enzahl\w*|enquote\w*)|erwerbslos(?:igkeit|e|en))\b(?!-)",
    "inflation": r"\b(?:inflation\w*|preissteigerung\w*|geldentwertung\w*|teuerung\w*|preisstabilität\w*|preisniveaustabilität\w*)",
    "public_debt": r"\b(?:staatsverschuldung\w*|neuverschuldung\w*|schuldenbremse\w*|staatsschulden\w*|haushaltskonsolidierung\w*)",
    "growth": r"\b(?:wirtschaftswachstum\w*|wachstumsschwäche\w*|rezession\w*|konjunkturprogramm\w*|konjunkturpaket\w*)",
    "energy_prices": r"\b(?:energiepreis\w*|strompreis\w*|gaspreis\w*|ölpreis\w*|energiekosten\w*|industriestrompreis\w*)",
    "skills_shortage": r"\b(?:fachkräftemangel\w*|arbeitskräftemangel\w*|fachkräftesicherung\w*|fachkräfteengpass\w*)",
    # supply-side and location agenda
    "location": r"\b(?:standort deutschland|wirtschaftsstandort\w*|standortsicherung\w*|deindustrialisierung\w*|wirtschaftswende)",
    "competitiveness": r"\bwettbewerbsfähigkeit\w*",
    "bureaucracy": r"\b(?:bürokratieabbau\w*|entbürokratisierung\w*|bürokratiekosten\w*|bürokratieentlastung\w*)",
    # labour against capital
    "strikes": r"\b(?:streik(?:s|en|recht\w*|welle\w*)?|warnstreik\w*|generalstreik\w*|arbeitskampf\w*|aussperrung\w*)\b",
    "codetermination": r"\b(?:mitbestimmung\w*|betriebsverfassung\w*|betriebsr(?:a|ä)t\w*)",
    "collective_bargaining": r"\b(?:tarifautonomie\w*|tarifbindung\w*|tarifflucht\w*|flächentarif\w*|tarifvertr(?:a|ä)g\w*|tariftreue\w*)",
    "wages": r"\b(?:mindestlohn\w*|lohnzurückhaltung\w*|lohnstückkosten\w*|lohnnebenkosten\w*|lohnpolitik\w*)",
    "working_time": r"\b(?:arbeitszeitverkürzung\w*|35-stunden-woche\w*|wochenarbeitszeit\w*|arbeitszeitgesetz\w*|höchstarbeitszeit\w*)",
    "worker_protection": r"\b(?:kündigungsschutz\w*|lohnfortzahlung\w*|entgeltfortzahlung\w*|befristung\w*|leiharbeit\w*|zeitarbeit\w*)",
    # buffers
    "short_time_work": r"\b(?:kurzarbeit\w*)",
    "early_retirement": r"\b(?:vorruhestand\w*|frühverrentung\w*|altersteilzeit\w*)",
    # frame
    "social_market_economy": r"\bsoziale(?:n|r)? marktwirtschaft",
    "social_justice": r"\b(?:soziale(?:n|r)? gerechtigkeit|verteilungsgerechtigkeit|umverteilung\w*)",
}
GROUPS = {
    "Economy as outcome": ["unemployment", "inflation", "public_debt", "growth", "energy_prices", "skills_shortage"],
    "Supply side and location": ["location", "competitiveness", "bureaucracy"],
    "Labour against capital": ["strikes", "codetermination", "collective_bargaining", "wages", "working_time", "worker_protection"],
    "Buffers": ["short_time_work", "early_retirement"],
    "Frame": ["social_market_economy", "social_justice"],
}
PATS = {k: re.compile(v) for k, v in TOPICS.items()}


def one(f):
    m = re.search(r"Plenarprotokoll_(\d{2})_(\d{3})_(\d{4})-", os.path.basename(f))
    t = re.sub(r"-\n", "", open(f, encoding="utf-8", errors="ignore").read().lower())
    r = {"year": int(m.group(3)), "words": len(t.split())}
    for k, p in PATS.items():
        n = 0
        for h in p.finditer(t):
            if h.group(0).startswith("kündigungsschutz") and TENANCY.search(t[max(0, h.start() - 100): h.end() + 100]):
                continue
            n += 1
        r[k] = n
    return r


def counts():
    cache = f"{RAW}/topic_counts.csv"
    if os.path.exists(cache):
        return pd.read_csv(cache)
    files = sorted(glob.glob(f"{RAW}/txt/files/txt_protokoll-gesamt/*.txt"))
    with Pool(4) as pool:
        rows = pool.map(one, files, chunksize=20)
    d = pd.DataFrame(rows)
    d.to_csv(cache, index=False)
    return d


def main():
    import okun_gap as og
    d = counts()
    y = d.groupby("year").sum()
    pm = (1e6 * y[list(TOPICS)].div(y.words, axis=0)).round(1)
    pm.to_csv("results/plenum_topics.csv")
    dep, _ = og.ba_rates()
    infl = pd.read_csv("../macro/data/static/preisrede_inflation.csv").set_index("jahr").vpi_rate
    x = pm[(pm.index >= 1950) & (pm.index <= 2025)].copy()
    x["u"] = [dep.get(i) for i in x.index]
    x["infl"] = [infl.get(i) for i in x.index]
    L = ["# Economic-policy debates in the Bundestag, 1949-2026 (hits per million words)", "",
         "Source: CPP-BT (Fobbe 2026); own dictionaries (scripts/plenum_topics.py). 2026 runs to 19 September.", "",
         "## Levels in selected years", ""]
    yrs = [1955, 1967, 1975, 1983, 1993, 1997, 2003, 2005, 2009, 2015, 2019, 2022, 2023, 2024, 2025]
    L += ["| Topic | " + " | ".join(map(str, yrs)) + " |", "|---|" + "---|" * len(yrs)]
    for g, ks in GROUPS.items():
        L.append(f"| **{g}** |" + " |" * len(yrs))
        for k in ks:
            L.append(f"| {k} | " + " | ".join(f"{pm.loc[v, k]:.0f}" for v in yrs) + " |")
    L += ["", "## Correlation with the registered unemployment rate and CPI inflation (annual levels)", "",
          "| Topic | r with unemployment 1950-2025 | 1950-2002 | 2003-2025 | r with inflation 1950-2025 |", "|---|---|---|---|---|"]
    a, b = x[x.index <= 2002], x[x.index >= 2003]
    for k in TOPICS:
        L.append(f"| {k} | {x[k].corr(x.u):+.2f} | {a[k].corr(a.u):+.2f} | {b[k].corr(b.u):+.2f} | {x[k].corr(x.infl):+.2f} |")
    L += ["", "## Group totals by decade (mean hits per million words)", ""]
    dec = pm.copy()
    for g, ks in GROUPS.items():
        dec[g] = pm[ks].sum(axis=1)
    dec["decade"] = (dec.index // 10) * 10
    t = dec.groupby("decade")[list(GROUPS)].mean().round(0)
    L += ["| Decade | " + " | ".join(GROUPS) + " |", "|---|" + "---|" * len(GROUPS)]
    L += [f"| {i}s | " + " | ".join(f"{t.loc[i, g]:.0f}" for g in GROUPS) + " |" for i in t.index]
    open("results/plenum_topics.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
