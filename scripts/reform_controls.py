"""Labour-market core cuts and the rise in unemployment, with political controls from the reform literature.

Outcome: year with at least one enacted cut to a labour-market core institution (dismissal protection, unemployment
benefit, sick pay, short-time work; pensions and the 1986 strike rule excluded), from coding/reform_coding_v2.yaml
(see scripts/reform_years.py).
Main regressor: rise in the registered unemployment rate over the previous three years (Δu3).
Controls, following the empirical reform literature (Pitlik and Wirth 2003; Høj et al. 2006; Potrafke 2010):
government ideology (cabinet share of left parties), grand coalition, opposition majority in the Bundesrat (veto
player), new government, years to the next federal election, far-right vote share at the last federal election,
fall in the output gap over three years. Data: coding/politics_annual.csv.
Estimator: Firth's penalised-likelihood logit (Firth 1993), the standard correction for rare events and small
samples (11 events in 59 years); Wald standard errors from the penalised information matrix; likelihood-ratio
test of Δu3 against the model with controls only. Sample split: 1968-2004 (before the AfD and the Merkel-era
grand coalitions) and 1968-2026.

Run from repository root: python3 scripts/reform_controls.py
Writes results/reform_controls.md
"""
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, "scripts")
import reform_years as ry  # noqa: E402
import okun_episodes_intl as oi  # noqa: E402
import okun_gap as og  # noqa: E402


def firth(y, X, iters=200, tol=1e-9):
    """Firth (1993) penalised maximum likelihood for the logit. Returns beta, se, penalised log-likelihood."""
    n, k = X.shape
    b = np.zeros(k)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X @ b))
        W = p * (1 - p)
        info = X.T @ (X * W[:, None])
        inv = np.linalg.inv(info)
        h = np.einsum("ij,jk,ik->i", X * np.sqrt(W)[:, None], inv, X * np.sqrt(W)[:, None])
        score = X.T @ (y - p + h * (0.5 - p))
        step = inv @ score
        b = b + step
        if np.max(np.abs(step)) < tol:
            break
    p = 1 / (1 + np.exp(-X @ b))
    W = p * (1 - p)
    info = X.T @ (X * W[:, None])
    ll = np.sum(y * np.log(p) + (1 - y) * np.log(1 - p)) + 0.5 * np.linalg.slogdet(info)[1]
    return b, np.sqrt(np.diag(np.linalg.inv(info))), ll


def build():
    it = ry.items()
    core = it[(it.direction == "cut") & (it.target == "core")]
    core = core[~core.area.str.contains("d") & ~core.law.str.contains("116")]
    dep, _ = og.ba_rates()
    gap = oi.splice_de(oi.ameco("AVGDGP"))
    pol = pd.read_csv("coding/politics_annual.csv").set_index("year")
    years = list(range(1968, 2027))
    d = pd.DataFrame(index=years)
    d["cut"] = d.index.isin(core.year.unique()).astype(int)
    d["du3"] = [dep[t] - dep[t - 3] if t in dep else dep[2025] - dep[2023] for t in years]
    d["gapfall3"] = [gap.get(t - 3, np.nan) - gap.get(t, np.nan) for t in years]
    for c in ["cabinet_left_share", "grand_coalition", "bundesrat_opposition_majority", "new_government",
              "years_to_next_election", "far_right_vote_share"]:
        d[c] = pol[c].reindex(years).astype(float)
    if d.cabinet_left_share.max() > 1.5:
        d["cabinet_left_share"] = d.cabinet_left_share / 100
    d.loc[2026, "gapfall3"] = gap.get(2023) - gap.get(2025) if pd.isna(d.loc[2026, "gapfall3"]) else d.loc[2026, "gapfall3"]
    return d


def fit(d, cols, label):
    z = d.dropna(subset=["cut"] + cols)
    X = np.column_stack([np.ones(len(z))] + [z[c].values for c in cols])
    b, se, ll = firth(z.cut.values.astype(float), X)
    return z, b, se, ll


