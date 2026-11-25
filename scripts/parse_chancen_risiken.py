#!/usr/bin/env python3
"""Parse BA 'Chancen und Risiken am Arbeitsmarkt nach Personengruppen - Deutschland' (xlsx)
into annual rows appended by build_ba_flows_csv.py. Returns list of dicts."""
import datetime, openpyxl, warnings
warnings.filterwarnings("ignore")

SHEETS = {  # sheet: (variable, group, monthly-count col, annual-rate col, rate variable)
    "1.1 Alo-ZuR-Tab": ("zugang_alo_aus_svb_1am_inkl_ausb", "insgesamt", "M", "R", "zugangsrisiko_aus_svb_pct_monatsdurchschnitt"),
    "1.4 Alo-AbCh-Tab": ("abgang_alo_in_besch_1am_inkl_ausb_cr", "insgesamt", "N", "S", "abgangschance_in_besch_1am_pct_monatsdurchschnitt"),
}
for num, grp in (("2", "deutsche"), ("3", "auslaender"), ("4", "frauen"), ("5", "maenner"), ("6", "unter_25"), ("7", "25_bis_u55"), ("8", "55_plus")):
    SHEETS[num + ".1"] = ("zugang_alo_aus_svb_1am_inkl_ausb", grp, "I", "M", "zugangsrisiko_aus_svb_pct_monatsdurchschnitt")
    SHEETS[num + ".3"] = ("abgang_alo_in_besch_1am_inkl_ausb_cr", grp, "I", "M", "abgangschance_in_besch_1am_pct_monatsdurchschnitt")

def parse(path, label):
    wb = openpyxl.load_workbook(path, data_only=True)
    out = []
    for key, (var, grp, mcol, rcol, rvar) in SHEETS.items():
        name = key if key in wb.sheetnames else next(s for s in wb.sheetnames if s.startswith(key + " ") and s.endswith("Tab"))
        ws = wb[name]
        sums, cnt, annual_rate, annual_avg = {}, {}, {}, {}
        for r in range(11, ws.max_row + 1):
            b = ws[f"B{r}"].value
            if isinstance(b, datetime.datetime):
                v = ws[f"{mcol}{r}"].value
                if isinstance(v, (int, float)):
                    sums[b.year] = sums.get(b.year, 0) + v; cnt[b.year] = cnt.get(b.year, 0) + 1
            elif isinstance(b, str) and b.strip().endswith("1)") and "gleitend" not in b:
                y = int(b[:4]); rv = ws[f"{rcol}{r}"].value; av = ws[f"{mcol}{r}"].value
                if isinstance(rv, (int, float)): annual_rate[y] = rv
                if isinstance(av, (int, float)): annual_avg[y] = av
        src = f"{label}, Tab. {name}"
        for y in sorted(sums):
            if cnt[y] == 12:
                if y in annual_avg and abs(annual_avg[y] * 12 - sums[y]) > 12:
                    raise SystemExit(f"check failed {name} {y}: {annual_avg[y]*12} vs {sums[y]}")
                out.append({"year": y, "variable": var, "group": grp, "value": round(sums[y]), "source": src + f" (Summe 12 Monatswerte, Spalte {mcol})"})
        for y in sorted(annual_rate):
            if cnt.get(y) == 12:
                out.append({"year": y, "variable": rvar, "group": grp, "value": round(annual_rate[y], 3), "source": src + f" (Jahreswert = Monatsdurchschnitt, Spalte {rcol})"})
    return out

if __name__ == "__main__":
    import sys
    for r in parse(sys.argv[1], "test"):
        if r["year"] in (2007, 2008, 2009, 2019, 2025): print(r["year"], r["variable"], r["group"], r["value"])
