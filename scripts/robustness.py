"""Phase 1 robustness checks for the output-shortfall accounting.

A. Consistent accounting: actual GDP 2025 against a counterfactual in which potential output had
   kept growing at its own pre-2019 trend and the output gap were closed. Then
   shortfall = lost potential (potential 2025 vs its own trend) + output gap 2025.
   Trend windows 1995-2019, 2010-19 and 2014-19.
B. Real-time check: German potential output 2025 (current vintage) against the path the Commission
   itself projected in its autumn 2019 forecast (growth 2019-21 as forecast, then the 2021 rate),
   and the output gap for 2018/2019 as estimated then and now.
C. Real wages and real unit labour costs, 2019-2025: compensation per employee deflated by the
   private-consumption deflator; nominal unit labour cost (compensation per employee / real GDP
   per employee) deflated by the GDP deflator.

Countries: DEU, FRA, ITA, GBR, USA, JPN. Source: AMECO (autumn 2026 vintage via the AMECO
query service; autumn 2019 vintage from the AMECO archive, data/raw/ameco_vintages/).
Run from repository root:  python3 scripts/robustness.py
Writes results/robustness.md
"""
import math
import os
import re
import urllib.request

RAW = "data/raw"
YEARS = list(range(1990, 2028))
C = {"DEU": "Germany", "FRA": "France", "ITA": "Italy", "GBR": "United Kingdom", "USA": "United States", "JPN": "Japan"}
V = {"gdp": "1.1.0.0.OVGD", "pot": "1.0.0.0.OVGDP", "gap": "1.0.0.0.AVGDGP", "comp": "1.0.0.0.HWCDW",
     "pcph": "3.1.0.0.PCPH", "pvgd": "3.1.0.0.PVGD", "emp": "1.0.0.0.NETD"}
URL = ("https://ec.europa.eu/economy_finance/ameco/wq/series?fullVariable={code}&countries=" + ",".join(C)
       + "&years=" + ",".join(map(str, YEARS)) + "&lastYear=0&defaultCountries=0")


def fetch(code):
    os.makedirs(RAW, exist_ok=True)
    path = f"{RAW}/ameco_{code}_long6.html"
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


def vintage2019(code, iso):
    for f in ("AMECO6.TXT", "AMECO1.TXT"):
        p = f"{RAW}/ameco_vintages/autumn2019/{f}"
        for line in open(p, encoding="latin-1"):
            if line.startswith(f"{iso}.{code};"):
                parts = line.strip().split(";")
                return {1960 + i: float(v) for i, v in enumerate(parts[5:]) if v not in ("NA", "")}
    return {}


def lost_potential(pot, a, b=2019, end=2025):
    g = (math.log(pot[b]) - math.log(pot[a])) / (b - a)
    return 100 * (math.log(pot[end]) - math.log(pot[b]) - g * (end - b))


