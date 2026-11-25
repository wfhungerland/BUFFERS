"""Convert the Harvard-style manuscript into Phenomenal World house style.

In-text (Author Year) citations become numbered footnotes in Chicago notes style:
the first citation of a source gives the full reference with a link, later ones a short form.
No reference list; unnumbered headings; short dek; methods note folded into footnotes.

Run from repository root:
  python3 scripts/to_pw_style.py manuscript/lost_in_transmission_v2_harvard.md manuscript/lost_in_transmission_pw.md
"""
import re
import sys

sys.path.insert(0, "scripts")
from pw_notes import NOTES  # noqa: E402

src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()
head, rest = s.split("## 1. Buying time, again", 1)
body, rest2 = ("## 1. Buying time, again" + rest).split("[^refugees]:", 1)
fndefs = "[^refugees]:" + rest2.split("## Methods note")[0]

names = sorted({k.rsplit(" ", 1)[0] for k in NOTES}, key=len, reverse=True)
name_re = "|".join(re.escape(n) for n in names)
seen = set()


def cite(key):
    if key not in NOTES:
        raise SystemExit(f"no note for {key}")
    full, short, url = NOTES[key]
    if key in seen:
        return short
    seen.add(key)
    return (full.rstrip(".") + f", <{url}>.") if url else full


def keys_in(text):
    out = []
    for m in re.finditer(rf"({name_re})((?:,? (?:19|20)\d\d[a-z]?)+)", text):
        out += [f"{m.group(1)} {y}" for y in re.findall(r"(?:19|20)\d\d[a-z]?", m.group(2))]
    return out


METHODS = {
    "table": "Lost capacity is the fall in the output gap, the distance between actual and potential output, from its last peak to its trough; an episode requires a fall of at least two points. The ratio is the change in the registered unemployment rate of the Federal Employment Agency, measured on dependent civilian employees, over the same years, divided by that fall. Before 2009 it ranged from 0.29 to 1.08; for 2022-25 it is 0.38 for all registered unemployed and 0.27 for German nationals only. Code and data are available from the author.",
    "figure": "Same method as Table 1, but with the ILO unemployment rate, which is available for all five countries and runs below the German registered rate. Negative German values around 2009 and 2013 reflect the fall in unemployment after the Hartz reforms, which overlaid the cycle.",
    "accounting": "Counterfactual: potential output growing at its 2014-19 trend and the output gap closed. Shortfall of actual output in 2025, in log points: lost potential −5.1, output gap −1.7, total −6.9. With trends from 1995-2019 or 2010-19, lost potential is −4.8 or −5.1. Against the Commission's autumn 2019 forecast (growth in 2019-21 as projected, constant thereafter) it is −5.1. Extrapolating actual GDP rather than potential gives about −10, because output grew faster than potential in 2014-19 as the gap opened. Own calculation from {{European Commission 2026}}; {{European Commission 2019}}",
    "potential": "The split approximates the Commission's production-function method: potential output as trend productivity times capital (weight 0.35) and potential labour (weight 0.65), where potential labour is the labour force times one minus the non-accelerating wage rate of unemployment times hours per worker. Against the 2014-19 trend: labour force −1.4, structural unemployment −1.1, hours −0.3, capital −1.2, trend productivity −1.0. Indicative, not the Commission's own decomposition. {{Havik et al. 2014}}",
    "flows": "Steady-state index u = s/(s+f), with s the monthly risk of entering unemployment from employment subject to social insurance and f the monthly chance of leaving unemployment for a job (annual averages). 2019: s 0.61 %, f 7.41 %; 2022: 0.51 %, 6.14 %; 2025: 0.59 %, 5.65 %. From 2019 to 2025 the index rises from 7.6 to 9.5; with only f changing it would rise to 9.8, with only s changing it would fall to 7.4. From 2022, changing s alone adds 1.1 points and changing f alone 0.6. In 2008-09 the rise came mainly from s. {{Bundesagentur für Arbeit 2025}}",
    "district": "Regression across 380 districts of the change in the AfD's second-vote share, 2021-25, on the share of employees in the secondary sector in 2019 (INKAR 2025, BBSR), the change in the foreign share of the population 2019-23, the share of protection seekers in 2023, the change in the registered unemployment rate 2022-25, and controls for east, city districts, income per head and the AfD share in 2021, with robust standard errors. One standard deviation adds 0.7 points (industry) and 0.2 points (foreign share); unemployment has no effect. The 2019 industry share correlates at 0.96 with the 2026 manufacturing share. Election data: {{Heddesheimer et al. 2025}}",
}

