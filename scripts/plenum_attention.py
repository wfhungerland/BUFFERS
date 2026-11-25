"""Parliamentary attention to unemployment and to reform pressure, per year and per recession episode.

Corpus: Corpus der Plenarprotokolle des Deutschen Bundestages (CPP-BT), Seán Fobbe, version 2026-09-19,
DOI 10.5281/zenodo.22844952, CC0. All plenary records 1949 to 19 September 2026 (TXT data set and
protocol metadata, in data/raw/cppbt/, not checked in).

Word fields (counted on lower-cased text, hits per million words):
- U  unemployment as a problem: Arbeitslosigkeit, Arbeitslose(n), Arbeitslosenzahl, Arbeitslosenquote,
     Massen-, Langzeit-, Jugendarbeitslosigkeit, Erwerbslosigkeit. Benefit names (Arbeitslosengeld, -hilfe,
     -versicherung) are excluded so that the Hartz renaming does not move the series.
- R  structural reform: Strukturreform, Reformstau, Arbeitsmarktreform, Sozialreform, Agenda 2010,
     Kündigungsschutz, Lohnnebenkosten, Flexibilisierung, Deregulierung.
- S  competitiveness and location: Standort Deutschland, Wirtschaftsstandort, Standortsicherung,
     Wettbewerbsfähigkeit, Deindustrialisierung, Wirtschaftswende, Bürokratieabbau.

Episodes: the rule of Table 1 (output gap falls at least two points from a local peak to the next trough;
AMECO autumn 2026). For each episode: change in attention from the peak year to the trough year, per point
of lost capacity, and the U change per point of rise in registered unemployment.

Run from repository root:  python3 scripts/plenum_attention.py
Writes results/plenum_attention.md and results/plenum_attention.csv
"""
import glob
import os
import re
import sys

import pandas as pd

sys.path.insert(0, "scripts")
RAW = "data/raw/cppbt"

FIELDS = {
    "U": r"\b(?:massen|langzeit|jugend)?(?:arbeitslos(?:igkeit|e|en|er|enzahl\w*|enquote\w*)|erwerbslos(?:igkeit|e|en))\b",
    "R": r"\b(?:strukturreform\w*|reformstau\w*|arbeitsmarktreform\w*|sozialreform\w*|agenda 2010|kündigungsschutz\w*"
         r"|lohnnebenkosten|flexibilisierung\w*|deregulierung\w*)",
    "S": r"\b(?:standort deutschland|wirtschaftsstandort\w*|standortsicherung\w*|wettbewerbsfähigkeit\w*"
         r"|deindustrialisierung\w*|wirtschaftswende|bürokratieabbau\w*)",
}
TERMS = {  # single terms reported for the episode table
    "deindustrialisierung": r"\bdeindustrialisierung\w*", "wettbewerbsfähigkeit": r"\bwettbewerbsfähigkeit\w*",
    "strukturreform": r"\bstrukturreform\w*", "kündigungsschutz": r"\bkündigungsschutz\w*",
    "bürokratieabbau": r"\bbürokratieabbau\w*",
}


def count():
    meta = pd.read_csv(glob.glob(f"{RAW}/*Plenarprotokolle_Metadaten.csv")[0], dtype={"doc_id": str})
    meta["key"] = meta.doc_id.str.replace(".xml", "", regex=False).str.zfill(5)
    year = dict(zip(meta.key, meta.sitzung_jahr))
    files = glob.glob(f"{RAW}/txt/files/txt_protokoll-gesamt/*.txt")
    pats = {k: re.compile(v) for k, v in {**FIELDS, **TERMS}.items()}
    rows = []
    for f in files:
        m = re.search(r"Plenarprotokoll_(\d{2})_(\d{3})_(\d{4})-", os.path.basename(f))
        key = f"{m.group(1)}{m.group(2)}"
        t = open(f, encoding="utf-8", errors="ignore").read().lower()
        t = re.sub(r"-\n", "", t)
        r = {"key": key, "year": int(m.group(3)), "words": len(t.split())}
        r.update({k: len(p.findall(t)) for k, p in pats.items()})
        rows.append(r)
    d = pd.DataFrame(rows)
    miss = d.year.isna().sum()
    if miss:
        print(f"warning: {miss} files without year")
    return d.dropna(subset=["year"]).astype({"year": int})


