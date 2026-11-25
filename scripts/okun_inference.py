"""Okun relation for Germany with uncertainty: annual regressions and alternative episode dating.

1. Annual regression, 1962-2025: change in the registered unemployment rate (BA, dependent civilian
   labour force) on the change in the output gap and its lag, with interaction terms for 2007-21 and for
   2022-25; HAC (Newey-West, 2 lags) standard errors. Gap: AMECO autumn 2026 (West Germany to 1990;
   the 1991 change is dropped because it spans the two series). Variant with the OECD gap (from 1991).
2. Cumulative response: sum of the gap coefficients (contemporaneous + lag) per period, with s.e.
3. Episode table with the rule's dating and with peaks moved to the year before the shock (2008, 2019).

Run from repository root:  python3 scripts/okun_inference.py
Writes results/okun_inference.md
"""
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

sys.path.insert(0, "scripts")
import okun_episodes_intl as oi  # noqa: E402
import okun_gap as og  # noqa: E402


def frame(gap, dep, start):
    d = pd.DataFrame({"gap": pd.Series(gap), "u": pd.Series(dep)}).dropna()
    d = d[(d.index >= start) & (d.index <= 2025)]
    d["du"], d["dg"] = d.u.diff(), d.gap.diff()
    d["dg1"] = d.dg.shift(1)
    d = d.drop(index=[1991, 1992], errors="ignore") if start < 1991 else d
    d["p2"] = ((d.index >= 2007) & (d.index <= 2021)).astype(int)
    d["p3"] = (d.index >= 2022).astype(int)
    return d.dropna()


def cumulative(m, terms):
    names = list(m.params.index)
    r = np.zeros(len(names))
    for t in terms:
        r[names.index(t)] += 1
    est = float(r @ m.params.values)
    se = float(np.sqrt(r @ m.cov_params().values @ r))
    return est, se


def main():
    gap = oi.splice_de(oi.ameco("AVGDGP"))
    dep, _ = og.ba_rates()
    L = ["# Okun relation for Germany with standard errors", "",
         "Dependent variable: annual change in the registered unemployment rate (pp). Regressors: change in the output gap "
         "(pp) this year and last year, interacted with period dummies (base 1962-2006; 2007-21; 2022-25). HAC s.e. (2 lags). "
         "Cumulative response = sum of current and lagged gap coefficients; a negative value means unemployment rises when the gap falls.", ""]
    f = "du ~ dg + dg1 + p2 + p3 + dg:p2 + dg1:p2 + dg:p3 + dg1:p3"
    for label, g, start in (("AMECO gap, 1962-2025", gap, 1961), ("OECD gap, 1993-2025", og.oecd_gap(), 1991)):
        d = frame(g, dep, start)
        if label.startswith("OECD"):
            d["p2"] = ((d.index >= 2007) & (d.index <= 2021)).astype(int)
        m = smf.ols(f, data=d).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
        L += [f"## {label} (N = {int(m.nobs)})", "", "| Period | Cumulative response | s.e. | 90 % interval |", "|---|---|---|---|"]
        for per, terms in (("Base (to 2006)", ["dg", "dg1"]), ("2007-21", ["dg", "dg1", "dg:p2", "dg1:p2"]),
                           ("2022-25", ["dg", "dg1", "dg:p3", "dg1:p3"])):
            e, s = cumulative(m, terms)
            L.append(f"| {per} | {e:+.2f} | {s:.2f} | {e - 1.645 * s:+.2f} to {e + 1.645 * s:+.2f} |")
        e, s = cumulative(m, ["dg:p3", "dg1:p3"])
        L += ["", f"Difference 2022-25 minus base: {e:+.2f} (s.e. {s:.2f}). With four annual observations and three own "
              "parameters, the 2022-25 standard error is not reliable; the restricted model below uses one.", ""]
        d["dgs"] = d.dg + d.dg1
        m2 = smf.ols("du ~ dg + dg1 + p2 + dg:p2 + dg1:p2 + dgs:p3", data=d).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
        e0, s0 = cumulative(m2, ["dg", "dg1"])
        e3, s3 = cumulative(m2, ["dg", "dg1", "dgs:p3", "dgs:p3"])  # the shift applies to both the current and the lagged term
        L += [f"Restricted model (2022-25 differs from the base by one common shift in the current and lagged slope, no own intercept): "
              f"cumulative response base {e0:+.2f} (s.e. {s0:.2f}); 2022-25 {e3:+.2f} (s.e. {s3:.2f}); "
              f"difference {2 * m2.params['dgs:p3']:+.2f} (s.e. {2 * m2.bse['dgs:p3']:.2f}).", ""]
    L += ["## Episode ratios with alternative dating (registered rate, AMECO gap)", "",
          "| Episode | Start → end | Gap fall | Δu | Ratio |", "|---|---|---|---|---|"]
    eps = oi.episodes(gap)
    alt = {(2007, 2009): (2008, 2009), (2017, 2020): (2019, 2020)}
    for a, b in eps:
        for lab, (x, y) in (("rule", (a, b)), ("alt", alt.get((a, b), (None, None)))):
            if x is None:
                continue
            fall, du = gap[x] - gap[y], dep[y] - dep[x]
            L.append(f"| {a}-{str(b)[2:]} ({lab}) | {x} → {y} | {fall:.1f} | {du:+.1f} | {du / fall:.2f} |")
    open("results/okun_inference.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
