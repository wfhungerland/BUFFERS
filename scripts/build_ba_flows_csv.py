#!/usr/bin/env python3
"""Build tidy CSV /home/user/buffers/data/raw/ba_flows/flows_de.csv from the raw files
fetched by fetch_ba_flows.py (ANBA Jahreszahlen xlsx, BA Zeitreihen PDF, Destatis 21211-0004).
Columns: year, variable, group, value, source. Run with python3 -I."""
import csv, glob, os, re, subprocess
import openpyxl

RAW = "/home/user/buffers/data/raw/ba_flows"
OUT = os.path.join(RAW, "flows_de.csv")
rows = []

def add(y, var, grp, val, src):
    rows.append({"year": y, "variable": var, "group": grp, "value": val, "source": src})

def de_row(ws):
    for r in ws.iter_rows(max_row=20, values_only=True):
        if r and r[0] == "Deutschland":
            return [int(float(x)) if isinstance(x, (int, float)) or (isinstance(x, str) and x.strip().replace('.', '').isdigit()) else x for x in r[1:]]
    raise ValueError("no Deutschland row")

for f in sorted(glob.glob(os.path.join(RAW, "anba-arbeitsmarkt-d-0-*12.xlsx"))):
    y = int(re.search(r"-(\d{4})12\.xlsx$", f).group(1))
    src = f"BA Statistik, ANBA Jahreszahlen {y} - Teil Arbeitsmarkt ({os.path.basename(f)})"
    wb = openpyxl.load_workbook(f, read_only=True)
    z = de_row(wb["II.1.3"])  # cols 1..14
    add(y, "zugang_alo_insgesamt", "insgesamt", z[0], src + ", Tab. II.1.3 Sp.1")
    add(y, "zugang_alo_aus_erwerbstaetigkeit_ohne_ausb", "insgesamt", z[1], src + ", Tab. II.1.3 Sp.2")
    add(y, "zugang_alo_aus_besch_1am_ohne_ausb", "insgesamt", z[2], src + ", Tab. II.1.3 Sp.3")
    add(y, "zugang_alo_aus_selbstaendigkeit", "insgesamt", z[4], src + ", Tab. II.1.3 Sp.5")
    add(y, "zugang_alo_aus_betr_ausbildung", "insgesamt", z[8], src + ", Tab. II.1.3 Sp.9")
    add(y, "zugang_alo_aus_besch_1am_inkl_ausb", "insgesamt", z[2] + z[8], src + ", Tab. II.1.3 Sp.3+Sp.9 (BA-Headline-Abgrenzung)")
    a = de_row(wb["II.1.5"])  # cols 1..16
    add(y, "abgang_alo_insgesamt", "insgesamt", a[0], src + ", Tab. II.1.5 Sp.1")
    add(y, "abgang_alo_in_erwerbstaetigkeit_ohne_ausb", "insgesamt", a[1], src + ", Tab. II.1.5 Sp.2")
    add(y, "abgang_alo_in_besch_1am_ohne_ausb", "insgesamt", a[2], src + ", Tab. II.1.5 Sp.3")
    add(y, "abgang_alo_in_selbstaendigkeit", "insgesamt", a[5], src + ", Tab. II.1.5 Sp.6")
    add(y, "abgang_alo_in_betr_ausbildung", "insgesamt", a[9], src + ", Tab. II.1.5 Sp.10")
    add(y, "abgang_alo_in_besch_1am_inkl_ausb", "insgesamt", a[2] + a[9], src + ", Tab. II.1.5 Sp.3+Sp.10 (BA-Headline-Abgrenzung)")
    for sheet, var in (("II.1.4", "zugang_alo_insgesamt"), ("II.1.6", "abgang_alo_insgesamt")):
        p = de_row(wb[sheet])
        for i, g in enumerate(["insgesamt", "maenner", "frauen", "unter_25", "25_bis_u55", "55_plus", "auslaender", "schwerbehinderte"]):
            if g != "insgesamt":
                add(y, var, g, p[i], src + f", Tab. {sheet} Sp.{i+1}")

