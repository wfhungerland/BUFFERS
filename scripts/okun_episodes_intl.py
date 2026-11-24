"""Figure 1 and Table 1: unemployment pass-through per recession, Germany against USA, FRA, ITA, GBR.

Episode = a fall of the output gap by at least 2 percentage points from a local peak to the next
local trough (AMECO, Autumn 2026 vintage; West Germany until 1990, Germany from 1991).
Pass-through beta = rise in the unemployment rate between the peak and the trough year,
divided by the fall in the output gap (percentage points of unemployment per point of lost capacity).

Unemployment: ILO definition (AMECO ZUTN) for the cross-country figure; registered rate on dependent
civilian labour force (BA) for the German Table 1 (results/okun_gap_peak_trough.csv, from okun_gap.py).

Run from repository root:  python3 scripts/okun_episodes_intl.py
Writes results/okun_episodes_intl.csv, results/table1.md, figures/figure1_passthrough.png/.svg
"""
import csv
import os
import re
import urllib.request

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAW, OUT, FIG = "data/raw", "results", "figures"
YEARS = list(range(1960, 2028))
NAMES = {"DEU": "Germany", "D_W": "West Germany", "USA": "United States", "FRA": "France",
         "ITA": "Italy", "GBR": "United Kingdom"}
URL = ("https://ec.europa.eu/economy_finance/ameco/wq/series?fullVariable=1.0.0.0.{v}&countries="
       + ",".join(NAMES) + "&years=" + ",".join(map(str, YEARS)) + "&lastYear=0&defaultCountries=0")
MIN_FALL = 2.0
LAST = 2025


def ameco(v):
    os.makedirs(RAW, exist_ok=True)
    path = f"{RAW}/ameco_{v}_6c.html"
    if not os.path.exists(path):
        req = urllib.request.Request(URL.format(v=v), headers={"User-Agent": "Mozilla/5.0 (research script)"})
        with urllib.request.urlopen(req, timeout=120) as r, open(path, "wb") as f:
            f.write(r.read())
    out = {}
    for row in re.findall(r"<tr.*?</tr>", open(path, encoding="utf-8").read(), re.S):
        c = [re.sub(r"<[^>]+>", "", x).strip() for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.S)]
        if c and c[0] in NAMES.values():
            out[c[0]] = {y: float(x) for y, x in zip(YEARS, c[3:]) if x not in ("", "NA")}
    return out


def splice_de(d):
    w, g = d["West Germany"], d["Germany"]
    return {y: (w.get(y) if y <= 1990 else g.get(y)) for y in YEARS if (w.get(y) if y <= 1990 else g.get(y)) is not None}


def episodes(gap):
    ys = sorted(y for y in gap if y <= LAST)
    eps, i = [], 0
    while i < len(ys) - 1:
        y = ys[i]
        if (i == 0 or gap[y] >= gap[ys[i - 1]]) and gap[y] > gap[ys[i + 1]]:  # local peak (first year allowed)
            j = i + 1
            while j < len(ys) - 1 and gap[ys[j + 1]] < gap[ys[j]]:
                j += 1
            t = ys[j]
            if gap[y] - gap[t] >= MIN_FALL:
                eps.append((y, t))
            i = j
        i += 1
    return eps


def main():
    gap, u = ameco("AVGDGP"), ameco("ZUTN")
    series = {"DEU": (splice_de(gap), splice_de(u))}
    for iso in ("USA", "FRA", "ITA", "GBR"):
        series[iso] = (gap[NAMES[iso]], u[NAMES[iso]])
    rows = []
    for iso, (g, un) in series.items():
        for a, b in episodes(g):
            if a in un and b in un:
                dg, du = g[b] - g[a], un[b] - un[a]
                rows.append({"country": iso, "peak": a, "trough": b, "d_gap": round(dg, 2),
                             "d_u_ilo": round(du, 2), "beta_ilo": round(du / -dg, 2)})
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/okun_episodes_intl.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, rows[0].keys())
        w.writeheader()
        w.writerows(rows)

    # Figure 2: pass-through by episode, Germany highlighted (house rule: Germany coloured, others grey)
    os.makedirs(FIG, exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=200)
    ax.axhline(0, color="#c3c2b7", lw=0.8, zorder=1)
    others = [r for r in rows if r["country"] != "DEU"]
    de = [r for r in rows if r["country"] == "DEU"]
    ax.scatter([r["trough"] for r in others], [r["beta_ilo"] for r in others], s=28, color="#a9a8a2",
               edgecolor="white", linewidth=1.2, zorder=2, label="United States, France, Italy, United Kingdom")
    ax.plot([r["trough"] for r in de], [r["beta_ilo"] for r in de], color="#2a78d6", lw=1, zorder=3)
    ax.scatter([r["trough"] for r in de], [r["beta_ilo"] for r in de], s=46, color="#2a78d6",
               edgecolor="white", linewidth=1.2, zorder=4, label="Germany (West Germany until 1990)")
    for r in de:
        lab = f"{r['peak']}-{str(r['trough'])[2:]}"
        off = (-4, 9) if r["peak"] == 1965 else (6, 4)
        ax.annotate(lab, (r["trough"], r["beta_ilo"]), xytext=off, textcoords="offset points",
                    fontsize=8, color="#0b0b0b")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color("#c3c2b7")
    ax.tick_params(colors="#52514e")
    ax.grid(axis="y", color="#ecebe7", lw=0.6)
    ax.set_axisbelow(True)
    ax.set_ylabel("Percentage points of unemployment\nper point of lost capacity", color="#52514e")
    ax.set_xlabel("Year of output-gap trough", color="#52514e")
    ax.legend(frameon=False, loc="upper left", fontsize=8)
    fig.text(0.01, 0.005, "Source: European Commission, AMECO (Autumn 2026): output gap, ILO unemployment rate. Own calculation.\n"
             "Episodes: output gap falls by at least 2 points from peak to trough. Labels: peak to trough year.",
             fontsize=6.5, color="#52514e")
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(f"{FIG}/figure1_passthrough.png")
    fig.savefig(f"{FIG}/figure1_passthrough.svg")

    # Table 1 for Germany: registered rate (BA, dependent basis) from okun_gap.py
    t = list(csv.DictReader(open(f"{OUT}/okun_gap_peak_trough.csv", encoding="utf-8")))
    md = ["| Episode | Output gap, peak → trough (% of potential) | Δ gap (pp) | Registered unemployment, peak → trough (%) | Δu (pp) | Δu per point of lost capacity |",
          "|---|---|---|---|---|---|"]
    for r in t:
        a, b = int(r["peak"]), int(r["trough"])
        md.append(f"| {r['episode']} | {a}: {float(r['gap_peak']):+.1f} → {b}: {float(r['gap_trough']):+.1f} | "
                  f"{float(r['d_gap']):.1f} | {float(r['u_reg_peak']):.1f} → {float(r['u_reg_trough']):.1f} | {float(r['d_u_reg']):+.1f} | {float(r['beta_reg']):.2f} |")
    open(f"{OUT}/table1.md", "w", encoding="utf-8").write("\n".join(md) + "\n")
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
