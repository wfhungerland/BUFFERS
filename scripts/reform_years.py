"""Robustness of the reform pattern: annual analysis of core cuts, 1965-2026.

Unit: calendar year of Bundestag passage. Outcome: at least one enacted cut to a core institution in that year
(items with direction = cut and target = core in coding/reform_coding_v2.yaml, inside the episode windows and in
`outside_windows`). Variants: all core cuts; without pensions (area d); without the 1986 strike-neutrality rule
(industrial-conflict law). Regressors: rise in the registered unemployment rate over the previous three years
(u_t - u_{t-3}), level of unemployment, fall in the output gap over three years, change of federal government in
the year or the year before, and an indicator for SPD-led governments.
Tests: difference in mean Δu between cut and non-cut years with a permutation p-value (10,000 draws);
logit of the cut indicator on Δu (and controls); episode-level variants of the window and overlap rule.

Run from repository root: python3 scripts/reform_years.py
Writes results/reform_years.md
"""
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import yaml

sys.path.insert(0, "scripts")
import okun_episodes_intl as oi  # noqa: E402
import okun_gap as og  # noqa: E402

# Federal governments (chancellor's party; date the new government took office).
GOV = [(1966, "CDU", "grand"), (1969, "SPD", "SPD-FDP"), (1982, "CDU", "CDU-FDP"), (1998, "SPD", "SPD-Greens"),
       (2005, "CDU", "grand"), (2009, "CDU", "CDU-FDP"), (2013, "CDU", "grand"), (2021, "SPD", "SPD-Greens-FDP"),
       (2025, "CDU", "CDU-SPD")]


def items():
    d = yaml.safe_load(open("coding/reform_coding_v2.yaml"))
    rows = []
    for e in d["episodes"]:
        for it in e["items"]:
            rows.append({**it, "source": "window"})
    for it in d["outside_windows"]:
        rows.append({**it, "source": "outside"})
    out = []
    for r in rows:
        y = str(r.get("bundestag_passed", ""))[:4]
        if not y.isdigit():
            continue
        out.append({"year": int(y), "direction": r.get("direction"), "target": r.get("target"), "area": str(r.get("area")),
                    "law": (r["law"]["short"] if isinstance(r.get("law"), dict) else str(r.get("law")))[:60],
                    "confirmed": str(r.get("confirmed")), "source": r["source"]})
    return pd.DataFrame(out)


def main():
    it = items()
    core = it[(it.direction == "cut") & (it.target == "core")]
    dep, _ = og.ba_rates()
    gap = oi.splice_de(oi.ameco("AVGDGP"))
    years = range(1968, 2027)
    y = pd.DataFrame(index=years)
    y["u"] = [dep.get(t) for t in years]
    y["du3"] = [dep.get(t, np.nan) - dep.get(t - 3, np.nan) if dep.get(t) is not None else np.nan for t in years]
    y.loc[2026, "du3"] = dep.get(2025) - dep.get(2023)  # 2026: last two complete years
    y["gapfall3"] = [gap.get(t - 3, np.nan) - gap.get(t, np.nan) for t in years]
    y["newgov"] = [int(any(g[0] in (t, t - 1) for g in GOV)) for t in years]
    y["spd"] = [next(g[1] for g in reversed(GOV) if g[0] <= t) == "SPD" for t in years]
    y["spd"] = y.spd.astype(int)
    variants = {
        "All core cuts": core,
        "Without pensions": core[~core.area.str.contains("d")],
        "Without pensions and strike rule": core[~core.area.str.contains("d") & ~core.law.str.contains("116")],
    }
    rng = np.random.default_rng(1)
    L = ["# Core cuts by year and the rise in unemployment, 1968-2026", "",
         "Core cuts: enacted laws coded cut/core in coding/reform_coding_v2.yaml, inside and outside the episode windows. "
         "Δu3 = registered unemployment rate in t minus t-3 (pp). Permutation p-value: share of 10,000 random relabellings "
         "of cut years with a difference in mean Δu3 at least as large.", "",
         "## Core-cut years", "", "| Year | Laws | Δu3 (pp) | u (%) |", "|---|---|---|---|"]
    for t, g in core.groupby("year"):
        L.append(f"| {t} | {'; '.join(g.law)} | {y.du3.get(t, np.nan):+.1f} | {y.u.get(t, np.nan):.1f} |")
    L += ["", "## Tests", "", "| Variant | Cut years | Mean Δu3 cut years | Mean Δu3 other years | Permutation p | "
          "Logit coef. on Δu3 (s.e.) | Logit with gap fall, new government, SPD-led: Δu3 coef. (s.e.) |", "|---|---|---|---|---|---|---|"]
    for name, c in variants.items():
        y["cut"] = y.index.isin(c.year.unique()).astype(int)
        z = y.dropna(subset=["du3", "gapfall3"])
        a, b = z[z.cut == 1].du3, z[z.cut == 0].du3
        obs = a.mean() - b.mean()
        perm = [(lambda s: z.du3[s == 1].mean() - z.du3[s == 0].mean())(rng.permutation(z.cut.values)) for _ in range(10000)]
        p = np.mean(np.array(perm) >= obs)
        m1 = smf.logit("cut ~ du3", data=z).fit(disp=0)
        try:
            m2 = smf.logit("cut ~ du3 + gapfall3 + newgov + spd", data=z).fit(disp=0)
            c2 = f"{m2.params['du3']:+.2f} ({m2.bse['du3']:.2f})"
        except Exception as ex:  # noqa: BLE001
            c2 = f"not estimable ({type(ex).__name__})"
        L.append(f"| {name} | {int(z.cut.sum())} of {len(z)} | {a.mean():+.2f} | {b.mean():+.2f} | {p:.3f} | "
                 f"{m1.params['du3']:+.2f} ({m1.bse['du3']:.2f}) | {c2} |")
    L += ["", "## Core-cut years with falling or stable unemployment (Δu3 ≤ 0.5)", ""]
    for t, g in core.groupby("year"):
        if y.du3.get(t, 9) <= 0.5:
            L.append(f"- {t}: {'; '.join(g.law)} (Δu3 {y.du3.get(t):+.1f}; areas {', '.join(g.area)})")
    L += ["", "## Episode-level variants", "",
          "| Variant | Episodes with core cut | Rise in unemployment in those episodes | Episodes without |", "|---|---|---|---|"]
    eps = oi.episodes(gap)
    du = {e: dep[e[1]] - dep[e[0]] for e in eps}

    def ep_cuts(c, lag, overlap_later):
        res = set()
        for t in c.year:
            hits = [e for e in eps if e[0] <= t <= e[1] + lag]
            if hits:
                res.add(hits[-1] if overlap_later else hits[0])
        return res
    for vname, c in variants.items():
        for lag in (1, 2, 3):
            for ol in (False, True):
                s = ep_cuts(c, lag, ol)
                cut = sorted(s)
                L.append(f"| {vname}; window trough+{lag}; overlap to {'later' if ol else 'earlier'} | "
                         + ", ".join(f"{a}-{str(b)[2:]}" for a, b in cut) + " | "
                         + ", ".join(f"{du[e]:+.1f}" for e in cut) + " | "
                         + ", ".join(f"{a}-{str(b)[2:]} ({du[(a, b)]:+.1f})" for a, b in eps if (a, b) not in s) + " |")
    open("results/reform_years.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
