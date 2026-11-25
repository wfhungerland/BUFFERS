"""Split of the German employment shortfall and of employment change by sector, 2019-2025.

A. Employment 2025 against a counterfactual in which the labour force had kept growing at its 2014-19
   trend (variant: 2010-14, before the 2015-16 migration) and the unemployment rate had stayed at its 2019
   level. Shortfall = labour force against its trend + change in (1 - ILO unemployment rate) since 2019.
   (An earlier version extrapolated the 2014-19 trend of the employment rate, which implied an unemployment
   rate of under 1 percent in 2025; that overstated the demand part.)
   AMECO, autumn 2026: NETD (employment, domestic), NLTN (labour force), ZUTN (ILO unemployment rate).
   Note: NETD (domestic concept) and NLTN/ZUTN (national/labour force survey) differ slightly; the
   residual is reported.
B. Employment by sector (persons, domestic concept), 2019 and 2025: Eurostat nama_10_a10_e.
Run from repository root:  python3 scripts/employment_split.py
Writes results/employment_split.md
"""
import json
import math
import os
import re
import urllib.request

RAW = "data/raw"
YEARS = list(range(2010, 2028))


def ameco(code):
    path = f"{RAW}/ameco_{code}_DEU_split.html"
    if not os.path.exists(path):
        url = (f"https://ec.europa.eu/economy_finance/ameco/wq/series?fullVariable={code}&countries=DEU&years="
               + ",".join(map(str, YEARS)) + "&lastYear=0&defaultCountries=0")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research script)"})
        with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
            f.write(r.read())
    for row in re.findall(r"<tr.*?</tr>", open(path, encoding="utf-8").read(), re.S):
        c = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
        if c and c[0] == "Germany":
            return {y: float(v) for y, v in zip(YEARS, c[3:]) if v}


def short(s):
    g = (math.log(s[2019]) - math.log(s[2014])) / 5
    return 100 * (math.log(s[2025]) - math.log(s[2019]) - 6 * g)


def eurostat():
    path = f"{RAW}/eurostat_nama_10_a10_e_de.json"
    if not os.path.exists(path):
        url = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nama_10_a10_e"
               "?geo=DE&unit=THS_PER&na_item=EMP_DC&sinceTimePeriod=2014")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research script)"})
        with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
            f.write(r.read())
    d = json.load(open(path))
    dims, size = d["id"], d["size"]
    idx = {k: d["dimension"][k]["category"]["index"] for k in dims}
    lab = d["dimension"]["nace_r2"]["category"]["label"]

    def get(n, y):
        pos, mult = 0, 1
        coords = {k: 0 for k in dims}
        coords["nace_r2"], coords["time"] = idx["nace_r2"][n], idx["time"][str(y)]
        for k, s in zip(reversed(dims), reversed(size)):
            pos += coords[k] * mult
            mult *= s
        return d["value"].get(str(pos))
    return [(n, lab[n], get(n, 2019), get(n, 2025)) for n in idx["nace_r2"]]


def main():
    emp, lf, u = ameco("1.0.0.0.NETD"), ameco("1.0.0.0.NLTN"), ameco("1.0.0.0.ZUTN")
    er = {y: 1 - u[y] / 100 for y in u}
    def lf_short(a, b):
        g = (math.log(lf[b]) - math.log(lf[a])) / (b - a)
        return 100 * (math.log(lf[2025]) - math.log(lf[2019]) - 6 * g)
    sr = 100 * math.log(er[2025] / er[2019])
    raw = 100 * math.log(emp[2025] / emp[2019])
    L = ["# German employment: supply, demand and sectors", "",
         "## A. Employment 2025 against a counterfactual (log points)", "",
         "Counterfactual: labour force on its pre-2019 trend, unemployment rate at its 2019 level.", "",
         f"- Actual change in employment 2019-25 (domestic concept): {raw:+.1f}; labour force {100 * math.log(lf[2025] / lf[2019]):+.1f}; "
         f"ILO unemployment rate {u[2019]:.1f} % in 2019, {u[2025]:.1f} % in 2025.",
         f"- Labour-force trend 2014-19 ({100 * (math.log(lf[2019]) - math.log(lf[2014])) / 5:.2f} % a year): labour force against trend {lf_short(2014, 2019):.1f}, "
         f"higher unemployment {sr:.1f}; total {lf_short(2014, 2019) + sr:.1f}; supply share {lf_short(2014, 2019) / (lf_short(2014, 2019) + sr):.0%}.",
         f"- Labour-force trend 2010-14 ({100 * (math.log(lf[2014]) - math.log(lf[2010])) / 4:.2f} % a year): labour force against trend {lf_short(2010, 2014):.1f}, "
         f"higher unemployment {sr:.1f}; total {lf_short(2010, 2014) + sr:.1f}; supply share {lf_short(2010, 2014) / (lf_short(2010, 2014) + sr):.0%}.", "",
         "## B. Employment by sector, thousand persons (Eurostat nama_10_a10_e)", "",
         "| Sector | 2019 | 2025 | Change |", "|---|---|---|---|"]
    for n, lab, a, b in eurostat():
        if a is not None and b is not None:
            L.append(f"| {n} {lab[:60]} | {a:,.0f} | {b:,.0f} | {b - a:+,.0f} |")
    open("results/employment_split.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
