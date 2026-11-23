"""Evidence for the revised thesis: 'lost potential without layoffs'.

For DEU, FRA, ITA, GBR, USA (AMECO, Autumn 2026 vintage):
1. Decompose the shortfall of real GDP in 2025 against its 2014-19 trend into
   (a) a shortfall of potential output against its own 2014-19 trend and
   (b) the change in the output gap 2019-2025.
2. Labour productivity per hour, hours per person, employment: 2014-19 vs 2019-25.
3. Manufacturing: real gross value added against employment, 2019 (and 2022) to 2025.

Run from repository root:  python3 scripts/potential_evidence.py
Writes results/potential_evidence.md and results/potential_evidence.csv
"""
import csv
import os
import re
import urllib.request

RAW = "data/raw"
OUT = "results"
YEARS = list(range(2010, 2028))
COUNTRIES = {"DEU": "Germany", "FRA": "France", "ITA": "Italy", "GBR": "United Kingdom", "USA": "United States"}
VARS = {
    "gdp": "1.1.0.0.OVGD",        # GDP, 2020 reference levels
    "pot": "1.0.0.0.OVGDP",       # potential GDP, 2020 reference levels
    "gap": "1.0.0.0.AVGDGP",      # output gap, % of potential
    "hours": "1.0.0.0.NLHT",      # total hours worked, millions
    "hpp": "1.0.0.0.NLHA",        # hours per person employed
    "emp": "1.0.0.0.NETD",        # employment, persons, domestic
    "gva_m": "1.1.0.0.OVGM",      # real GVA manufacturing
    "emp_m": "1.0.0.0.NETM",      # employment manufacturing, persons
    "u_ilo": "1.0.0.0.ZUTN",      # unemployment rate, Eurostat definition
}
URL = ("https://ec.europa.eu/economy_finance/ameco/wq/series?fullVariable={code}&countries="
       + ",".join(COUNTRIES) + "&years=" + ",".join(map(str, YEARS)) + "&lastYear=0&defaultCountries=0")


def fetch(code):
    os.makedirs(RAW, exist_ok=True)
    path = f"{RAW}/ameco_{code}_5c.html"
    if not os.path.exists(path):
        req = urllib.request.Request(URL.format(code=code), headers={"User-Agent": "Mozilla/5.0 (research script)"})
        with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
            f.write(r.read())
    html = open(path, encoding="utf-8").read()
    out = {}
    for row in re.findall(r"<tr.*?</tr>", html, re.S):
        c = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
        if c and c[0] in COUNTRIES.values():
            out[c[0]] = {y: float(v) for y, v in zip(YEARS, c[3:]) if v not in ("", "NA")}
    return out


def cagr(d, a, b):
    return (d[b] / d[a]) ** (1 / (b - a)) - 1


