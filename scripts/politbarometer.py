"""Politbarometer 1977-2024 (partial cumulation, ZA2391 v17.0.0): most important problems and the gap between
the judged economic situation of the country and of oneself.

Data: Forschungsgruppe Wahlen (2026), Politbarometer 1977-2024 (Partielle Kumulation), GESIS, Köln, ZA2391
Datenfile Version 17.0.0, doi:10.4232/1.14611. Not redistributed; expected at data/raw/gesis/ZA2391_v17-0-0.dta.

- Problems: share of respondents naming a topic as the most or second most important problem (v33, v34),
  spontaneous answers coded by FGW into 140 categories; topic groups below.
- Economic situation: v25 (country) and v27 (own), 1 very good ... 5 very bad. Net balance = % good or very good
  minus % bad or very bad. Gap = own balance minus country balance.
Weights: dwght (total weight, corrects the East oversample) where positive, else pwght; before 1990 West only.
Missing codes (< 0) are dropped per item. Codes are FGW's; items change over time (codebook v33). Code 98 is
used for another item in 1989, so the reform group starts in 2003. 1986-88 allowed three answers, of which two are kept.

Run from repository root:  python3 scripts/politbarometer.py
Writes results/politbarometer.md and results/politbarometer.csv (yearly aggregates only)
"""
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
F = "data/raw/gesis/ZA2391_v17-0-0.dta"
GROUPS = {
    "unemployment": [14, 90],
    "economy": [13, 95, 115, 117],
    "prices_energy": [5, 93, 76, 110],  # 123 (Energiewende, renewables, coal exit, CO2 tax) left out: mainly climate policy
    "reform": [96, 98],
    "labour_capital": [7, 8, 9, 79, 105],
    "social_justice": [77, 2],
    "pensions": [1],
    "migration": [53, 54, 51, 52],
    "public_debt": [56],
}


def load():
    d = pd.read_stata(F, columns=["intyear", "intmonth", "v4a", "dwght", "pwght", "v25", "v27", "v33", "v34"],
                      convert_categoricals=False)
    d["w"] = np.where(d.dwght > 0, d.dwght, d.pwght)
    return d


def wmean(x, w):
    return float((x * w).sum() / w.sum()) if w.sum() > 0 else np.nan


def main():
    d = load()
    rows = []
    for y, g in d.groupby("intyear"):
        r = {"year": int(y), "n": len(g)}
        p = g[(g.v33 > 0) | (g.v34 > 0)]
        r["n_problem"] = len(p)
        for k, codes in GROUPS.items():
            if k == "reform" and y < 2003:  # codes 96/98 (Reformstau, Hartz IV) only from 2003; in 1989 code 98 carries another item
                codes = []
            hit = p.v33.isin(codes) | p.v34.isin(codes)
            r[k] = 100 * wmean(hit.astype(float), p.w) if len(p) else np.nan
        for v, name in (("v25", "country"), ("v27", "own")):
            q = g[g[v] > 0]
            r[f"n_{name}"] = len(q)
            if len(q):
                r[f"{name}_good"] = 100 * wmean((q[v] <= 2).astype(float), q.w)
                r[f"{name}_bad"] = 100 * wmean((q[v] >= 4).astype(float), q.w)
                r[f"{name}_net"] = r[f"{name}_good"] - r[f"{name}_bad"]
        if "own_net" in r and "country_net" in r:
            r["gap"] = r["own_net"] - r["country_net"]
        rows.append(r)
    t = pd.DataFrame(rows).set_index("year")
    t.round(1).to_csv("results/politbarometer.csv")

    import okun_gap as og
    dep, _ = og.ba_rates()
    t["u"] = [dep.get(i) for i in t.index]
    L = ["# Politbarometer 1977-2024: problems and economic judgements (weighted annual means)", "",
         "Source: Forschungsgruppe Wahlen (2026), ZA2391 v17.0.0, doi:10.4232/1.14611; own calculation. "
         "Problems: % naming the topic as most or second most important. Net = % good minus % bad. "
         "Gap = own net minus country net. u = registered unemployment rate (BA).", "",
         "| Year | u | Unemployment | Economy | Prices/energy | Reform | Labour-capital | Social justice | Country net | Own net | Gap |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for y in t.index:
        r = t.loc[y]
        f = lambda k: f"{r[k]:.0f}" if k in r and pd.notna(r[k]) else ""
        L.append(f"| {y} | {r.u:.1f} | " + " | ".join(f(k) for k in ["unemployment", "economy", "prices_energy", "reform",
                                                                       "labour_capital", "social_justice", "country_net", "own_net", "gap"]) + " |")
    import statsmodels.formula.api as smf
    t["du"] = t.u.diff()
    x = t.dropna(subset=["unemployment", "u", "migration", "du"])
    m = smf.ols("unemployment ~ u + du + migration + prices_energy", data=x).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    L += ["", "## Competing issues", "", "| Year | Migration | Prices/energy | Economy | Unemployment |", "|---|---|---|---|---|"]
    for yy in (1992, 1993, 2003, 2005, 2015, 2016, 2018, 2019, 2022, 2023, 2024):
        L.append(f"| {yy} | {t.migration[yy]:.0f} | {t.prices_energy[yy]:.0f} | {t.economy[yy]:.0f} | {t.unemployment[yy]:.0f} |")
    L += ["", f"Regression of 'unemployment named' (%) on the unemployment rate, its change and the shares naming migration and "
          f"prices/energy, {int(x.index.min())}-{int(x.index.max())} (N = {len(x)}), HAC s.e.: "
          + "; ".join(f"{k} {m.params[k]:+.2f} ({m.bse[k]:.2f})" for k in ["u", "du", "migration", "prices_energy"])
          + f"; R² {m.rsquared:.2f}. Residual 2022-24: " + ", ".join(f"{i} {m.resid.get(i, float('nan')):+.1f}" for i in (2022, 2023, 2024)) + "."]
    x = t.dropna(subset=["unemployment", "u"])
    L += ["", f"Correlation of 'unemployment named' with the unemployment rate: {x.unemployment.corr(x.u):+.2f} "
          f"({x.index.min()}-{x.index.max()}, N = {len(x)}).", ""]
    g = t.dropna(subset=["gap"])
    if len(g):
        L += ["Note: West Germany only until 1990; unified Germany from 1991 (the own balance falls from 60 to 23 at the break).",
              f"Gap (own minus country net balance): mean {g.gap.mean():+.0f}; "
              f"largest: " + ", ".join(f"{i} {g.gap[i]:+.0f}" for i in g.gap.sort_values(ascending=False).index[:6]) + "."]
    open("results/politbarometer.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