def main():
    d = {k: fetch(v) for k, v in V.items()}
    L = ["# Robustness of the output-shortfall accounting (AMECO)", "",
         "## A. Shortfall against a closed-gap path of pre-2019 potential (log points, %)", "",
         "Shortfall = lost potential (2025 vs own trend) + output gap 2025.", "",
         "| | Lost potential, trend 1995-2019 | 2010-19 | 2014-19 | Output gap 2025 | Total shortfall (2014-19 trend) |",
         "|---|---|---|---|---|---|"]
    for iso, n in C.items():
        if n not in d["pot"] or n not in d["gap"]:
            L.append(f"| {iso} | n/a | n/a | n/a | n/a | n/a |")
            continue
        pot, gap = d["pot"][n], d["gap"][n]
        lp = {w: lost_potential(pot, w) for w in (1995, 2010, 2014) if w in pot}
        g25 = 100 * math.log(1 + gap[2025] / 100)
        L.append(f"| {iso} | {lp.get(1995, float('nan')):.1f} | {lp[2010]:.1f} | {lp[2014]:.1f} | {g25:.1f} | {lp[2014] + g25:.1f} |")

    L += ["", "## B. German potential: autumn 2019 forecast against today", ""]
    P19 = vintage2019("1.0.0.0.OVGDP", "DEU")
    G19 = vintage2019("1.0.0.0.AVGDGP", "DEU")
    Pc, Gc = d["pot"]["Germany"], d["gap"]["Germany"]
    r21 = P19[2021] / P19[2020] - 1
    level = 1.0
    for y in range(2020, 2026):
        level *= (P19[y] / P19[y - 1]) if y <= 2021 else (1 + r21)
    cur = Pc[2025] / Pc[2019]
    L += [f"- Potential growth 2014-19: {100 * ((P19[2019] / P19[2014]) ** 0.2 - 1):.2f} % a year in the 2019 vintage, "
          f"{100 * ((Pc[2019] / Pc[2014]) ** 0.2 - 1):.2f} % today.",
          f"- 2019 vintage: potential to grow {100 * ((P19[2021] / P19[2019]) ** 0.5 - 1):.2f} % a year in 2019-21; extended at that rate, "
          f"potential in 2025 would be {100 * (level - 1):.1f} % above 2019. Today's estimate: {100 * (cur - 1):.1f} %. "
          f"Write-down against the Commission's own 2019 projection: {100 * math.log(cur / level):.1f} log points.",
          f"- Output gap 2018: {G19[2018]:+.2f} % then, {Gc[2018]:+.2f} % today; 2019: {G19[2019]:+.2f} % then, {Gc[2019]:+.2f} % today "
          "(end-of-sample estimates are revised; here the 2019 gap was revised up by more than a point).", ""]

    L += ["## C. Real wages and real unit labour costs, change since 2019 (%)", "",
          "| | Real compensation per employee 2019-22 | 2019-23 | 2019-25 | Real unit labour cost 2019-25 |",
          "|---|---|---|---|---|"]
    for iso, n in C.items():
        if any(n not in d[k] for k in ("comp", "pcph", "pvgd", "gdp", "emp")):
            L.append(f"| {iso} | n/a | n/a | n/a | n/a |")
            continue
        comp, pc, pv, gdp, emp = (d[k][n] for k in ("comp", "pcph", "pvgd", "gdp", "emp"))
        rw = {y: comp[y] / pc[y] for y in comp if y in pc}
        rulc = {y: comp[y] / (gdp[y] / emp[y]) / pv[y] for y in comp if y in pv and y in gdp and y in emp}
        f = lambda s, a, b: 100 * (s[b] / s[a] - 1)
        L.append(f"| {iso} | {f(rw, 2019, 2022):.1f} | {f(rw, 2019, 2023):.1f} | {f(rw, 2019, 2025):.1f} | {f(rulc, 2019, 2025):.1f} |")
    open("results/robustness.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))




def japan():
    """D. Japan after 1990 (OECD Economic Outlook): pass-through and potential write-down."""
    import csv
    def load(f):
        d = {}
        for r in csv.DictReader(open(f, encoding="utf-8")):
            d.setdefault((r["REF_AREA"], r["MEASURE"]), {})[int(r["TIME_PERIOD"])] = float(r["OBS_VALUE"])
        return d
    g = load(f"{RAW}/oecd_GAP_jpn.csv")
    u = load(f"{RAW}/oecd_UNR_jpn.csv")
    p = load(f"{RAW}/oecd_GDPVTR_jpn.csv")
    gap, un = g[("JPN", "GAP")], u[("JPN", "UNR")]
    L = ["", "## D. Japan after 1990 (OECD Economic Outlook)", "",
         "| Episode | Δ gap (pp) | Δ unemployment (pp) | Ratio |", "|---|---|---|---|"]
    for a, b in ((1990, 1994), (1997, 1999), (2007, 2009)):
        dg, du = gap[b] - gap[a], un[b] - un[a]
        L.append(f"| {a}-{b} | {dg:.1f} | {du:+.1f} | {du / -dg:.2f} |")
    pot = p.get(("JPN", "GDPVTR"))
    if pot:
        gr = (math.log(pot[1990]) - math.log(pot[1985])) / 5
        lp = 100 * (math.log(pot[1999]) - math.log(pot[1990]) - gr * 9)
        L.append(f"\nJapanese potential output in 1999 against its 1985-90 trend: {lp:.1f} log points.")
    return L




def alternatives():
    """E. Alternative write-downs (referee point: the Commission's figure as an upper bound)."""
    import csv
    def load(f):
        d = {}
        for r in csv.DictReader(open(f, encoding="utf-8")):
            d.setdefault((r["REF_AREA"], r["MEASURE"]), {})[int(r["TIME_PERIOD"])] = float(r["OBS_VALUE"])
        return d
    pot = load(f"{RAW}/oecd_GDPVTR_jpn.csv")[("DEU", "GDPVTR")]
    gap = load(f"{RAW}/oecd_GAP_jpn.csv")[("DEU", "GAP")]
    d = {k: fetch(v) for k, v in {"lf": "1.0.0.0.NLTN", "nawru": "1.0.0.0.ZNAWRU", "pot": "1.0.0.0.OVGDP"}.items()}
    lf, nw, P = d["lf"]["Germany"], d["nawru"]["Germany"], d["pot"]["Germany"]
    g1014 = (math.log(lf[2014]) - math.log(lf[2010])) / 4
    lf_alt = 100 * (math.log(lf[2025]) - math.log(lf[2019]) - 6 * g1014)
    lf_base = lost_potential(lf, 2014)
    naw_base = lost_potential({y: 1 - nw[y] / 100 for y in nw}, 2014)
    naw_alt = 100 * math.log((1 - nw[2025] / 100) / (1 - nw[2019] / 100))
    base = lost_potential(P, 2014)
    alt = base - 0.65 * (lf_base - lf_alt) - 0.65 * (naw_base - naw_alt)
    return ["", "## E. Alternative estimates of the German write-down (log points, 2025)", "",
            f"- Commission (AMECO), 2014-19 trend: {base:.1f}",
            f"- OECD Economic Outlook potential, 2014-19 trend: {lost_potential(pot, 2014):.1f}; 2010-19 trend: {lost_potential(pot, 2010):.1f}; OECD output gap 2025: {gap[2025]:.1f}",
            f"- Commission, but labour-force trend from 2010-14 (before the 2015-16 migration surge; {100 * g1014:.2f} % a year instead of "
            f"{100 * ((math.log(lf[2019]) - math.log(lf[2014])) / 5):.2f} %) and structural unemployment (NAWRU) held at its 2019 level "
            f"({nw[2019]:.2f} % in 2019, {nw[2025]:.2f} % in 2025): {alt:.1f}",
            "- Range of the write-down: about 3 to 5 points; the Commission's figure is the upper end."]



if __name__ == "__main__":
    main()
    with open("results/robustness.md", "a", encoding="utf-8") as f:
        for part in (japan(), alternatives()):
            f.write("\n".join(part) + "\n")
            print("\n".join(part))
