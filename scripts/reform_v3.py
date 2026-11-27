"""Reform analysis on the systematic, cycle-blind coding v3 (coding/reform_coding_v3.yaml, 166 laws 1965-2026).

Target (from the law's area): core = a dismissal protection, b unemployment benefit, c sick pay, e short-time work;
pension = d; margin = f fixed-term/agency/marginal, g minimum income support, h ALMP, i minimum wage; other = j.
Outcomes per year: core cut (direction cut), variants (cut or mixed; size >= 2; size-weighted count), core expansion,
margin cut, pension cut. Second coder (coding/reform_coding_v3_coder2.csv): agreement and robustness.
Regressors: Δu over k years (registered BA rate; ILO rate AMECO ZUTN), lagged level, fiscal controls (change in gross
debt ratio over 3 years, change in unemployment-insurance contribution rate over 3 years, Maastricht years 1992-98),
political controls (coding/politics_annual.csv). Firth logit (scripts/reform_controls.py), out-of-sample 2005-26,
specification curve, stated motives.
Run: python3 scripts/reform_v3.py  -> results/reform_v3.md, figures/fig_speccurve.png
"""
import itertools
import os
import sys

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, "scripts")
import okun_episodes_intl as oi  # noqa: E402
import okun_gap as og  # noqa: E402
from reform_controls import firth  # noqa: E402

AREA_TARGET = {"a": "core", "b": "core", "c": "core", "e": "core", "d": "pension", "f": "margin", "g": "margin",
               "h": "margin", "i": "margin", "j": "other"}
YEARS = list(range(1968, 2027))


def items():
    d = yaml.safe_load(open("coding/reform_coding_v3.yaml"))["items"]
    rows = []
    for it in d:
        y = str(it.get("bundestag_passed", ""))[:4]
        if not y.isdigit():
            continue
        area = str(it.get("area", "")).split(",")[0].strip()[:1]
        mot = it.get("motive_stated") or {}
        rows.append({"id": it["id"], "year": int(y), "area": area, "target": AREA_TARGET.get(area, "other"),
                     "direction": it.get("direction"), "size": int(it.get("size") or 1),
                     "motive": (mot.get("category") if isinstance(mot, dict) else str(mot)) or "",
                     "law": (it["law"].get("short") if isinstance(it.get("law"), dict) else str(it.get("law")))[:70],
                     "confirmed": str(it.get("confirmed"))})
    df = pd.DataFrame(rows)
    c2p = "coding/reform_coding_v3_coder2.csv"
    if os.path.exists(c2p):
        c2 = pd.read_csv(c2p).rename(columns={"direction": "direction2", "size": "size2", "target": "target2"})
        df = df.merge(c2[["id", "direction2", "size2", "target2"]], on="id", how="left")
    return df


def series():
    dep, _ = og.ba_rates()
    ilo = oi.splice_de(oi.ameco("ZUTN"))
    fis = pd.read_csv("coding/fiscal_annual.csv")
    def get(var):
        x = fis[fis.variable == var].drop_duplicates("year").set_index("year").value
        return pd.to_numeric(x, errors="coerce")
    debt = get("gg_gross_debt_pct_gdp_linked")
    uic = get("ui_contribution_rate")
    pol = pd.read_csv("coding/politics_annual.csv").set_index("year")
    s = pd.DataFrame(index=YEARS)
    last = max(k for k in dep)
    for k in (1, 2, 3, 4):
        s[f"du{k}"] = [dep.get(min(t, last), np.nan) - dep.get(t - k, np.nan) for t in YEARS]
        s[f"dilo{k}"] = [ilo.get(min(t, 2025), np.nan) - ilo.get(t - k, np.nan) for t in YEARS]
    s["u_lag"] = [dep.get(t - 1, np.nan) for t in YEARS]
    s["ddebt3"] = [debt.get(t - 1, np.nan) - debt.get(t - 4, np.nan) for t in YEARS]
    s["duic3"] = [uic.get(t, np.nan) - uic.get(t - 3, np.nan) for t in YEARS]
    s["maastricht"] = [int(1992 <= t <= 1998) for t in YEARS]
    for c in ["cabinet_left_share", "grand_coalition", "bundesrat_opp_strict_majority", "new_government",
              "years_to_next_election", "far_right_vote_share", "bundesrat_opposition_majority"]:
        s[c] = pol[c].reindex(YEARS).astype(float)
    s["bundesrat_opp_strict_majority"] = s.bundesrat_opp_strict_majority.fillna(s.bundesrat_opposition_majority)
    s["cabinet_left_share"] = s.cabinet_left_share / 100
    return s