# BA Zeitreihen PDF, Tabelle 7.3 (Bestand, Zugang, Abgang insgesamt, 2007-2025)
pdf = os.path.join(RAW, "analyse-arbeitsmarkt-zeitreihen-d-0-202512.pdf")
if os.path.exists(pdf):
    txt = subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
    i = txt.find("7.3 Tabelle: Bestand, Zugang, Abgang")
    src = "BA Statistik, Der Arbeitsmarkt in Deutschland - Zeitreihen bis 2025, Tab. 7.3"
    have = {(r["year"], r["variable"]) for r in rows}
    for line in txt[i:i + 8000].splitlines():
        m = re.match(r"\s+(20\d\d)\s+([\d.]+)\s+[\d,]+\s+[\d,]+\s+([\d.]+)\s+([\d.]+)\s", line)
        if m:
            y = int(m.group(1)); n = lambda s: int(s.replace(".", ""))
            add(y, "bestand_alo_jd", "insgesamt", n(m.group(2)), src)
            if (y, "zugang_alo_insgesamt") not in have:
                add(y, "zugang_alo_insgesamt", "insgesamt", n(m.group(3)), src)
            if (y, "abgang_alo_insgesamt") not in have:
                add(y, "abgang_alo_insgesamt", "insgesamt", n(m.group(4)), src)
    # indicators quoted in the Jahresrueckblick text (Zeitreihen bis 2025, p. 9)
    add(2025, "zugangsrisiko_aus_svb_pct_monatsdurchschnitt", "insgesamt", 0.59, src.replace("Tab. 7.3", "Jahresrueckblick S. 9 (Text)"))
    add(2024, "zugangsrisiko_aus_svb_pct_monatsdurchschnitt", "insgesamt", 0.57, src.replace("Tab. 7.3", "Jahresrueckblick S. 9 (Text)"))
    add(2025, "abgangschance_in_svb_1am_pct", "insgesamt", 5.65, src.replace("Tab. 7.3", "Jahresrueckblick S. 9 (Text)"))

# Destatis Berufsbildungsstatistik 21211-0004 (Stichtag 31.12., NOT the BIBB 30.09. survey)
dc = os.path.join(RAW, "destatis_21211-0004_flat.csv")
if os.path.exists(dc):
    for r in csv.DictReader(open(dc, encoding="utf-8"), delimiter=";"):
        if r["2_variable_attribute_label"] == "Insgesamt" and r["4_variable_attribute_label"] == "Insgesamt":
            g = {"Insgesamt": "insgesamt", "Deutsche": "deutsche", "Ausländer": "auslaender"}[r["3_variable_attribute_label"]]
            add(int(r["time"]), "neu_abgeschl_ausbildungsvertraege_destatis_3112", g, int(r["value"]),
                "Destatis GENESIS 21211-0004 Berufsbildungsstatistik (Neuabschluesse Jan-Dez)")

# BA 'Chancen und Risiken am Arbeitsmarkt nach Personengruppen' (monthly, summed to years)
import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_chancen_risiken import parse as parse_cr
for f in sorted(glob.glob(os.path.join(RAW, "analyse-d-chancen-risiken-personen-d-0-*.xlsx")))[-1:]:
    stamp = re.search(r"-(\d{6})\.xlsx$", f).group(1)
    rows += parse_cr(f, f"BA Statistik, Chancen und Risiken am Arbeitsmarkt nach Personengruppen - Deutschland, Stand {stamp} ({os.path.basename(f)})")

# optional extra rows maintained by hand (same columns), e.g. older years from PDFs
extra = os.path.join(RAW, "flows_de_manual.csv")
if os.path.exists(extra):
    rows += list(csv.DictReader(open(extra, encoding="utf-8")))

rows.sort(key=lambda r: (r["variable"], r["group"], int(r["year"])))
with open(OUT, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["year", "variable", "group", "value", "source"])
    w.writeheader(); w.writerows(rows)
print(len(rows), "rows ->", OUT)