# 1) mark everything with placeholders, so that notes are numbered in reading order
body = body.replace("Own calculation; see the methods note.*", "Own calculation.@@M:table@@*", 1)
body = body.replace("own calculation; see the methods note.*", "own calculation.@@M:figure@@*", 1)
for k in ["accounting", "potential", "flows", "district"]:
    body = body.replace(" (see the methods note)", f"@@M:{k}@@", 1)
body = re.sub(rf"({name_re}) \(((?:19|20)\d\d[a-z]?)\)", lambda m: f"{m.group(1)}@@C:{m.group(1)} {m.group(2)}@@", body)


def paren(m):
    inner = m.group(1)
    ks = keys_in(inner)
    if not ks:
        return m.group(0)
    pre = "Own calculation from " if "own calculation" in inner else ""
    return "@@C:" + pre + "|".join(ks) + "@@"


body = re.sub(r" \(([^()]*?(?:19|20)\d\d[a-z]?[^()]*?)\)", paren, body)
body = re.sub(r"((?:@@[^@]+@@)+)([.,;:])", r"\2\1", body)  # marker after punctuation
body = re.sub(r"^## \d+\. ", "## ", body, flags=re.M)

# 2) resolve in reading order
notes = []
fn_order = re.findall(r"\[\^(refugees|manuf|afd)\]", body)


def resolve_inline(text):
    return re.sub(r"\{\{(.+?)\}\}", lambda m: cite(m.group(1)), text)


def make(m):
    tag = m.group(1)
    if tag.startswith("M:"):
        txt = resolve_inline(METHODS[tag[2:]])
    else:
        c = tag[2:]
        pre = ""
        if c.startswith("Own calculation from "):
            pre, c = "Own calculation from ", c[len("Own calculation from "):]
        txt = pre + "; ".join(cite(k).rstrip(".") for k in c.split("|")) + "."
    notes.append(txt)
    return f"[^n{len(notes)}]"


# existing named footnotes also need resolving in order: handle by inserting their text when the marker appears
named = {}
for lab, txt in re.findall(r"\[\^(\w+)\]: (.+)", fndefs):
    named[lab] = txt


def make_all(m):
    if m.group(0).startswith("[^"):
        lab = m.group(2)
        txt = re.sub(r" \(([^()]*?(?:19|20)\d\d[a-z]?[^()]*?)\)",
                     lambda mm: (" (" + "; ".join(cite(k).rstrip(".") for k in keys_in(mm.group(1))) + ")") if keys_in(mm.group(1)) else mm.group(0),
                     named[lab])
        notes.append(txt)
        return f"[^n{len(notes)}]"
    return make(m)


body = re.sub(r"@@([^@]+)@@|\[\^(refugees|manuf|afd)\]", make_all, body)
head = head.replace("## How Germany buys time with demography and a hiring freeze, and why its growth model has no coalition left to change it",
                    "## How Germany buys time with demography and a hiring freeze")
# merge adjacent markers into one note (Chicago: one note per place), then renumber
def merge(m):
    ids = [int(x) for x in re.findall(r"\[\^n(\d+)\]", m.group(0))]
    first = ids[0]
    for k in ids[1:]:
        notes[first - 1] = notes[first - 1].rstrip() + " " + notes[k - 1]
        notes[k - 1] = None
    return f"[^n{first}]"


body = re.sub(r"(?:\[\^n\d+\]){2,}", merge, body)
order = {}
for old in re.findall(r"\[\^n(\d+)\]", body):
    order.setdefault(int(old), len(order) + 1)
body = re.sub(r"\[\^n(\d+)\]", lambda m: f"[^n{order[int(m.group(1))]}]", body)
notes = [notes[old - 1] for old in sorted(order, key=order.get)]
notes_md = "\n\n".join(f"[^n{i}]: {t}" for i, t in enumerate(notes, 1))
open(out, "w", encoding="utf-8").write(head + body.rstrip() + "\n\n" + notes_md + "\n")
left = re.findall(r"\([A-Z][^()]{2,60} (?:19|20)\d\d[a-z]?\)", body)
print(len(notes), "footnotes;", len(seen), "sources;", "unconverted:", left[:3])
