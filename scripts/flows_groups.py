"""Inflow risk and exit chance by group, and steady-state decomposition per group (and per Land if available).

Data: BA Statistik, "Chancen und Risiken am Arbeitsmarkt nach Personengruppen", December 2025
(annual averages of monthly rates, 2007-2025). Germany from data/raw/ba_flows/flows_de.csv (parsed with
scripts/parse_chancen_risiken.py); Länder from data/raw/ba_flows/laender/cr_XX.xlsx if present.
s = risk of becoming unemployed out of employment subject to social insurance (% per month),
f = chance of leaving unemployment for a job on the first labour market (% per month),
u* = s / (s + f): a steady-state index, not the official rate.
Decomposition: change in u* when only s moves (f held at the base year) and when only f moves.

Run from repository root:  python3 scripts/flows_groups.py
Writes results/flows_groups.md
"""
import glob
import os
import sys

import pandas as pd

sys.path.insert(0, "scripts")
S_VAR, F_VAR = "zugangsrisiko_aus_svb_pct_monatsdurchschnitt", "abgangschance_in_besch_1am_pct_monatsdurchschnitt"
GROUPS = {"insgesamt": "All", "unter_25": "Under 25", "25_bis_u55": "25 to 54", "55_plus": "55 and over",
          "deutsche": "Germans", "auslaender": "Foreigners", "frauen": "Women", "maenner": "Men"}
LAND = {"01": "Schleswig-Holstein", "02": "Hamburg", "03": "Niedersachsen", "04": "Bremen", "05": "Nordrhein-Westfalen",
        "06": "Hessen", "07": "Rheinland-Pfalz", "08": "Baden-Württemberg", "09": "Bayern", "10": "Saarland", "11": "Berlin",
        "12": "Brandenburg", "13": "Mecklenburg-Vorpommern", "14": "Sachsen", "15": "Sachsen-Anhalt", "16": "Thüringen"}


def ustar(s, f):
    return 100 * s / (s + f)


def decomp(s, f, a, b):
    u0, u1 = ustar(s[a], f[a]), ustar(s[b], f[b])
    return u0, u1, ustar(s[b], f[a]) - u0, ustar(s[a], f[b]) - u0


def rows(table, keys, labels, a, b):
    out = [f"| | s {a} | s {b} | f {a} | f {b} | Δf (%) | u* {a} | u* {b} | only s | only f | share of f |", "|---" * 11 + "|"]
    for k in keys:
        if k not in table:
            continue
        s, f = table[k]
        if a not in s or b not in s:
            continue
        u0, u1, ds, df = decomp(s, f, a, b)
        sh = df / (ds + df) if (ds + df) != 0 else float("nan")
        out.append(f"| {labels[k]} | {s[a]:.2f} | {s[b]:.2f} | {f[a]:.2f} | {f[b]:.2f} | {100 * (f[b] / f[a] - 1):+.0f} "
                   f"| {u0:.1f} | {u1:.1f} | {ds:+.1f} | {df:+.1f} | {sh:.0%} |")
    return out


def table(path, groups):
    import parse_chancen_risiken as pcr
    rec = pcr.parse(path, os.path.basename(path))
    sj = s_jan_nov(path, groups)
    t = {}
    for g in groups:
        s = sj.get(g, {})
        f = {r["year"]: r["value"] for r in rec if r["group"] == g and r["variable"] == F_VAR}
        if s and f:
            t[g] = (s, f)
    return t


def s_jan_nov(path, groups):
    """Inflow risk as the mean of the monthly values January-November: the December rate for 2025 needs
    January 2026 employment and is not yet published. Same months in every year, so years stay comparable."""
    import datetime
    import openpyxl
    import parse_chancen_risiken as pcr
    wb = openpyxl.load_workbook(path, data_only=True)
    out = {}
    for key, (var, grp, mcol, rcol, rvar) in pcr.SHEETS.items():
        if rvar != S_VAR or grp not in groups:
            continue
        name = key if key in wb.sheetnames else next(x for x in wb.sheetnames if x.startswith(key + " ") and x.endswith("Tab"))
        ws, acc = wb[name], {}
        for r in range(11, ws.max_row + 1):
            b, v = ws[f"B{r}"].value, ws[f"{rcol}{r}"].value
            if isinstance(b, datetime.datetime) and b.month <= 11 and isinstance(v, (int, float)):
                acc.setdefault(b.year, []).append(v)
        out[grp] = {y: sum(v) / len(v) for y, v in acc.items() if len(v) == 11}
    return out