def main():
    d = build()
    CTRL = ["cabinet_left_share", "grand_coalition", "bundesrat_opposition_majority", "new_government",
            "years_to_next_election", "far_right_vote_share", "gapfall3"]
    specs = [("(1) Δu3 only", ["du3"]), ("(2) political controls only", CTRL[:-1]), ("(3) Δu3 + political controls", ["du3"] + CTRL[:-1]),
             ("(4) = (3) + gap fall", ["du3"] + CTRL)]
    names = {"du3": "Δ unemployment rate over 3 years (pp)", "cabinet_left_share": "Cabinet share of left parties",
             "grand_coalition": "Grand coalition", "bundesrat_opposition_majority": "Opposition majority in Bundesrat",
             "new_government": "New government this year", "years_to_next_election": "Years to next federal election",
             "far_right_vote_share": "Far-right vote share, last federal election (%)", "gapfall3": "Fall in output gap over 3 years (pp)"}
    L = ["# Labour-market core cuts with political controls (Firth logit)", "",
         "Outcome: year with an enacted cut to dismissal protection, unemployment benefit, sick pay or short-time work. "
         "Coefficients (penalised-likelihood s.e.). LR = penalised likelihood-ratio statistic for adding Δu3 to the model "
         "with the same controls (χ²(1); 3.84 = 5 %, 6.63 = 1 %).", ""]
    for period, (a, bnd) in (("1968-2026", (1968, 2026)), ("1968-2004", (1968, 2004))):
        sub = d[(d.index >= a) & (d.index <= bnd)]
        if period == "1968-2004":
            sub = sub.drop(columns=["far_right_vote_share"])
        L += [f"## {period} (years: {len(sub)}, cut years: {int(sub.cut.sum())})", ""]
        cols_used, res = [], {}
        for lab, cols in specs:
            cols = [c for c in cols if c in sub.columns and sub[c].notna().any() and sub[c].std() > 0]
            z, b, se, ll = fit(sub, cols, lab)
            res[lab] = (cols, b, se, ll, z)
        header = list(res)
        L += ["| Variable | " + " | ".join(header) + " |", "|---|" + "---|" * len(header)]
        allc = ["du3"] + CTRL
        for c in allc:
            cells = []
            for lab in header:
                cols, b, se, ll, z = res[lab]
                if c in cols:
                    i = cols.index(c) + 1
                    zval = b[i] / se[i]
                    star = "***" if abs(zval) > 2.576 else "**" if abs(zval) > 1.96 else "*" if abs(zval) > 1.645 else ""
                    cells.append(f"{b[i]:+.2f}{star} ({se[i]:.2f})")
                else:
                    cells.append("")
            if any(cells):
                L.append(f"| {names[c]} | " + " | ".join(cells) + " |")
        L.append("| N | " + " | ".join(str(len(res[h][4])) for h in header) + " |")
        # LR tests of du3
        for with_, without in (("(3) Δu3 + political controls", "(2) political controls only"),):
            cols_w, _, _, ll_w, z_w = res[with_]
            cols_wo = [c for c in cols_w if c != "du3"]
            ll_wo = fit(z_w, cols_wo, "")[3]
            L += ["", f"LR test for Δu3 given political controls: {2 * (ll_w - ll_wo):.2f}."]
        # descriptive: cut years by grand coalition
        g = sub.groupby("grand_coalition").agg(years=("cut", "size"), cut_years=("cut", "sum"), mean_du3=("du3", "mean"))
        L += ["", "Cut years by coalition type: " + "; ".join(
            f"{'grand coalition' if i == 1 else 'other'}: {int(r.cut_years)} of {int(r.years)} years (mean Δu3 {r.mean_du3:+.2f})" for i, r in g.iterrows()), ""]
    open("results/reform_controls.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
