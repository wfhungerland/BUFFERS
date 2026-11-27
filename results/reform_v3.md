# Reform analysis on the systematic coding v3

Items: 165; by target and direction:

| Target | cut | deregulation | expansion | mixed | re-regulation |
|---|---|---|---|---|---|
| core | 13 | 5 | 22 | 6 | 5 |
| margin | 16 | 7 | 26 | 12 | 14 |
| other | 0 | 0 | 1 | 3 | 10 |
| pension | 14 | 0 | 10 | 1 | 0 |

Second coder (n = 165): agreement on direction 76% (Cohen's kappa 0.67); on 'cut' vs other 97%; on target 99%; size within one step 100%.

## Core cuts (coder 1; cut or deregulation of a core institution)

| Year | Laws | Size | Stated motive | Δu3 (pp) |
|---|---|---|---|---|
| 1977 | 4. AFG-ÄndG 1977 | 2 | jobs/employment | +1.9 |
| 1981 | Arbeitsförderungs-Konsolidierungsgesetz (AFKG) 1981 | 3 | budget/consolidation | +1.2 |
| 1982 | Haushaltsbegleitgesetz 1983 | 3 | budget/consolidation | +3.7 |
| 1983 | Haushaltsbegleitgesetz 1984 | 3 | budget/consolidation | +5.3 |
| 1986 | § 116 AFG Neutralitätsgesetz 1986; SchwbG-Änderung 1986 | 2, 1 | other, jobs/employment | -0.1 |
| 1992 | Kündigungsmöglichkeiten-Verlängerung 1992 | 1 | budget/consolidation | +0.6 |
| 1993 | FKPG 1993 (AFG part); 1. SKWPG 1993 | 2, 3 | budget/consolidation, budget/consolidation | +2.6 |
| 1995 | 2. AFG-ÄndG Baugewerbe 1995 | 2 | other | +1.9 |
| 1996 | Arbeitsrechtliches Beschäftigungsförderungsgesetz 1996 (KSchG part); Arbeitsrechtliches Beschäftigungsförderungsgesetz 1996 (sick-pay part) | 3, 3 | jobs/employment, jobs/employment | +1.7 |
| 1997 | Arbeitsförderungs-Reformgesetz (AFRG | 3 | jobs/employment | +2.1 |
| 2002 | Hartz I (benefit part) | 2 | jobs/employment | -0.9 |
| 2003 | Arbeitsmarktreformgesetz 2003 (KSchG part); Arbeitsmarktreformgesetz 2003 (ALG duration part); Hartz III | 2, 3, 2 | jobs/employment, jobs/employment, other | +0.9 |
| 2019 | Brexit-Steuerbegleitgesetz (Brexit-StBG) 2019 (KSchG part) | 1 | other | -1.3 |

Stated motives of core cuts: jobs/employment 8; budget/consolidation 6; other 4.

## Core cuts: Firth logit, annual 1968-2026

| Model | Coefficients (s.e.) | N (cut years) |
|---|---|---|
| Δu3 | du3 +0.48 (0.19) | 59 (13) |
| Δu3 + level | du3 +0.48 (0.19); u_lag +0.11 (0.10) | 59 (13) |
| Δu3 × level | du3 +0.54 (0.58); u_lag +0.11 (0.12); du3_x_u -0.01 (0.07) | 59 (13) |
| Δu3 ILO | dilo3 +0.61 (0.23) | 59 (13) |
| Δu3 + fiscal | du3 +0.26 (0.23); ddebt3 -0.03 (0.06); duic3 +0.37 (0.47); maastricht +1.75 (0.99) | 53 (13) |
| Δu3 + fiscal + political | du3 +0.30 (0.26); ddebt3 -0.14 (0.11); duic3 +0.04 (0.52); maastricht +1.38 (1.16); cabinet_left_share -1.36 (1.65); grand_coalition -1.14 (1.50); bundesrat_opp_strict_majority +1.99 (1.28); new_government -1.23 (1.17); years_to_next_election +0.38 (0.38) | 53 (13) |

## Other outcomes, Δu3 only and with fiscal controls

| Outcome | Δu3 only | Δu3 with fiscal controls | Years with event |
|---|---|---|---|
| Core cut (coder 1) | +0.48 (0.19) | +0.26 (0.23) | 13 of 59 |
| Core cut or mixed | +0.51 (0.19) | +0.28 (0.22) | 17 of 59 |
| Core cut, size ≥ 2 | +0.60 (0.22) | +0.36 (0.24) | 11 of 59 |
| Core cut, size 3 | +0.78 (0.28) | +0.51 (0.30) | 7 of 59 |
| Core expansion | -0.18 (0.18) | -0.12 (0.25) | 15 of 59 |
| Margin cut | +0.10 (0.16) | -0.01 (0.21) | 15 of 59 |
| Margin deregulation | +0.09 (0.22) | +0.10 (0.32) | 6 of 59 |
| Pension cut | +0.01 (0.18) | -0.12 (0.24) | 12 of 59 |
| Core cut (coder 2 direction, coder 2 target) | +0.48 (0.19) | +0.26 (0.23) | 13 of 59 |

## Out of sample 2005-2026 (model fitted on 1968-2004)

- du3: expected core-cut years 4.7, observed 1, P(observed or fewer) 0.031.
- dilo3: expected core-cut years 4.2, observed 1, P(observed or fewer) 0.052.

## Specification curve (192 specifications)

Positive coefficient: 100%; significant at 10 %: 58%; at 5 %: 38%. Median coefficient +0.53.
By Δu window: 1 years 60% significant at 5 %; 2 years 44% significant at 5 %; 3 years 29% significant at 5 %; 4 years 19% significant at 5 %.
By controls: both 2%; fiscal 21%; none 85%; political 44%.
By period: all 51%; pre2005 25%.
By measure: dilo 42%; du 34%.

## External validation: OECD employment protection index (regular and temporary contracts)

- epl_regular_v1 (1985-2025): falls in []; rises in [1994].
- epl_temporary_v1 (1985-2025): falls in [1986, 1995, 1997, 1998, 2003, 2004]; rises in [2013, 2018].
- epl_regular_v4 (2013-2025): falls in []; rises in [].
- epl_temporary_v4 (2013-2025): falls in []; rises in [2018].
- Coded dismissal-protection cuts and fixed-term/agency deregulation (coder 1), years: 1985, 1986, 1989, 1992, 1996, 2002, 2003, 2007, 2019.
