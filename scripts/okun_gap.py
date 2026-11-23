"""Okun pass-through per German recession episode, measured against the output gap.

Answers referee finding 1: does the 2022-25 episode show unusually low
unemployment pass-through once output losses are measured against current
potential (output gap) instead of a pre-crisis trend?

Sources (downloaded at run time, cached in data/raw/, not committed):
- Output gap: European Commission, AMECO, variable AVGDGP
  (gap between actual and potential GDP, % of potential), Autumn 2026 forecast vintage.
  West Germany (D_W) until 1990, Germany (DEU) from 1991.
- Output gap, robustness: OECD Economic Outlook, measure GAP.
- Registered unemployment rate: Bundesagentur fuer Arbeit, "Arbeitslosigkeit im Zeitverlauf"
  (product 562, reporting month October 2026), annual averages,
  rate on dependent civilian labour force (1950-1990 West, 1991- Germany),
  plus rate on all civilian labour force for 1992-.
- ILO unemployment rate: AMECO ZUTN (Eurostat definition).

Run from repository root:  python3 scripts/okun_gap.py
Writes results/okun_gap_episodes.csv and results/okun_gap_episodes.md
"""
import csv
import os
import re
import urllib.request

import openpyxl

RAW = "data/raw"
OUT = "results"
YEARS = list(range(1960, 2028))
AMECO_URL = ("https://ec.europa.eu/economy_finance/ameco/wq/series?fullVariable=1.0.0.0.{var}"
             "&countries=DEU,D_W&years=" + ",".join(map(str, YEARS)) +
             "&lastYear=0&defaultCountries=0")
OECD_URL = ("https://sdmx.oecd.org/public/rest/data/OECD.ECO.MAD,DSD_EO@DF_EO,/DEU.GAP.A"
            "?startPeriod=1990&format=csvfilewithlabels")
BA_URL = "https://newswolf.eu/claude-daten/GD/arbeit/destatis/ba_alo_dwo.xlsx"

# Method A (main): output-gap peak to output-gap trough (AMECO), unemployment change over the
# same years and with a one-year lag (trough + 1), because unemployment lags output.
PEAK_TROUGH = [("1966/67", 1965, 1967), ("1974/75", 1973, 1975), ("1981/82", 1979, 1983),
               ("1992/93", 1991, 1993), ("2008/09", 2008, 2009), ("2020", 2019, 2020),
               ("2022-25", 2022, 2025)]
# Method B (robustness): last year before real GDP fell (t0), fixed windows of 2 and 3 years.
EPISODES = [("1966/67", 1966), ("1974/75", 1974), ("1981/82", 1981), ("1992/93", 1992),
            ("2008/09", 2008), ("2020", 2019), ("2022-25", 2022)]
WINDOWS = [2, 3]


def fetch(url, path):
    os.makedirs(RAW, exist_ok=True)
    if not os.path.exists(path):
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research script)"})
        with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
            f.write(r.read())
    return path


