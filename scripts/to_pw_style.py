"""Convert the Harvard-style manuscript into Phenomenal World house style:
in-text (Author Year) citations become numbered footnotes with the full reference
(and a link where known); no reference list; unnumbered headings; methods note folded
into footnotes.

Run from repository root:
  python3 scripts/to_pw_style.py manuscript/lost_in_transmission_v2_harvard.md manuscript/lost_in_transmission_pw.md
"""
import re
import sys

src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding="utf-8").read()

head, rest = s.split("## 1. Buying time, again", 1)
rest = "## 1. Buying time, again" + rest
body, rest2 = rest.split("[^refugees]:", 1)
fndefs = "[^refugees]:" + rest2.split("## Methods note")[0]
refs = s.split("## References", 1)[1].strip()

# reference entries -> citation key
PERSON = {"Baccaro, L., M. Blyth": "Baccaro, Blyth and Pontusson", "Baccaro, L. and J. Pontusson": "Baccaro and Pontusson",
          "Burda": "Burda and Hunt", "Dullien": "Dullien et al.", "Emmenegger": "Emmenegger et al.",
          "Fitzenberger": "Fitzenberger and Kagerl", "Hassel": "Hassel", "Havik": "Havik et al.",
          "Heddesheimer": "Heddesheimer et al.", "Köcher": "Köcher", "Palier": "Palier and Thelen",
          "Röhl": "Röhl", "Streeck": "Streeck", "Bundesverfassungsgericht": "BVerfG", "Die Bundeswahlleiterin": "Bundeswahlleiterin"}
URL = {
    "European Commission 2026": "https://economy-finance.ec.europa.eu/economic-research-and-databases/economic-databases/ameco-database_en",
    "IAB 2025": "https://iab.de/presseinfo/mit-rund-1-million-offenen-stellen-bleibt-die-personalnachfrage-schwach/",
    "Volkswagen 2024": "https://www.volkswagen-group.com/de/pressemitteilungen/einigung-erzielt-volkswagen-ag-stellt-sich-wettbewerbsfaehig-fuer-die-zukunft-auf-18911",
    "Infratest dimap 2023": "https://www.infratest-dimap.de/umfragen-analysen/bundesweit/umfragen/aktuell/33-jahre-wiedervereinigung/",
    "IWH 2014": "https://www.iwh-halle.de/fileadmin/user_upload/press/press_releases/17-14.pdf",
    "BMAS 2026": "https://www.bmas.de/DE/Service/Presse/Pressemitteilungen/2026/kabinett-beschliesst-arbeitsrechtspaket.html",
    "Destatis 2026a": "https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/05/PD26_N032_42.html",
    "Bundeszentrale für politische Bildung 2025": "https://www.bpb.de/themen/parteien/parteien-in-deutschland/afd/273132/die-programmatik-der-afd/",
    "EY 2026": "https://www.ey.com/de_de/newsroom/2026/01/ey-verbraucherumfrage-2025-2026",
    "Deutscher Bundestag 2026d": "https://www.bundestag.de/dokumente/textarchiv/2026/kw21-de-arbeitszeit-1178888",
}
entries = {}
for e in refs.split("\n\n"):
    e = e.strip()
    m = re.match(r"(.+?) \((?:eds\.\) \()?((?:19|20)\d\d[a-z]?)\):", e)
    if not m:
        continue
    auth, yr = m.group(1), m.group(2)
    key = None
    for k, v in PERSON.items():
        if auth.startswith(k):
            key = v
            break
    if key is None:
        key = auth.split(" (")[0]
    k = f"{key} {yr}"
    if k in URL:
        e = e.rstrip(".") + f". [Link]({URL[k]})"
    entries[k] = e
names = sorted({k.rsplit(" ", 1)[0] for k in entries}, key=len, reverse=True)
name_re = "|".join(re.escape(n) for n in names)

notes = []


def new_note(text):
    notes.append(text.strip())
    return f"[^n{len(notes)}]"


def refs_in(text):
    """All (name, year) pairs in a citation string, including '2025b, 2026a' lists."""
    found = []
    for m in re.finditer(rf"({name_re})((?:,? (?:19|20)\d\d[a-z]?)+)", text):
        for y in re.findall(r"(?:19|20)\d\d[a-z]?", m.group(2)):
            found.append(f"{m.group(1)} {y}")
    return found


def note_for(cite):
    keys = refs_in(cite)
    parts = [entries[k] for k in keys if k in entries]
    missing = [k for k in keys if k not in entries]
    if missing:
        raise SystemExit(f"missing reference: {missing} in '{cite}'")
    extra = ""
    if "own calculation" in cite:
        extra = "Own calculation. "
    return new_note(extra + " ".join(p if p.endswith(".") or p.endswith(")") else p + "." for p in parts))