def outcome(it, target, dirs, min_size=1, dircol="direction", sizecol="size", targetcol="target"):
    x = it[(it[targetcol] == target) & (it[dircol].isin(dirs)) & (it[sizecol] >= min_size)]
    return pd.Series([int(t in set(x.year)) for t in YEARS], index=YEARS)


def fit(y, s, cols):
    z = pd.concat([y.rename("y"), s[cols]], axis=1).dropna()
    X = np.column_stack([np.ones(len(z))] + [z[c].values for c in cols])
    b, se, ll = firth(z.y.values.astype(float), X)
    return b, se, len(z), int(z.y.sum())


def main():
    it = items()
    s = series()
    L = ["# Reform analysis on the systematic coding v3", ""]
    L += [f"Items: {len(it)}; by target and direction:", "", "| Target | " + " | ".join(sorted(it.direction.dropna().unique())) + " |",
          "|---|" + "---|" * it.direction.nunique()]
    tab = pd.crosstab(it.target, it.direction)
    for t in tab.index:
        L.append(f"| {t} | " + " | ".join(str(tab.loc[t].get(c, 0)) for c in sorted(it.direction.dropna().unique())) + " |")
    # agreement with coder 2
    if "direction2" in it:
        a = it.dropna(subset=["direction2"])
        agree = (a.direction == a.direction2).mean()
        po = agree
        cats = sorted(set(a.direction) | set(a.direction2))
        pe = sum((a.direction == c).mean() * (a.direction2 == c).mean() for c in cats)
        kappa = (po - pe) / (1 - pe)
        cut1, cut2 = a.direction == "cut", a.direction2 == "cut"
        tg = (a.target == a.target2).mean() if "target2" in a else np.nan
        L += ["", f"Second coder (n = {len(a)}): agreement on direction {agree:.0%} (Cohen's kappa {kappa:.2f}); on 'cut' vs other "
              f"{(cut1 == cut2).mean():.0%}; on target {tg:.0%}; size within one step {((a["size"] - a["size2"]).abs() <= 1).mean():.0%}."]
    # core-cut years
    core = it[(it.target == "core") & (it.direction.isin(["cut", "deregulation"]))]
    L += ["", "## Core cuts (coder 1; cut or deregulation of a core institution)", "", "| Year | Laws | Size | Stated motive | Δu3 (pp) |", "|---|---|---|---|---|"]
    for t, g in core.groupby("year"):
        L.append(f"| {t} | {'; '.join(g.law)} | {', '.join(map(str, g['size']))} | {', '.join(g.motive)} | {s.du3.get(t, np.nan):+.1f} |")
    mot = core.motive.value_counts()
    L += ["", "Stated motives of core cuts: " + "; ".join(f"{k} {v}" for k, v in mot.items()) + "."]
    # main models
    y_core = outcome(it, "core", ["cut", "deregulation"])  # loosening dismissal protection is a cut for employees
    specs = {"Δu3": ["du3"], "Δu3 + level": ["du3", "u_lag"], "Δu3 × level": ["du3", "u_lag", "du3_x_u"],
             "Δu3 ILO": ["dilo3"], "Δu3 + fiscal": ["du3", "ddebt3", "duic3", "maastricht"],
             "Δu3 + fiscal + political": ["du3", "ddebt3", "duic3", "maastricht", "cabinet_left_share", "grand_coalition",
                                          "bundesrat_opp_strict_majority", "new_government", "years_to_next_election"]}
    s["du3_x_u"] = s.du3 * s.u_lag
    L += ["", "## Core cuts: Firth logit, annual 1968-2026", "", "| Model | Coefficients (s.e.) | N (cut years) |", "|---|---|---|"]
    for name, cols in specs.items():
        b, se, n, k = fit(y_core, s, cols)
        L.append(f"| {name} | " + "; ".join(f"{c} {b[i + 1]:+.2f} ({se[i + 1]:.2f})" for i, c in enumerate(cols)) + f" | {n} ({k}) |")
    # other outcomes
    L += ["", "## Other outcomes, Δu3 only and with fiscal controls", "", "| Outcome | Δu3 only | Δu3 with fiscal controls | Years with event |", "|---|---|---|---|"]
    outs = {"Core cut (coder 1)": y_core, "Core cut or mixed": outcome(it, "core", ["cut", "deregulation", "mixed"]),
            "Core cut, size ≥ 2": outcome(it, "core", ["cut", "deregulation"], 2), "Core cut, size 3": outcome(it, "core", ["cut", "deregulation"], 3), "Core expansion": outcome(it, "core", ["expansion"]),
            "Margin cut": outcome(it, "margin", ["cut"]), "Margin deregulation": outcome(it, "margin", ["deregulation"]),
            "Pension cut": outcome(it, "pension", ["cut"])}
    if "direction2" in it:
        outs["Core cut (coder 2 direction, coder 2 target)"] = outcome(it.dropna(subset=["direction2"]), "core", ["cut", "deregulation"], 1, "direction2", "size2", "target2")
    for name, y in outs.items():
        b1, se1, n1, k1 = fit(y, s, ["du3"])
        b2, se2, n2, k2 = fit(y, s, ["du3", "ddebt3", "duic3", "maastricht"])
        L.append(f"| {name} | {b1[1]:+.2f} ({se1[1]:.2f}) | {b2[1]:+.2f} ({se2[1]:.2f}) | {k1} of {n1} |")
    # out of sample
    pre = [t for t in YEARS if t <= 2004]
    post = [t for t in YEARS if t >= 2005]
    z = pd.concat([y_core.rename("y"), s[["du3", "dilo3"]]], axis=1)
    L += ["", "## Out of sample 2005-2026 (model fitted on 1968-2004)", ""]
    for col in ("du3", "dilo3"):
        zp = z.loc[pre].dropna()
        b, se, _ = firth(zp.y.values.astype(float), np.column_stack([np.ones(len(zp)), zp[col].values]))
        zq = z.loc[post].dropna()
        p = 1 / (1 + np.exp(-(b[0] + b[1] * zq[col].values)))
        dist = np.array([1.0])
        for q in p:  # Poisson-binomial distribution of the number of cut years
            dist = np.convolve(dist, [1 - q, q])
        k = int(zq.y.sum())
        L.append(f"- {col}: expected core-cut years {p.sum():.1f}, observed {k}, P(observed or fewer) {dist[:k + 1].sum():.3f}.")
    # specification curve
    rows = []
    defs = {"cut": (["cut", "deregulation"], 1), "cut+mixed": (["cut", "deregulation", "mixed"], 1), "cut size≥2": (["cut", "deregulation"], 2)}
    ctrl = {"none": [], "fiscal": ["ddebt3", "duic3", "maastricht"],
            "political": ["cabinet_left_share", "grand_coalition", "bundesrat_opp_strict_majority", "new_government", "years_to_next_election"]}
    ctrl["both"] = ctrl["fiscal"] + ctrl["political"]
    for (dn, (dirs, ms)), k, meas, (cn, cc), period in itertools.product(defs.items(), (1, 2, 3, 4), ("du", "dilo"), ctrl.items(), ("all", "pre2005")):
        y = outcome(it, "core", dirs, ms)
        ss = s if period == "all" else s.loc[[t for t in YEARS if t <= 2004]]
        yy = y.loc[ss.index]
        cols = [f"{meas}{k}"] + cc
        if period == "pre2005":
            cols = [c for c in cols if c != "grand_coalition"]
        try:
            b, se, n, ev = fit(yy, ss, cols)
            rows.append({"def": dn, "k": k, "measure": meas, "controls": cn, "period": period, "b": b[1], "se": se[1]})
        except Exception:  # noqa: BLE001
            pass
    sc = pd.DataFrame(rows)
    sc["z"] = sc.b / sc.se
    sc.to_csv("results/reform_speccurve.csv", index=False)
    L += ["", f"## Specification curve ({len(sc)} specifications)", "",
          f"Positive coefficient: {(sc.b > 0).mean():.0%}; significant at 10 %: {(sc.z > 1.645).mean():.0%}; at 5 %: {(sc.z > 1.96).mean():.0%}. "
          f"Median coefficient {sc.b.median():+.2f}.",
          "By Δu window: " + "; ".join(f"{k} years {g.z.gt(1.96).mean():.0%} significant at 5 %" for k, g in sc.groupby("k")) + ".",
          "By controls: " + "; ".join(f"{k} {g.z.gt(1.96).mean():.0%}" for k, g in sc.groupby("controls")) + ".",
          "By period: " + "; ".join(f"{k} {g.z.gt(1.96).mean():.0%}" for k, g in sc.groupby("period")) + ".",
          "By measure: " + "; ".join(f"{k} {g.z.gt(1.96).mean():.0%}" for k, g in sc.groupby("measure")) + "."]
    # figure
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    q = sc.sort_values("b").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7, 3.2))
    col = ["#257de0" if z > 1.96 else "#9fc3ef" if z > 1.645 else "#bbbbbb" for z in q.z]
    ax.vlines(q.index, q.b - 1.96 * q.se, q.b + 1.96 * q.se, color="#dddddd", lw=1)
    ax.scatter(q.index, q.b, c=col, s=10, zorder=3)
    ax.axhline(0, color="#666666", lw=0.8)
    ax.set_ylabel("Coefficient on Δu (Firth logit)")
    ax.set_xlabel("Specifications, sorted by coefficient")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#e6e6e6", lw=0.8)
    fig.text(0, -0.06, f"{len(sc)} specifications: outcome definition, Δu window (1-4 years), registered or ILO rate, controls (none, fiscal, political, both), "
             "full sample or 1968-2004.\nDark blue: p < 0.05; light blue: p < 0.10; grey: not significant. Bars: 95 % intervals.", fontsize=7, color="#666666")
    fig.tight_layout()
    fig.savefig("figures/fig_speccurve.png", dpi=200, bbox_inches="tight", facecolor="white")
    # EPL validation
    fis = pd.read_csv("coding/fiscal_annual.csv")
    L += ["", "## External validation: OECD employment protection index (regular and temporary contracts)", ""]
    for var in ("epl_regular_v1", "epl_temporary_v1", "epl_regular_v4", "epl_temporary_v4"):
        e = fis[fis.variable == var].drop_duplicates("year").set_index("year").value.astype(float).sort_index()
        ch = e.diff()
        falls = [int(t) for t in ch.index if ch[t] < -0.01]
        rises = [int(t) for t in ch.index if ch[t] > 0.01]
        L.append(f"- {var} ({int(e.index.min())}-{int(e.index.max())}): falls in {falls}; rises in {rises}.")
    dereg = it[(it.direction.isin(["cut", "deregulation"])) & (it.area.isin(["a", "f"]))]
    L.append("- Coded dismissal-protection cuts and fixed-term/agency deregulation (coder 1), years: " + ", ".join(map(str, sorted(dereg.year.unique()))) + ".")
    open("results/reform_v3.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
