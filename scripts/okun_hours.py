"""Okun relation with hours: how the loss of capacity in each episode split into fewer hours per worker,
fewer workers and more unemployment.

For every episode of the rule in Table 1 (output gap falls at least two points, AMECO autumn 2026):
- Δ log total hours worked (AMECO NLHT), split into Δ log employment (NETD) and Δ log hours per person (NLHA),
- each divided by the fall in the output gap; and the rise in the ILO unemployment rate (ZUTN).
Germany (West Germany until 1990) and, for the same rule applied to their own gaps, FRA, ITA, GBR, USA.
Changes are measured against the counterfactual of the pre-episode trend of each series (average growth
in the five years before the peak; for peaks from 2020 on, 2014-19), so that the secular fall in hours per worker does not count as adjustment.

Run from repository root:  python3 scripts/okun_hours.py
Writes results/okun_hours.md
"""
import math
import sys

sys.path.insert(0, "scripts")
import okun_episodes_intl as oi  # noqa: E402

V = {"gap": "AVGDGP", "hours": "NLHT", "emp": "NETD", "hpp": "NLHA", "u": "ZUTN"}


def series(d, name):
    if name == "Germany":
        return oi.splice_de(d)
    return d.get(name, {})


def dev(x, a, b, k=5):
    """Log change a->b minus the trend of the k years before a (100 x log points)."""
    e = a if a < 2020 else 2019  # pre-trend must not contain the pandemic years
    if any(y not in x or x[y] <= 0 for y in (e - k, e, a, b)):
        return float("nan")
    g = (math.log(x[e]) - math.log(x[e - k])) / k
    return 100 * (math.log(x[b]) - math.log(x[a]) - g * (b - a))


def main():
    raw = {k: oi.ameco(v) for k, v in V.items()}
    L = ["# Okun relation with hours (AMECO autumn 2026)", "",
         "Per episode: change in total hours, employment and hours per person employed (log points, against the trend of the five years before the peak; for peaks from 2020 on, 2014-19), "
         "and the rise in the ILO unemployment rate (pp); 'per pt' = divided by the fall in the output gap.", "",
         "| Country | Episode | Gap fall | Total hours | of which employment | of which hours per person | Δu (pp) | Hours per pt | Employment per pt | Hours/person per pt | Δu per pt |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for name in ["Germany", "France", "Italy", "United Kingdom", "United States"]:
        s = {k: series(raw[k], name) for k in V}
        for a, b in oi.episodes(s["gap"]):
            if a < 1971:
                continue
            fall = s["gap"][a] - s["gap"][b]
            h, e, p = dev(s["hours"], a, b), dev(s["emp"], a, b), dev(s["hpp"], a, b)
            du = s["u"].get(b, float("nan")) - s["u"].get(a, float("nan"))
            L.append(f"| {name} | {a}-{str(b)[2:]} | {fall:.1f} | {h:+.1f} | {e:+.1f} | {p:+.1f} | {du:+.1f} "
                     f"| {h / fall:+.2f} | {e / fall:+.2f} | {p / fall:+.2f} | {du / fall:+.2f} |")
    open("results/okun_hours.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
