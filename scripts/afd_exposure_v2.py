"""AfD gain 2021-2025 by district, version 2 (answers referee points on timing and rivals).

Changes to afd_exposure.py:
- Industrial exposure measured BEFORE the shock: share of employees (SV-Beschäftigte am Arbeitsort)
  in the secondary sector, 2019 (INKAR 2025, indicator a_svb_sekundär).
- Migration as rival explanation: change in the foreign share of the population 2019-2023 and the
  share of protection seekers 2023 (INKAR, a_ausl_bev, a_schutzs_bev).
- Same controls as before (east, city district, income per head, AfD share 2021) and the change in
  the registered unemployment rate 2022-25.
Data: INKAR 2025 extract (data/raw/inkar/inkar_kreise_subset.csv, made by streaming the INKAR csv),
Makrowolf static files for elections, unemployment, district types and income.

Run from repository root:  python3 scripts/afd_exposure_v2.py [path to macro repo]
Writes results/afd_exposure_v2.md
"""
import sys

import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, "scripts")
from afd_exposure import load  # noqa: E402

MACRO = sys.argv[1] if len(sys.argv) > 1 else "../macro"


def inkar():
    d = pd.read_csv("data/raw/inkar/inkar_kreise_subset.csv", sep=";", dtype={"Kennziffer": str}, decimal=",")
    d["ags"] = d["Kennziffer"].str.zfill(8).str[:5]
    p = d.pivot_table(index="ags", columns=["Kuerzel", "Zeitbezug"], values="Wert", aggfunc="first")
    out = pd.DataFrame(index=p.index)
    out["sec_2019"] = p[("a_svb_sekundär", 2019)]
    out["sec_2023"] = p[("a_svb_sekundär", 2023)]
    out["foreign_2019"] = p[("a_ausl_bev", 2019)]
    out["foreign_2023"] = p[("a_ausl_bev", 2023)]
    out["refugee_2023"] = p[("a_schutzs_bev", 2023)]
    out["d_foreign"] = out.foreign_2023 - out.foreign_2019
    return out


def main():
    import afd_exposure
    afd_exposure.MACRO = MACRO
    afd_exposure.S = f"{MACRO}/data/static"
    d = load().join(inkar(), how="inner")
    import numpy as np
    k = pd.read_csv(f"{MACRO}/data/static/kreisatlas_inkar.csv", dtype={"ags": str})
    for key, col in (("akademiker", "degree"), ("alter", "mean_age"), ("dichte", "density")):
        d = d.join(k[k.kennzahl == key].set_index("ags")["wert"].rename(col))
    d["log_density"] = np.log(d.density)
    d = d.dropna(subset=["sec_2019", "d_foreign", "refugee_2023", "degree", "mean_age", "log_density"])
    models = {
        "(1) industry 2019": "d_afd ~ d_u + sec_2019 + east + city + income_k + afd21",
        "(2) migration only": "d_afd ~ d_u + d_foreign + refugee_2023 + east + city + income_k + afd21",
        "(3) both": "d_afd ~ d_u + sec_2019 + d_foreign + refugee_2023 + east + city + income_k + afd21",
        "(4) both, West only": "d_afd ~ d_u + sec_2019 + d_foreign + refugee_2023 + city + income_k + afd21",
        "(5) + education, age, density": "d_afd ~ d_u + sec_2019 + d_foreign + refugee_2023 + east + city + income_k + afd21 + degree + mean_age + log_density",
        "(6) = (5), West only": "d_afd ~ d_u + sec_2019 + d_foreign + refugee_2023 + city + income_k + afd21 + degree + mean_age + log_density",
    }
    labels = {"d_u": "Δ unemployment rate 2022-25 (pp)", "sec_2019": "Secondary-sector share of employees 2019 (%)",
              "d_foreign": "Δ foreign share of population 2019-23 (pp)", "refugee_2023": "Protection seekers, share of population 2023 (%)",
              "east": "East", "city": "City district", "income_k": "Income per head (€1,000/month)", "afd21": "AfD share 2021",
              "degree": "Employees with a degree (%)", "mean_age": "Mean age (years)", "log_density": "Log population density"}
    res = {k: smf.ols(f, data=d if "West" not in k else d[d.east == 0]).fit(cov_type="HC1") for k, f in models.items()}
    L = ["# AfD gain 2021-2025: pre-shock industry and migration (districts)", "",
         f"N = {len(d)} districts (West: {int((d.east == 0).sum())}). OLS, robust standard errors (HC1).", "",
         "| Variable | " + " | ".join(models) + " |", "|---|" + "---|" * len(models)]
    for v, lab in labels.items():
        cells = []
        for r in res.values():
            if v in r.params:
                p = r.pvalues[v]
                star = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
                cells.append(f"{r.params[v]:.2f}{star} ({r.bse[v]:.2f})")
            else:
                cells.append("")
        L.append(f"| {lab} | " + " | ".join(cells) + " |")
    L.append("| R² | " + " | ".join(f"{r.rsquared:.2f}" for r in res.values()) + " |")
    keys = ["sec_2019", "d_foreign", "refugee_2023", "d_u", "income_k", "afd21", "degree", "mean_age", "log_density"]
    for name in ["(3) both", "(5) + education, age, density", "(6) = (5), West only"]:
        r = res[name]
        sub = d if "West" not in name else d[d.east == 0]
        L += ["", f"## One standard deviation, model {name}", ""]
        for v in keys:
            if v in r.params:
                L.append(f"- {labels[v]}: SD {sub[v].std():.2f}, effect {r.params[v] * sub[v].std():+.2f} pp AfD (p = {r.pvalues[v]:.3f})")
    L += ["", f"Mean AfD gain {d.d_afd.mean():.1f} pp. Correlation of 2019 industry share with the 2026 manufacturing share: "
          f"{d.sec_2019.corr(d.sh_manuf):.2f}."]
    open("results/afd_exposure_v2.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
