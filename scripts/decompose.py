"""Referee findings 1-3: where does the German output shortfall come from?

A. Growth accounting of actual GDP (AMECO, Autumn 2026): log GDP = log employment
   + log hours per person + log output per hour. Each component's 2025 level is compared with
   its own 2014-19 trend extrapolated to 2025. The three shortfalls add up to the GDP shortfall
   (in log points, shown as percent).
B. Approximate production-function decomposition of potential output, in the spirit of the
   Commission method (Havik et al. 2014): potential = TFP trend x capital^0.35 x potential labour^0.65,
   with potential labour = labour force x (1 - NAWRU) x hours per person. TFP trend is the residual.
   Shortfalls of each contribution against its 2014-19 trend, 2025.
C. Unemployment of German nationals only (BA, rate on dependent civilian labour force), to strip
   out the registration of Ukrainian refugees from June 2022; pass-through per point of lost capacity.

Run from repository root:  python3 scripts/decompose.py
Writes results/decompose.md
"""
import math
import os
import re
import urllib.request

import openpyxl

RAW = "data/raw"
YEARS = list(range(2010, 2028))
C = {"DEU": "Germany", "FRA": "France", "ITA": "Italy", "GBR": "United Kingdom", "USA": "United States"}
URL = ("https://ec.europa.eu/economy_finance/ameco/wq/series?fullVariable={code}&countries="
       + ",".join(C) + "&years=" + ",".join(map(str, YEARS)) + "&lastYear=0&defaultCountries=0")
V = {"gdp": "1.1.0.0.OVGD", "pot": "1.0.0.0.OVGDP", "emp": "1.0.0.0.NETD", "hpp": "1.0.0.0.NLHA",
     "hours": "1.0.0.0.NLHT", "k": "1.0.0.0.OKND", "lf": "1.0.0.0.NLTN", "nawru": "1.0.0.0.ZNAWRU",
     "gap": "1.0.0.0.AVGDGP"}
ALPHA = 0.35
T0, T1, END = 2014, 2019, 2025


def fetch(code):
    os.makedirs(RAW, exist_ok=True)
    path = f"{RAW}/ameco_{code}_5c.html"
    if not os.path.exists(path):
        req = urllib.request.Request(URL.format(code=code), headers={"User-Agent": "Mozilla/5.0 (research script)"})
        with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
            f.write(r.read())
    out = {}
    for row in re.findall(r"<tr.*?</tr>", open(path, encoding="utf-8").read(), re.S):
        c = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
        if c and c[0] in C.values():
            out[c[0]] = {y: float(v) for y, v in zip(YEARS, c[3:]) if v not in ("", "NA")}
    return out


def shortfall(series):
    """Log deviation (in %) of END level from the T0-T1 trend extrapolated to END."""
    g = (math.log(series[T1]) - math.log(series[T0])) / (T1 - T0)
    return 100 * (math.log(series[END]) - (math.log(series[T1]) + g * (END - T1)))


def main():
    d = {k: fetch(v) for k, v in V.items()}
    lines = ["# Decomposition of the output shortfall, 2025 against the 2014-19 trend (AMECO, Autumn 2026)", "",
             "## A. Actual GDP: employment, hours per person, output per hour (log points, %)", "",
             "| | GDP | Employment | Hours per person | Output per hour |", "|---|---|---|---|---|"]
    for iso, name in C.items():
        g = {k: d[k][name] for k in d}
        prod = {y: g["gdp"][y] / g["hours"][y] for y in g["hours"]}
        lines.append(f"| {iso} | {shortfall(g['gdp']):.1f} | {shortfall(g['emp']):.1f} | "
                     f"{shortfall(g['hpp']):.1f} | {shortfall(prod):.1f} |")
    lines += ["", "Employment, hours per person and output per hour add up to GDP (hours = employment × hours per person).", "",
              "## B. Potential output: approximate production function (log points, %)", "",
              f"Potential = TFP × K^{ALPHA} × L^{1 - ALPHA}; L = labour force × (1 − NAWRU) × hours per person; TFP residual.", "",
              "| | Potential | Capital (×0.35) | Labour force (×0.65) | 1−NAWRU (×0.65) | Hours per person (×0.65) | TFP (residual) |",
              "|---|---|---|---|---|---|---|"]
    for iso, name in C.items():
        g = {k: d[k][name] for k in d}
        if END not in g["k"]:  # France: capital stock ends 2024; extend with its 2023-24 growth (flagged)
            g["k"] = dict(g["k"])
            g["k"][END] = g["k"][END - 1] ** 2 / g["k"][END - 2]
            iso = iso + "*"
        une = {y: 1 - g["nawru"][y] / 100 for y in g["nawru"]}
        sp, sk, slf, sn, sh = (shortfall(g["pot"]), shortfall(g["k"]), shortfall(g["lf"]), shortfall(une),
                               shortfall(g["hpp"]))
        tfp = sp - ALPHA * sk - (1 - ALPHA) * (slf + sn + sh)
        lines.append(f"| {iso} | {sp:.1f} | {ALPHA * sk:.1f} | {(1 - ALPHA) * slf:.1f} | {(1 - ALPHA) * sn:.1f} | "
                     f"{(1 - ALPHA) * sh:.1f} | {tfp:.1f} |")
    lines += ["", "Approximation: the Commission uses trend participation and trend hours, not actual hours per person,",
              "and its own capital series; the split is indicative, not the official one.",
              "* France: capital stock for 2025 extrapolated from 2023-24 growth.", ""]

    # C. German nationals only
    wb = openpyxl.load_workbook(f"{RAW}/ba_alo_dwo.xlsx", read_only=True, data_only=True)
    de, fo = {}, {}
    for r in wb["Tabelle 2.3.1"].iter_rows(values_only=True):
        if isinstance(r[0], int):
            de[r[0]] = (r[1], r[3])
            fo[r[0]] = (r[10], r[12])
    gap = d["gap"]["Germany"]
    lines += ["## C. Registered unemployment, German nationals only (BA, rate on dependent civilian labour force)", "",
              "| Episode | Δ gap (pp) | Δu all (pp) | Δu Germans (pp) | Ratio all | Ratio Germans | Δ unemployed foreigners / Δ all |",
              "|---|---|---|---|---|---|---|"]
    tot = {}
    for r in wb["Tabelle 2.1.1"].iter_rows(values_only=True):
        if isinstance(r[0], int) and isinstance(r[7], (int, float)):
            tot[r[0]] = (r[1], r[7])
    for name, a, b in (("2008/09", 2008, 2009), ("2020", 2019, 2020), ("2022-25", 2022, 2025)):
        dg = gap[b] - gap[a] if a >= 2010 else None
        if dg is None:
            dg = {"2008/09": -6.42}[name]  # from okun_gap.py (AMECO, peak 2008 to trough 2009)
        dua, dud = tot[b][1] - tot[a][1], de[b][1] - de[a][1]
        share_f = (fo[b][0] - fo[a][0]) / (tot[b][0] - tot[a][0]) if tot[b][0] != tot[a][0] else float("nan")
        lines.append(f"| {name} | {dg:.2f} | {dua:+.1f} | {dud:+.1f} | {dua / -dg:.2f} | {dud / -dg:.2f} | {share_f:.0%} |")
    lines += ["", "Foreign nationals' unemployment also responds to the cycle, so the German-nationals ratio is a lower bound",
              "for the cyclical pass-through; the true value lies between the two ratios."]
    open("results/decompose.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
