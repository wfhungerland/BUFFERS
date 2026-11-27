"""Responsiveness of parliamentary attention to unemployment: slopes with confidence intervals and an estimated break date.

ΔA_t = a + b Δu_t + e_t, A = unemployment hits per million words (CPP-BT), u = registered unemployment rate (BA).
Slopes with HAC s.e. for 1951-2002 and 2003-2025; break date estimated by the sup-F (Andrews 1993 / Quandt) test over
candidate years with at least 15 % of observations on each side; critical values from Andrews (1993), 2 parameters,
15 % trimming: 10 % 10.0, 5 % 11.7, 1 % 15.6.
Run: python3 scripts/plenum_breaks.py  -> results/plenum_breaks.md
"""
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
sys.path.insert(0, "scripts")
import okun_gap as og

dep, _ = og.ba_rates()
pm = pd.read_csv("results/plenum_topics.csv", index_col=0)
x = pm[(pm.index >= 1950) & (pm.index <= 2025)].copy()
x["u"] = [dep.get(i) for i in x.index]
d = x[["unemployment", "wages", "social_justice", "public_debt", "location", "competitiveness", "bureaucracy", "u"]].diff().dropna()
d = d.rename(columns={"unemployment": "U"})
L = ["# Attention to unemployment: slopes and break date", "",
     "Slope of the annual change in attention (hits per million words) on the annual change in the unemployment rate (pp). HAC s.e. (2 lags).", "",
     "| Topic | 1951-2002 slope (95 % CI) | 2003-2025 slope (95 % CI) | Difference (s.e.) |", "|---|---|---|---|"]
for k in ["U", "wages", "social_justice", "public_debt", "location", "competitiveness", "bureaucracy"]:
    z = d.copy(); z["post"] = (z.index >= 2003).astype(int)
    m = smf.ols(f"{k} ~ u + post + u:post", data=z).fit(cov_type="HAC", cov_kwds={"maxlags": 2})
    b0, s0 = m.params["u"], m.bse["u"]
    V = m.cov_params(); b1 = b0 + m.params["u:post"]; s1 = np.sqrt(V.loc["u", "u"] + V.loc["u:post", "u:post"] + 2 * V.loc["u", "u:post"])
    L.append(f"| {k} | {b0:+.1f} ({b0 - 1.96 * s0:+.1f} to {b0 + 1.96 * s0:+.1f}) | {b1:+.1f} ({b1 - 1.96 * s1:+.1f} to {b1 + 1.96 * s1:+.1f}) | {m.params['u:post']:+.1f} ({m.bse['u:post']:.1f}) |")
# sup-F for U
n = len(d); yrs = list(d.index); lo, hi = int(0.15 * n), int(0.85 * n)
r0 = smf.ols("U ~ u", data=d).fit(); ssr0 = r0.ssr
F = {}
for t in yrs[lo:hi]:
    z = d.copy(); z["post"] = (z.index >= t).astype(int)
    r = smf.ols("U ~ u + post + u:post", data=z).fit()
    F[t] = ((ssr0 - r.ssr) / 2) / (r.ssr / (n - 4))
t_star = max(F, key=F.get)
L += ["", f"Sup-F break test for the unemployment topic (break in intercept and slope): maximum F = {F[t_star]:.1f} at {t_star} "
      f"(Andrews 1993 critical values, 15 % trimming, 2 restrictions: 10 % 10.0, 5 % 11.7, 1 % 15.6). Next highest: "
      + ", ".join(f"{k} {v:.1f}" for k, v in sorted(F.items(), key=lambda kv: -kv[1])[1:4]) + ".",
      f"Standard deviation of Δu: 1951-2002 {d.u[d.index <= 2002].std():.2f}, 2003-2025 {d.u[d.index >= 2003].std():.2f} (lower variance attenuates correlations, not slopes)."]
open("results/plenum_breaks.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L))
