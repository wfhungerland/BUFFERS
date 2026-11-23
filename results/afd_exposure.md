# AfD gain 2021–2025 against exposure and unemployment, 400 districts

N = 393 districts (West only: 319). OLS, robust standard errors (HC1).

Dependent variable: change in AfD second-vote share, Bundestag 2025 minus 2021, percentage points.

| Variable | (1) unemployment only | (2) exposure only | (3) both | (4) both + controls | (5) West only |
|---|---|---|---|---|---|
| Δ unemployment rate 2022–25 (pp) | -0.64** (0.32) |  | -0.49* (0.28) | -0.01 (0.20) | 0.22 (0.16) |
| Share energy-intensive manuf. (% of employees) |  | 0.25*** (0.04) | 0.24*** (0.03) | 0.07*** (0.03) | 0.06** (0.02) |
| Share metal/auto/machinery (% of employees) |  | 0.08*** (0.01) | 0.09*** (0.01) | 0.06*** (0.01) | 0.04*** (0.01) |
| East | 4.68*** (0.36) | 4.97*** (0.34) | 5.00*** (0.33) | 0.12 (0.58) |  |
| City district |  |  |  | -1.17*** (0.26) | -0.66*** (0.18) |
| Income per head (€1,000/month) |  |  |  | -2.36*** (0.22) | -2.03*** (0.17) |
| AfD share 2021 |  |  |  | 0.26*** (0.05) | 0.60*** (0.03) |
| R² | 0.37 | 0.50 | 0.50 | 0.74 | 0.81 |

## Size of effects (model 4, one standard deviation)

- Δ unemployment rate 2022–25 (pp): SD 0.39, effect -0.00 pp AfD
- Share energy-intensive manuf. (% of employees): SD 3.52, effect +0.26 pp AfD
- Share metal/auto/machinery (% of employees): SD 8.25, effect +0.47 pp AfD

## Descriptives

- Mean AfD gain: 11.5 pp (West 10.6, East 15.2).
- Mean Δ unemployment 2022–25: 0.92 pp; correlation with AfD gain: -0.06.
- Correlation AfD gain with energy-intensive share: 0.29; with metal share: 0.12.

Caveats: employment shares are measured in March 2026, after the shock (no pre-shock baseline in the data);
block shares inside manufacturing partly follow state-level industry mixes (see macro docs/zoll_kreise.md);
cross-section only, no causal identification.
