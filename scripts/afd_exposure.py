"""Section 5 evidence: does the AfD gain 2021-2025 track industrial exposure or unemployment?

Kreis level (400 districts). Data from the Makrowolf repository (hungerland-macro/macro):
- data/static/kreisatlas_wahlen.csv: Bundestag second votes 2021 and 2025 on 2021 district
  boundaries (GERDA, Heddesheimer et al. 2025).
- data/static/zoll_kreise_ba.csv: employees subject to social insurance by district, March 2026
  (BA Regionalreport): total, manufacturing (C), and three manufacturing blocks:
  'vorleistung' = WZ 16, 17, 19, 20, 22, 23 (wood, paper, coke and petroleum, chemicals,
  rubber and plastics, glass/ceramics/minerals: the energy-intensive core);
  'metall' = WZ 24-30, 32, 33 (metals, electrical, machinery, vehicles: the supplier and auto core);
  'konsum' = WZ 10-15, 18, 21, 31.
- data/static/kreis_arbeitsmarkt_monat.csv.gz: registered unemployment rate by district, monthly (BA).
- data/static/kreisatlas_typen.csv: West/East, settlement type (BBSR).
- data/static/kreisatlas_inkar.csv: household income per head (INKAR 2025).

Run from repository root:  python3 scripts/afd_exposure.py [path to macro repo]
Writes results/afd_exposure.md and results/afd_exposure_kreise.csv
"""
import sys

import pandas as pd
import statsmodels.formula.api as smf

MACRO = sys.argv[1] if len(sys.argv) > 1 else "../macro"
S = f"{MACRO}/data/static"


def load():
    w = pd.read_csv(f"{S}/kreisatlas_wahlen.csv", dtype={"ags": str})
    w = w[(w.wahl == "btw") & (w.jahr.isin([2021, 2025]))].copy()
    w["afd_share"] = 100 * w.afd / w.gueltige
    afd = w.pivot(index="ags", columns="jahr", values="afd_share").rename(columns={2021: "afd21", 2025: "afd25"})

    b = pd.read_csv(f"{S}/zoll_kreise_ba.csv", dtype={"ags": str})
    b = b.pivot(index="ags", columns="merkmal", values="wert")
    emp = pd.DataFrame({
        "sh_manuf": 100 * b["c"] / b["insgesamt"],
        "sh_energy": 100 * b["vorleistung"] / b["insgesamt"],
        "sh_metal": 100 * b["metall"] / b["insgesamt"],
    })

    a = pd.read_csv(f"{S}/kreis_arbeitsmarkt_monat.csv.gz", dtype={"ags": str})
    a = a[a.merkmal == "quote"].copy()
    a["year"] = a.monat.str[:4].astype(int)
    u = a[a.year.isin([2019, 2021, 2022, 2025])].groupby(["ags", "year"]).wert.mean().unstack()
    u.columns = [f"u{c % 100:02d}" for c in u.columns]

    t = pd.read_csv(f"{S}/kreisatlas_typen.csv", dtype={"ags": str}).set_index("ags")
    t["east"] = (t.west_ost == 2).astype(int)
    t["city"] = (t.kreistyp == 1).astype(int)

    i = pd.read_csv(f"{S}/kreisatlas_inkar.csv", dtype={"ags": str})
    inc = i[i.kennzahl == "einkommen"].set_index("ags")["wert"].rename("income")

    d = afd.join(emp).join(u).join(t[["east", "city"]]).join(inc).dropna()
    d["d_afd"] = d.afd25 - d.afd21
    d["d_u"] = d.u25 - d.u22
    d["income_k"] = d.income / 1000
    return d


def fit(d, formula):
    return smf.ols(formula, data=d).fit(cov_type="HC1")


def main():
    d = load()
    d.to_csv("results/afd_exposure_kreise.csv")
    models = {
        "(1) unemployment only": "d_afd ~ d_u + east",
        "(2) exposure only": "d_afd ~ sh_energy + sh_metal + east",
        "(3) both": "d_afd ~ d_u + sh_energy + sh_metal + east",
        "(4) both + controls": "d_afd ~ d_u + sh_energy + sh_metal + east + city + income_k + afd21",
        "(5) West only": "d_afd ~ d_u + sh_energy + sh_metal + city + income_k + afd21",
    }
    out = ["# AfD gain 2021–2025 against exposure and unemployment, 400 districts", "",
           f"N = {len(d)} districts (West only: {int((d.east == 0).sum())}). OLS, robust standard errors (HC1).", "",
           "Dependent variable: change in AfD second-vote share, Bundestag 2025 minus 2021, percentage points.", "",
           "| Variable | " + " | ".join(models) + " |", "|---|" + "---|" * len(models)]
    res = {k: fit(d if "West" not in k else d[d.east == 0], f) for k, f in models.items()}
    labels = {"d_u": "Δ unemployment rate 2022–25 (pp)", "sh_energy": "Share energy-intensive manuf. (% of employees)",
              "sh_metal": "Share metal/auto/machinery (% of employees)", "east": "East", "city": "City district",
              "income_k": "Income per head (€1,000/month)", "afd21": "AfD share 2021"}
    for v, lab in labels.items():
        cells = []
        for r in res.values():
            if v in r.params:
                p = r.pvalues[v]
                star = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
                cells.append(f"{r.params[v]:.2f}{star} ({r.bse[v]:.2f})")
            else:
                cells.append("")
        out.append(f"| {lab} | " + " | ".join(cells) + " |")
    out.append("| R² | " + " | ".join(f"{r.rsquared:.2f}" for r in res.values()) + " |")

    sd = d[["d_u", "sh_energy", "sh_metal"]].std()
    r4 = res["(4) both + controls"]
    out += ["", "## Size of effects (model 4, one standard deviation)", ""]
    for v in ["d_u", "sh_energy", "sh_metal"]:
        out.append(f"- {labels[v]}: SD {sd[v]:.2f}, effect {r4.params[v] * sd[v]:+.2f} pp AfD")
    out += ["", "## Descriptives", "",
            f"- Mean AfD gain: {d.d_afd.mean():.1f} pp (West {d[d.east == 0].d_afd.mean():.1f}, East {d[d.east == 1].d_afd.mean():.1f}).",
            f"- Mean Δ unemployment 2022–25: {d.d_u.mean():.2f} pp; correlation with AfD gain: {d.d_u.corr(d.d_afd):.2f}.",
            f"- Correlation AfD gain with energy-intensive share: {d.sh_energy.corr(d.d_afd):.2f}; with metal share: {d.sh_metal.corr(d.d_afd):.2f}.",
            "", "Caveats: employment shares are measured in March 2026, after the shock (no pre-shock baseline in the data);",
            "block shares inside manufacturing partly follow state-level industry mixes (see macro docs/zoll_kreise.md);",
            "cross-section only, no causal identification."]
    open("results/afd_exposure.md", "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    main()