def ameco(var):
    html = open(fetch(AMECO_URL.format(var=var), f"{RAW}/ameco_{var}.html"), encoding="utf-8").read()
    out = {}
    for row in re.findall(r"<tr.*?</tr>", html, re.S):
        cells = [re.sub(r"<[^>]+>", "", c).strip() for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
        if cells and cells[0] in ("Germany", "West Germany"):
            out[cells[0]] = {y: float(v) for y, v in zip(YEARS, cells[3:]) if v}
    # splice: West Germany until 1990, Germany from 1991
    return {y: (out["West Germany"] if y <= 1990 else out["Germany"]).get(y) for y in YEARS}


def oecd_gap():
    rows = csv.DictReader(open(fetch(OECD_URL, f"{RAW}/oecd_gap_deu.csv"), encoding="utf-8"))
    return {int(r["TIME_PERIOD"]): float(r["OBS_VALUE"]) for r in rows}


def ba_rates():
    wb = openpyxl.load_workbook(fetch(BA_URL, f"{RAW}/ba_alo_dwo.xlsx"), read_only=True, data_only=True)
    dep, civ = {}, {}
    for r in wb["Tabelle 1.1"].iter_rows(values_only=True):  # West, 1950-1990
        if isinstance(r[0], int) and isinstance(r[7], (int, float)):
            dep[r[0]] = float(r[7])
    for r in wb["Tabelle 2.1.1"].iter_rows(values_only=True):  # Germany, 1991-
        if isinstance(r[0], int):
            if isinstance(r[7], (int, float)):
                dep[r[0]] = float(r[7])
            if isinstance(r[4], (int, float)):
                civ[r[0]] = float(r[4])
    return dep, civ


def main():
    gap = ameco("AVGDGP")
    ilo_raw = ameco("ZUTN")
    ogap = oecd_gap()
    dep, civ = ba_rates()
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for name, t0 in EPISODES:
        for w in WINDOWS:
            t1 = t0 + w
            if t1 > 2025:
                continue
            dg = gap[t1] - gap[t0]
            du = dep[t1] - dep[t0]
            r = {"episode": name, "t0": t0, "t1": t1,
                 "gap_t0": gap[t0], "gap_t1": gap[t1], "d_gap": round(dg, 2),
                 "u_reg_t0": dep[t0], "u_reg_t1": dep[t1], "d_u_reg": round(du, 2),
                 "beta_reg": round(du / -dg, 2) if dg < 0 else "",
                 "d_u_ilo": round(ilo_raw[t1] - ilo_raw[t0], 2) if ilo_raw.get(t0) and ilo_raw.get(t1) else "",
                 "beta_ilo": "", "d_gap_oecd": "", "beta_reg_oecd": ""}
            if r["d_u_ilo"] != "" and dg < 0:
                r["beta_ilo"] = round(r["d_u_ilo"] / -dg, 2)
            if t0 in ogap and t1 in ogap:
                dgo = ogap[t1] - ogap[t0]
                r["d_gap_oecd"] = round(dgo, 2)
                r["beta_reg_oecd"] = round(du / -dgo, 2) if dgo < 0 else ""
            rows.append(r)
    with open(f"{OUT}/okun_gap_episodes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    pt = []
    for name, a, b in PEAK_TROUGH:
        dg = gap[b] - gap[a]
        du0 = dep[b] - dep[a]
        du1 = dep.get(b + 1, float("nan")) - dep[a] if b + 1 <= 2025 else None
        pt.append({"episode": name, "peak": a, "trough": b, "gap_peak": gap[a], "gap_trough": gap[b],
                   "u_reg_peak": dep[a], "u_reg_trough": dep[b],
                   "d_gap": round(dg, 2), "d_u_reg": round(du0, 2), "beta_reg": round(du0 / -dg, 2),
                   "d_u_reg_lag1": "" if du1 is None else round(du1, 2),
                   "beta_reg_lag1": "" if du1 is None else round(du1 / -dg, 2)})
    with open(f"{OUT}/okun_gap_peak_trough.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, pt[0].keys())
        w.writeheader()
        w.writerows(pt)

    # Counterfactual of the essay, recomputed on the gap
    g25, g22 = gap[2025], gap[2022]
    lines = ["# Okun pass-through per episode, measured against the output gap", "",
             "## Method A: gap peak to gap trough", "",
             "| Episode | Gap peak → trough | Δ gap (pp) | Δ u reg. same years (pp) | β | Δ u reg. to trough+1 (pp) | β lag 1 |",
             "|---|---|---|---|---|---|---|"]
    for r in pt:
        lines.append(f"| {r['episode']} | {r['peak']} ({r['gap_peak']:+.2f}) → {r['trough']} ({r['gap_trough']:+.2f}) | "
                     f"{r['d_gap']} | {r['d_u_reg']} | {r['beta_reg']} | {r['d_u_reg_lag1']} | {r['beta_reg_lag1']} |")
    lines += ["", "## Method B: fixed windows from the last pre-recession year", "",
             "Registered rate on dependent civilian labour force (BA). Gap: AMECO Autumn 2026, % of potential.", "",
             "| Episode | Window | Δ gap (pp) | Δ u registered (pp) | β registered | Δ u ILO (pp) | β ILO | Δ gap OECD | β reg. (OECD gap) |",
             "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['episode']} | {r['t0']}–{r['t1']} | {r['d_gap']} | {r['d_u_reg']} | {r['beta_reg']} | "
                     f"{r['d_u_ilo']} | {r['beta_ilo']} | {r['d_gap_oecd']} | {r['beta_reg_oecd']} |")
    lines += ["", "## Counterfactual in the essay, recomputed", "",
              f"- Gap 2022: {g22:+.2f} %, gap 2025: {g25:+.2f} % (AMECO). Change: {g25 - g22:+.2f} pp.",
              f"- Okun β = 0.4 on that change implies Δu ≈ {0.4 * (g22 - g25):+.2f} pp.",
              f"- Okun β = 0.4 on the 2025 gap level implies u about {0.4 * -g25:.2f} pp above its gap-neutral level.",
              f"- Observed registered rate (dependent basis): {dep[2022]} % (2022) → {dep[2025]} % (2025), "
              f"Δ {dep[2025] - dep[2022]:+.1f} pp; all-civilian basis {civ[2022]} → {civ[2025]} %.",
              f"- Essay's version: β = 0.4 × shortfall > 5 % against the 2019-projected path ⇒ about +2 pp (\"missing million\")."]
    open(f"{OUT}/okun_gap_episodes.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
