"""Validation of the plenary word fields: random keyword-in-context samples per field and period,
on the same de-hyphenated, lower-cased text and with the same tenancy filter as plenum_attention.py.
Run from repository root: python3 scripts/plenum_kwic.py
Writes results/plenum_kwic.md (for reading) and results/plenum_kwic.csv (for coding: id, field, period, year, context)."""
import csv, glob, random, re, sys
sys.path.insert(0, "scripts")
from plenum_attention import FIELDS, TENANCY
random.seed(1)
N = 50
F = glob.glob("data/raw/cppbt/txt/files/txt_protokoll-gesamt/*.txt")
yr = lambda f: int(re.search(r"_(\d{4})-\d{2}-\d{2}_", f).group(1))
PERIODS = ((1980, 1983), (2003, 2005), (2023, 2025))
texts = {}
for f in F:
    if any(lo <= yr(f) <= hi for lo, hi in PERIODS):
        t = re.sub(r"-\n", "", open(f, encoding="utf-8", errors="ignore").read())
        texts[f] = re.sub(r"\s+", " ", t)
L = [f"# Plenary word fields: random samples ({N} per field and period, seed 1)", ""]
rows = []
for k in ("U", "R", "S"):
    pat = re.compile(FIELDS[k])
    for lo, hi in PERIODS:
        hits = []
        for f, t in texts.items():
            if not lo <= yr(f) <= hi:
                continue
            tl = t.lower()
            for m in pat.finditer(tl):
                if m.group(0).startswith("kündigungsschutz") and TENANCY.search(tl[max(0, m.start() - 100): m.end() + 100]):
                    continue
                hits.append((yr(f), t[max(0, m.start() - 150): m.end() + 150]))
        sample = random.sample(hits, min(N, len(hits)))
        L += [f"## {k}, {lo}-{hi} ({len(hits)} hits)", ""]
        for i, (y, c) in enumerate(sample):
            rid = f"{k}-{lo}-{i + 1:02d}"
            rows.append({"id": rid, "field": k, "period": f"{lo}-{hi}", "year": y, "context": c})
            L.append(f"{rid} ({y}) …{c}…")
        L.append("")
open("results/plenum_kwic.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
with open("results/plenum_kwic.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["id", "field", "period", "year", "context"]); w.writeheader(); w.writerows(rows)
print(len(rows))
