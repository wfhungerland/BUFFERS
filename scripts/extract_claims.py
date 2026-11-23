"""Extract every sentence with a number from the manuscript into inventory/claims.csv.

Run from the repository root:  python3 scripts/extract_claims.py
Existing status columns are kept for claims whose text is unchanged.
"""
import csv, re, os

SRC = "manuscript/lost_in_transmission.md"
OUT = "inventory/claims.csv"
FIELDS = ["id", "section", "claim", "cited_source", "status", "checked_against", "note"]

old = {}
if os.path.exists(OUT):
    for r in csv.DictReader(open(OUT, encoding="utf-8")):
        old[r["claim"]] = r

text = open(SRC, encoding="utf-8").read().split("\n## References")[0]
section, rows, n = "", [], 0
for line in text.split("\n"):
    if line.startswith("## "):
        section = line[3:].strip()
        continue
    if not line.strip() or line.startswith(("#", "|", "!", "|---")):
        continue
    for s in re.split(r"(?<=[.;])\s+(?=[A-Z“(])", line):
        if not re.search(r"\d", re.sub(r"\[\^\d+\]|\((?:[^()]*\d{4}[a-z]?[^()]*)\)", "", s)):
            continue
        n += 1
        cites = "; ".join(re.findall(r"\(([^()]*\b(?:19|20)\d\d[a-z]?[^()]*)\)", s))
        prev = old.get(s.strip(), {})
        rows.append({
            "id": f"C{n:03d}", "section": section, "claim": s.strip(),
            "cited_source": cites,
            "status": prev.get("status", "offen"),
            "checked_against": prev.get("checked_against", ""),
            "note": prev.get("note", ""),
        })
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, FIELDS); w.writeheader(); w.writerows(rows)
print(len(rows), "claims written to", OUT)
