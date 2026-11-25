"""Table 1 by the stated rule: every German episode in which the output gap falls by at least two
points from a local peak to the next trough (same algorithm and dates as Figure 1).
Gap: AMECO autumn 2026 (West Germany until 1990). Unemployment: registered rate on dependent civilian
labour force (BA). Writes results/table1_rule.md
Run from repository root: python3 scripts/table1_rule.py
"""
import sys

sys.path.insert(0, "scripts")
import okun_episodes_intl as oi  # noqa: E402
import okun_gap as og  # noqa: E402


def main():
    gap = oi.splice_de(oi.ameco("AVGDGP"))
    dep, _ = og.ba_rates()
    rows = ["| Episode | Lost capacity (points) | Registered unemployment, before → after (%) | Rise per point of lost capacity |",
            "|---|---|---|---|"]
    for a, b in oi.episodes(gap):
        dg, du = gap[b] - gap[a], dep[b] - dep[a]
        rows.append(f"| {a}-{str(b)[2:]} | {-dg:.1f} | {dep[a]:.1f} → {dep[b]:.1f} | {du / -dg:.2f} |")
    open("results/table1_rule.md", "w", encoding="utf-8").write("\n".join(rows) + "\n")
    print("\n".join(rows))


if __name__ == "__main__":
    main()
