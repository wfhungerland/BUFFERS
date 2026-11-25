"""Validation of the plenary word fields: random keyword-in-context samples per field and period.
Run from repository root: python3 scripts/plenum_kwic.py  -> results/plenum_kwic.md"""
import glob, random, re, sys
sys.path.insert(0, "scripts")
from plenum_attention import FIELDS
random.seed(1)
F = glob.glob("data/raw/cppbt/txt/files/txt_protokoll-gesamt/*.txt")
yr = lambda f: int(re.search(r"_(\d{4})-\d{2}-\d{2}_", f).group(1))
L = ["# Plenary word fields: random samples (40 per field and period, seed 1)", ""]
for k in FIELDS:
    pat = re.compile(FIELDS[k])
    for lo, hi in ((2003, 2005), (2023, 2025)):
        hits = []
        for f in [f for f in F if lo <= yr(f) <= hi]:
            t = re.sub(r"\s+", " ", open(f, encoding="utf-8", errors="ignore").read())
            tl = t.lower()
            hits += [(yr(f), t[max(0, m.start() - 110): m.end() + 110]) for m in pat.finditer(tl)]
        L += [f"## {k}, {lo}-{hi} ({len(hits)} hits)", ""] + [f"{i+1}. ({y}) …{c}…" for i, (y, c) in enumerate(random.sample(hits, min(40, len(hits))))] + [""]
open("results/plenum_kwic.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
