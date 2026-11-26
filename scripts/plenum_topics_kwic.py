"""Validation samples for the topic dictionaries of plenum_topics.py: 20 random hits per topic and period
(1990-2005, 2019-2025), same text preparation and tenancy filter. Seed 2.
Run from repository root: python3 scripts/plenum_topics_kwic.py  -> results/plenum_topics_kwic.csv"""
import csv, glob, random, re, sys
sys.path.insert(0, "scripts")
from plenum_topics import TOPICS, TENANCY
random.seed(2)
N, PERIODS = 20, ((1990, 2005), (2019, 2025))
yr = lambda f: int(re.search(r"_(\d{4})-\d{2}-\d{2}_", f).group(1))
F = [f for f in glob.glob("data/raw/cppbt/txt/files/txt_protokoll-gesamt/*.txt") if any(a <= yr(f) <= b for a, b in PERIODS)]
texts = {f: re.sub(r"\s+", " ", re.sub(r"-\n", "", open(f, encoding="utf-8", errors="ignore").read())) for f in F}
rows = []
for k, pat in TOPICS.items():
    if k == "unemployment":
        continue
    p = re.compile(pat)
    for a, b in PERIODS:
        hits = []
        for f, t in texts.items():
            if not a <= yr(f) <= b:
                continue
            tl = t.lower()
            for m in p.finditer(tl):
                if m.group(0).startswith("kündigungsschutz") and TENANCY.search(tl[max(0, m.start() - 100): m.end() + 100]):
                    continue
                hits.append((yr(f), t[max(0, m.start() - 150): m.end() + 150]))
        for i, (y, c) in enumerate(random.sample(hits, min(N, len(hits)))):
            rows.append({"id": f"{k}-{a}-{i + 1:02d}", "topic": k, "period": f"{a}-{b}", "year": y, "context": c})
with open("results/plenum_topics_kwic.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["id", "topic", "period", "year", "context"]); w.writeheader(); w.writerows(rows)
print(len(rows))