def germany():
    return table("data/raw/ba_flows/analyse-d-chancen-risiken-personen-d-0-202512.xlsx", GROUPS)


def laender():
    t = {}
    for p in sorted(glob.glob("data/raw/ba_flows/laender/cr_*.xlsx")):
        x = table(p, ["insgesamt"])
        if x:
            t[os.path.basename(p)[3:5]] = x["insgesamt"]
    return t


def main():
    t = germany()
    L = ["# Inflow risk and exit chance by group (BA, Chancen und Risiken, December 2025)", "",
         "s = monthly risk of becoming unemployed from a job (%), f = monthly chance of leaving unemployment for a job (%),",
         "u* = s/(s+f) (two-state steady-state index; flows from and to non-participation are shown separately below). s is the January-November mean in every year (December 2025 not yet published); f the annual mean. 'only s' / 'only f': change in u* if only that rate had moved. 'share of f' = only f / (only s + only f).", ""]
    for g in list(t):  # base: mean of 2015-18, to avoid starting from the 2019 peak of f
        s_, f_ = t[g]
        s_["2015-18"] = sum(s_[y] for y in range(2015, 2019)) / 4
        f_["2015-18"] = sum(f_[y] for y in range(2015, 2019)) / 4
    for a, b in ((2019, 2025), ("2015-18", 2025), (2022, 2025), (2008, 2009)):
        L += [f"## {a} to {b}", ""] + rows(t, GROUPS, GROUPS, a, b) + [""]
    s_, f_ = t["insgesamt"]
    L += ["## Series, all unemployed", "", "| Year | s | f |", "|---|---|---|"]
    L += [f"| {y} | {s_.get(y, float('nan')):.2f} | {f_[y]:.2f} |" for y in range(2007, 2026) if y in f_]
    L += ["", "## All inflows and outflows (ANBA annual counts, thousands; stock = annual mean)", "",
          "Exit rates per month = annual exits / 12 / mean stock. 'Other' exits: into training, measures, inactivity, sickness, "
          "retirement and unknown; 'other' inflows: from training, measures, inactivity and abroad.", "",
          "| Year | Stock | Inflows | of which from a job | Exits | of which into a job | Exit rate into a job (%/month) | Exit rate, other (%/month) |",
          "|---|---|---|---|---|---|---|---|"]
    a = pd.read_csv("data/raw/ba_flows/flows_de.csv")
    a = a[a.group == "insgesamt"].drop_duplicates(["year", "variable"]).pivot(index="year", columns="variable", values="value")
    for y in range(2017, 2026):
        r = a.loc[y]
        st, ex, ej = r.bestand_alo_jd, r.abgang_alo_insgesamt, r.abgang_alo_in_besch_1am_inkl_ausb
        L.append(f"| {y} | {st / 1e3:,.0f} | {r.zugang_alo_insgesamt / 1e3:,.0f} | {r.zugang_alo_aus_besch_1am_inkl_ausb / 1e3:,.0f} "
                 f"| {ex / 1e3:,.0f} | {ej / 1e3:,.0f} | {100 * ej / 12 / st:.1f} | {100 * (ex - ej) / 12 / st:.1f} |")
    L.append("")
    lt = laender()
    if lt:
        L += [f"## Länder, 2019 to 2025 ({len(lt)} of 16)", ""] + rows(lt, sorted(lt), LAND, 2019, 2025) + [""]
        L += [f"## Länder, 2022 to 2025", ""] + rows(lt, sorted(lt), LAND, 2022, 2025) + [""]
    open("results/flows_groups.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