def main():
    data = {k: fetch(v) for k, v in VARS.items()}
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for iso, name in COUNTRIES.items():
        g = {k: data[k].get(name, {}) for k in VARS}
        trend_g = cagr(g["gdp"], 2014, 2019)
        trend_p = cagr(g["pot"], 2014, 2019)
        gdp_short = 100 * (g["gdp"][2025] / (g["gdp"][2019] * (1 + trend_g) ** 6) - 1)
        pot_short = 100 * (g["pot"][2025] / (g["pot"][2019] * (1 + trend_p) ** 6) - 1)
        prod = {y: g["gdp"][y] / g["hours"][y] for y in g["hours"] if y in g["gdp"]}
        r = {
            "country": iso,
            "gdp_growth_2014_19_pa": round(100 * trend_g, 2),
            "gdp_growth_2019_25_pa": round(100 * cagr(g["gdp"], 2019, 2025), 2),
            "gdp_shortfall_vs_trend_2025_pct": round(gdp_short, 1),
            "potential_growth_2014_19_pa": round(100 * trend_p, 2),
            "potential_growth_2019_25_pa": round(100 * cagr(g["pot"], 2019, 2025), 2),
            "potential_shortfall_vs_trend_2025_pct": round(pot_short, 1),
            "gap_2019": round(g["gap"][2019], 2), "gap_2022": round(g["gap"][2022], 2), "gap_2025": round(g["gap"][2025], 2),
            "prod_per_hour_growth_2014_19_pa": round(100 * cagr(prod, 2014, 2019), 2),
            "prod_per_hour_growth_2019_25_pa": round(100 * cagr(prod, 2019, 2025), 2),
            "hours_per_person_2019": round(g["hpp"][2019]), "hours_per_person_2025": round(g["hpp"][2025]),
            "employment_change_2019_25_pct": round(100 * (g["emp"][2025] / g["emp"][2019] - 1), 1),
            "manuf_gva_change_2019_25_pct": round(100 * (g["gva_m"][2025] / g["gva_m"][2019] - 1), 1) if 2025 in g["gva_m"] else "",
            "manuf_emp_change_2019_25_pct": round(100 * (g["emp_m"][2025] / g["emp_m"][2019] - 1), 1) if 2025 in g["emp_m"] else "",
            "manuf_gva_change_2022_25_pct": round(100 * (g["gva_m"][2025] / g["gva_m"][2022] - 1), 1) if 2025 in g["gva_m"] else "",
            "manuf_emp_change_2022_25_pct": round(100 * (g["emp_m"][2025] / g["emp_m"][2022] - 1), 1) if 2025 in g["emp_m"] else "",
            "u_ilo_2019": g["u_ilo"].get(2019), "u_ilo_2022": g["u_ilo"].get(2022), "u_ilo_2025": g["u_ilo"].get(2025),
        }
        rows.append(r)
    with open(f"{OUT}/potential_evidence.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    def line(label, key, fmt="{}"):
        return f"| {label} | " + " | ".join(fmt.format(r[key]) if r[key] != "" else "n/a" for r in rows) + " |"

    md = ["# Evidence: lost potential without layoffs (AMECO, Autumn 2026 vintage)", "",
          "| | " + " | ".join(r["country"] for r in rows) + " |", "|---|" + "---|" * len(rows),
          line("Real GDP growth 2014–19, % p.a.", "gdp_growth_2014_19_pa"),
          line("Real GDP growth 2019–25, % p.a.", "gdp_growth_2019_25_pa"),
          line("GDP 2025 vs 2014–19 trend, %", "gdp_shortfall_vs_trend_2025_pct"),
          line("Potential growth 2014–19, % p.a.", "potential_growth_2014_19_pa"),
          line("Potential growth 2019–25, % p.a.", "potential_growth_2019_25_pa"),
          line("Potential 2025 vs 2014–19 trend, %", "potential_shortfall_vs_trend_2025_pct"),
          line("Output gap 2019, %", "gap_2019"), line("Output gap 2022, %", "gap_2022"), line("Output gap 2025, %", "gap_2025"),
          line("Productivity per hour 2014–19, % p.a.", "prod_per_hour_growth_2014_19_pa"),
          line("Productivity per hour 2019–25, % p.a.", "prod_per_hour_growth_2019_25_pa"),
          line("Hours per person 2019", "hours_per_person_2019"), line("Hours per person 2025", "hours_per_person_2025"),
          line("Employment 2019–25, %", "employment_change_2019_25_pct"),
          line("Manufacturing real GVA 2019–25, %", "manuf_gva_change_2019_25_pct"),
          line("Manufacturing employment 2019–25, %", "manuf_emp_change_2019_25_pct"),
          line("Manufacturing real GVA 2022–25, %", "manuf_gva_change_2022_25_pct"),
          line("Manufacturing employment 2022–25, %", "manuf_emp_change_2022_25_pct"),
          line("ILO unemployment 2019, %", "u_ilo_2019"), line("ILO unemployment 2022, %", "u_ilo_2022"),
          line("ILO unemployment 2025, %", "u_ilo_2025"), "",
          "Identity (approximately): GDP shortfall vs trend ≈ potential shortfall vs trend + (gap 2025 − gap 2019)."]
    open(f"{OUT}/potential_evidence.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