def main():
    path = "results/plenum_attention.csv"
    if os.path.exists(f"{RAW}/counts.csv"):
        d = pd.read_csv(f"{RAW}/counts.csv")
    else:
        d = count()
        d.to_csv(f"{RAW}/counts.csv", index=False)
    y = d.groupby("year").sum(numeric_only=True)
    for k in list(FIELDS) + list(TERMS):
        y[f"{k}_pm"] = 1e6 * y[k] / y.words
    y[["words"] + [f"{k}_pm" for k in list(FIELDS) + list(TERMS)]].round(1).to_csv(path)

    import okun_episodes_intl as oi
    import okun_gap as og
    gap = oi.splice_de(oi.ameco("AVGDGP"))
    dep, _ = og.ba_rates()
    L = ["# Parliamentary attention to unemployment and reform (Bundestag plenary records, CPP-BT)", "",
         "Hits per million words. U = unemployment as a problem; R = structural reform; S = competitiveness and location.",
         "Peak = year before the slump (local peak of the output gap), trough = last year of the slump. 2026 runs to 19 September.", "",
         "| Episode | Lost capacity (pts) | Δ unemployment (pp) | U peak → trough | ΔU per pt capacity | ΔU per pp unemployment "
         "| R peak → trough | ΔR per pt | S peak → trough | ΔS per pt |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for a, b in oi.episodes(gap):
        dg, du = -(gap[b] - gap[a]), dep[b] - dep[a]
        c = {k: (y.loc[a, f"{k}_pm"], y.loc[b, f"{k}_pm"]) for k in FIELDS}
        L.append(f"| {a}-{str(b)[2:]} | {dg:.1f} | {du:+.1f} | {c['U'][0]:.0f} → {c['U'][1]:.0f} | {(c['U'][1] - c['U'][0]) / dg:+.0f} "
                 f"| {(c['U'][1] - c['U'][0]) / du if abs(du) > 0.3 else float('nan'):+.0f} "
                 f"| {c['R'][0]:.0f} → {c['R'][1]:.0f} | {(c['R'][1] - c['R'][0]) / dg:+.0f} "
                 f"| {c['S'][0]:.0f} → {c['S'][1]:.0f} | {(c['S'][1] - c['S'][0]) / dg:+.0f} |")
    L += ["", "## Level of attention by year (hits per million words)", "",
          "| Year | Unemployment rate (%) | U | R | S | Deindustrialisierung | Wettbewerbsfähigkeit | Strukturreform | Kündigungsschutz | Bürokratieabbau |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for yr in [1966, 1967, 1968, 1974, 1975, 1976, 1981, 1982, 1983, 1984, 1993, 1994, 1996, 1997, 2002, 2003, 2004, 2005,
               2009, 2010, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]:
        if yr in y.index:
            r = y.loc[yr]
            L.append(f"| {yr} | {dep.get(yr, float('nan')):.1f} | {r.U_pm:.0f} | {r.R_pm:.0f} | {r.S_pm:.0f} | {r.deindustrialisierung_pm:.1f} "
                     f"| {r['wettbewerbsfähigkeit_pm']:.0f} | {r.strukturreform_pm:.1f} | {r['kündigungsschutz_pm']:.1f} | {r['bürokratieabbau_pm']:.1f} |")
    yy = y[(y.index >= 1950) & (y.index <= 2025)].copy()
    yy["u"] = [dep.get(i) for i in yy.index]
    yy = yy.dropna(subset=["u"])
    import statsmodels.formula.api as smf
    yy["post22"] = (yy.index >= 2022).astype(int)
    m = smf.ols("U_pm ~ u + post22", data=yy).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    res = yy.U_pm - smf.ols("U_pm ~ u", data=yy[yy.index < 2022]).fit().predict(yy)
    L += ["", f"Years with an unemployment rate: {yy.index.min()}-{yy.index.max()} (N = {len(yy)}).",
          f"- U on the unemployment rate, all years: {m.params['u']:.1f} hits per million words per point (HAC s.e. {m.bse['u']:.1f}); "
          f"shift from 2022 on: {m.params['post22']:+.1f} (s.e. {m.bse['post22']:.1f}).",
          "- Residual of U against the pre-2022 relation (actual minus predicted): "
          + ", ".join(f"{i}: {res[i]:+.0f}" for i in res.index if i >= 2019)]
    open("results/plenum_attention.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