METHODS = {
    "table": "Lost capacity is the fall in the output gap, the distance between actual and potential output, from its last peak to its trough; an episode requires a fall of at least two points. The ratio is the change in the registered unemployment rate of the Federal Employment Agency, measured on dependent civilian employees, over the same years, divided by that fall. Before 2009 it ranged from 0.29 to 1.08; for 2022-25 it is 0.38 for all registered unemployed and 0.27 for German nationals only. Code and data: author's repository.",
    "figure": "Same method as Table 1, but with the ILO unemployment rate, which is available for all five countries and runs below the German registered rate. Negative German values around 2009 and 2013 reflect the fall in unemployment after the Hartz reforms, which overlaid the cycle.",
    "potential": "The split is an approximation of the Commission's production-function method (Havik, K. et al. (2014): The Production Function Methodology for Calculating Potential Growth Rates & Output Gaps. European Economy Economic Papers 535, European Commission, Brussels): potential output as trend productivity times capital (weight 0.35) and potential labour (weight 0.65). Against its 2014-19 trend, German potential output in 2025 is 5.1 points lower: labour force −1.4, structural unemployment −1.1, hours −0.3, capital −1.2, trend productivity −1.0. Indicative only; not the Commission's own decomposition.",
    "decomp": "Real GDP in 2025 compared with its 2014-19 trend, in log points: employment −5.4, hours per worker −0.5, output per hour −4.3 (European Commission, AMECO, autumn 2026; own calculation).",
    "productivity": "Trend productivity accounts for about one of the five points of lost potential; see the note on the decomposition of potential output above.",
    "district": "Regression across 400 districts of the change in the AfD's second-vote share, 2021-25 (GERDA, Heddesheimer, V., H. Sichart, A. Wiedemann and H. Hilbig (2025), Scientific Data 12, doi:10.1038/s41597-025-04811-5), on the change in the registered unemployment rate, 2022-25, the shares of employment in energy-intensive manufacturing and in metal, car and machinery production (March 2026), and controls for east, city districts, income per head and the AfD share in 2021, with robust standard errors. With controls, unemployment has no effect; one standard deviation more energy-intensive or metal employment adds 0.3 or 0.5 points. Employment shares are measured after the shock, so the estimate is descriptive.",
}

# methods-note references, in order of appearance
body = body.replace("Own calculation; see the methods note.*", "Own calculation." + new_note(METHODS["table"]) + "*", 1)
body = body.replace("own calculation; see the methods note.*", "own calculation." + new_note(METHODS["figure"]) + "*", 1)
order = ["potential", "decomp", "productivity", "district"]
for key in order:
    i = body.index(" (see the methods note)")
    body = body[:i] + new_note(METHODS[key]) + body[i + len(" (see the methods note)"):]

# narrative citations: Name (Year)
def narr(m):
    return m.group(1) + note_for(f"{m.group(1)} {m.group(2)}")
body = re.sub(rf"({name_re}) \(((?:19|20)\d\d[a-z]?)\)", narr, body)

# parenthetical citations
def paren(m):
    inner = m.group(1)
    if not refs_in(inner):
        return m.group(0)
    return note_for(inner)
body = re.sub(r" \(([^()]*?(?:19|20)\d\d[a-z]?[^()]*?)\)", paren, body)
# move markers behind following punctuation
body = re.sub(r"((?:\[\^n\d+\])+)([.,;:])", r"\2\1", body)

# citations inside existing footnote texts
def paren_fn(m):
    keys = refs_in(m.group(1))
    if not keys:
        return m.group(0)
    return " (" + "; ".join(entries[k].rstrip(".") for k in keys) + ")"
fndefs = re.sub(r" \(([^()]*?(?:19|20)\d\d[a-z]?[^()]*?)\)", paren_fn, fndefs)

# headings without numbers, short dek
body = re.sub(r"^## \d+\. ", "## ", body, flags=re.M)
head = head.replace("## How Germany buys time with demography and a hiring freeze, and why its growth model has no coalition left to change it",
                    "## How Germany buys time with demography and a hiring freeze")
notes_md = "\n\n".join(f"[^n{i}]: {t}" for i, t in enumerate(notes, 1))
open(out, "w", encoding="utf-8").write(head + body.rstrip() + "\n\n" + fndefs.strip() + "\n\n" + notes_md + "\n")
print(len(notes), "footnotes;", "remaining Harvard-like:", re.findall(r"\([A-Z][^()]{2,60} (?:19|20)\d\d[a-z]?\)", body)[:5])
