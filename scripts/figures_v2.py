"""Figures for the working paper v2 (static PNG/SVG for print; light surface).

fig_salience: three panels with a common time axis: registered unemployment rate; share naming unemployment as
              a top problem (Politbarometer); unemployment talk in the Bundestag (hits per million words).
fig_judgements: net balance of judgements on the country's and one's own economic situation, 1977-2024.
fig_topics: five topic groups in Bundestag debates by decade.
Palette: reference categorical slots (validated with the dataviz validator, light mode); every series is
direct-labelled because four slots sit below 3:1 contrast on white.

Run from repository root: python3 scripts/figures_v2.py
"""
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, "scripts")
import okun_gap as og  # noqa: E402

C = ["#257de0", "#f47230", "#00b894", "#f2a600", "#ee7fac"]
INK, INK2, GRID = "#191919", "#666666", "#e6e6e6"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": INK2, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False})


EPS = ((1965, 1967), (1973, 1975), (1979, 1983), (1991, 1993), (2001, 2005), (2007, 2009), (2011, 2013), (2017, 2020), (2022, 2025))


def style(ax):
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def save(fig, name):
    for ext in ("png", "svg"):
        fig.savefig(f"figures/{name}.{ext}", dpi=200, bbox_inches="tight", facecolor="white")


def salience():
    dep, _ = og.ba_rates()
    pb = pd.read_csv("results/politbarometer.csv", index_col=0)
    pl = pd.read_csv("results/plenum_topics.csv", index_col=0)
    u = pd.Series(dep).sort_index()
    u = u[(u.index >= 1977) & (u.index <= 2025)]
    fig, axes = plt.subplots(3, 1, figsize=(7, 6.4), sharex=True)
    panels = [(u, "Registered unemployment rate (%)", C[0]),
              (pb.unemployment.dropna(), "Survey: unemployment named as a top problem (% of respondents)", C[1]),
              (pl.unemployment[(pl.index >= 1977) & (pl.index <= 2025)], "Bundestag: unemployment talk (hits per million words)", C[2])]
    for ax, (s, title, col) in zip(axes, panels):
        ax.plot(s.index, s.values, color=col, lw=2, solid_capstyle="round")
        ax.set_title(title, loc="left", fontsize=9, color=INK)
        ax.set_ylim(bottom=0)
        style(ax)
        last = s.index.max()
        ax.annotate(f"{s[last]:.0f}" if s[last] > 10 else f"{s[last]:.1f}", (last, s[last]), xytext=(4, 0),
                    textcoords="offset points", va="center", fontsize=8, color=INK)
        for x0, x1 in EPS:
            ax.axvspan(x0, x1, color="#f2f2f2", zorder=0, lw=0)
    axes[-1].set_xlim(1976, 2027)
    axes[0].set_title("Registered unemployment rate, dependent civilian labour force (%)", loc="left", fontsize=9, color=INK)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.text(0.01, 0.005, "Shaded: downturns by the rule of Table 3 (1979-83, 1991-93, 2001-05, 2007-09, 2011-13, 2017-20, 2022-25). Sources: Bundesagentur\n"
             "für Arbeit; Forschungsgruppe Wahlen (2026), Politbarometer ZA2391 (from 1986); Fobbe (2026), CPP-BT; own calculation.", fontsize=7, color=INK2)
    save(fig, "fig_salience")


def judgements():
    pb = pd.read_csv("results/politbarometer.csv", index_col=0)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    for col, lab, c in (("own_net", "Own economic situation", C[1]), ("country_net", "Economic situation in Germany", C[0])):
        s = pb[col].dropna()
        ax.plot(s.index, s.values, color=c, lw=2, marker="o", ms=3)
        ax.annotate(lab, (s.index.max(), s.iloc[-1]), xytext=(6, 0), textcoords="offset points", va="center", fontsize=8, color=INK)
    ax.plot([1976, 2025], [0, 0], color=INK2, lw=0.8)
    for x0, x1 in EPS:
        ax.axvspan(x0, x1, color="#f2f2f2", zorder=0, lw=0)
    ax.axvline(1990.5, color=INK2, lw=0.8, ls=":")
    ax.annotate("West Germany | Germany", (1990.5, 73), ha="center", fontsize=7, color=INK2)
    for y in (1982, 1993, 2003, 2009, 2024):
        ax.annotate(f"{y}: {pb.own_net[y]:+.0f} / {pb.country_net[y]:+.0f}", (y, pb.country_net[y]), xytext=(34, 0) if y == 2003 else (0, -14),
                    textcoords="offset points", ha="left" if y == 2003 else "center", va="center" if y == 2003 else "baseline", fontsize=7, color=INK2)
    ax.set_ylabel("% good minus % bad")
    ax.set_xlim(1976, 2034)
    ax.set_ylim(-68, 78)
    ax.set_xticks([1980, 1990, 2000, 2010, 2020])
    ax.spines["bottom"].set_bounds(1976, 2025)
    style(ax)
    fig.text(0, -0.04, "Shaded: downturns by the rule of Table 3. Labels: own / country net balance in selected years; 1978 own value missing.\nSource: Forschungsgruppe Wahlen (2026), "
             "Politbarometer 1977-2024 (ZA2391 v17.0.0), weighted; own calculation.", fontsize=7, color=INK2)
    fig.tight_layout()
    save(fig, "fig_judgements")


def topics():
    sys.path.insert(0, "scripts")
    from plenum_topics import GROUPS
    pl = pd.read_csv("results/plenum_topics.csv", index_col=0)
    pl = pl[(pl.index >= 1950) & (pl.index <= 2025)]
    dec = pd.DataFrame({g: pl[ks].sum(axis=1) for g, ks in GROUPS.items()}).rolling(3, center=True, min_periods=2).mean()
    fig, ax = plt.subplots(figsize=(7, 3.8))
    nudge = {"Buffers": -7, "Frame": 7}
    for (g, s), c in zip(dec.items(), C):
        ax.plot(s.index, s.values, color=c, lw=2)
        ax.annotate(g, (2025, s.iloc[-1]), xytext=(6, nudge.get(g, 0)), textcoords="offset points", va="center", fontsize=8, color=INK)
    for x0, x1 in EPS:
        ax.axvspan(x0, x1, color="#f2f2f2", zorder=0, lw=0)
    ax.set_ylabel("Hits per million words (3-year mean)")
    ax.set_ylim(bottom=0)
    ax.set_xlim(1950, 2046)
    ax.set_xticks([1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020])
    ax.spines["bottom"].set_bounds(1950, 2025)
    style(ax)
    fig.text(0, -0.04, "1950-2025, three-year centred mean; shaded: downturns. Groups sum dictionaries of different breadth. Source: Fobbe (2026), CPP-BT; own calculation.",
             fontsize=7, color=INK2)
    fig.tight_layout()
    save(fig, "fig_topics")


if __name__ == "__main__":
    salience()
    judgements()
    topics()
