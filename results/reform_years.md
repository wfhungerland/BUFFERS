# Core cuts by year and the rise in unemployment, 1968-2026

Core cuts: enacted laws coded cut/core in coding/reform_coding_v2.yaml, inside and outside the episode windows. Δu3 = registered unemployment rate in t minus t-3 (pp). Permutation p-value: share of 10,000 random relabellings of cut years with a difference in mean Δu3 at least as large.

## Core-cut years

| Year | Laws | Δu3 (pp) | u (%) |
|---|---|---|---|
| 1975 | HStruktG-AFG (Zumutbarkeit part) | +3.6 | 4.7 |
| 1977 | 4. AFG-ÄndG | +1.9 | 4.5 |
| 1978 | 21. Rentenanpassungsgesetz (21. RAG) | -0.4 | 4.3 |
| 1981 | Arbeitsförderungs-Konsolidierungsgesetz (AFKG) | +1.2 | 5.5 |
| 1982 | Haushaltsbegleitgesetz 1983 | +3.7 | 7.5 |
| 1983 | Haushaltsbegleitgesetz 1984 | +5.3 | 9.1 |
| 1984 | AF/RVÄndG 1984 (Sperrzeit part) | +3.6 | 9.1 |
| 1986 | § 116 AFG Neutralitätsgesetz | -0.1 | 9.0 |
| 1989 | Rentenreformgesetz 1992 | -1.1 | 7.9 |
| 1993 | FKPG; 1. SKWPG | +2.6 | 9.8 |
| 1996 | Arbeitsrechtliches Beschäftigungsförderungsgesetz 1996 (KSch; Arbeitsrechtliches Beschäftigungsförderungsgesetz 1996 (sick; Wachstums- und Beschäftigungsförderungsgesetz (WFG) | +1.7 | 11.5 |
| 1997 | Arbeitsförderungs-Reformgesetz (AFRG, SGB III); Rentenreformgesetz 1999 | +2.1 | 12.7 |
| 2001 | Altersvermögensergänzungsgesetz (AVmEG) | -2.0 | 10.3 |
| 2002 | Hartz I (ALG indexation part) | -0.9 | 10.8 |
| 2003 | Arbeitsmarktreformgesetz 2003 (KSchG part); Arbeitsmarktreformgesetz 2003 (ALG duration part); Hartz III | +0.9 | 11.6 |
| 2004 | RV-Nachhaltigkeitsgesetz | +1.4 | 11.7 |
| 2007 | RV-Altersgrenzenanpassungsgesetz | -1.6 | 10.1 |

## Tests

| Variant | Cut years | Mean Δu3 cut years | Mean Δu3 other years | Permutation p | Logit coef. on Δu3 (s.e.) | Logit with gap fall, new government, SPD-led: Δu3 coef. (s.e.) |
|---|---|---|---|---|---|---|
| All core cuts | 17 of 59 | +1.29 | -0.13 | 0.003 | +0.47 (0.18) | +0.59 (0.26) |
| Without pensions | 12 of 59 | +2.13 | -0.19 | 0.000 | +0.89 (0.27) | +0.95 (0.34) |
| Without pensions and strike rule | 11 of 59 | +2.34 | -0.19 | 0.000 | +1.00 (0.30) | +1.04 (0.38) |

## Core-cut years with falling or stable unemployment (Δu3 ≤ 0.5)

- 1978: 21. Rentenanpassungsgesetz (21. RAG) (Δu3 -0.4; areas d)
- 1986: § 116 AFG Neutralitätsgesetz (Δu3 -0.1; areas e)
- 1989: Rentenreformgesetz 1992 (Δu3 -1.1; areas d)
- 2001: Altersvermögensergänzungsgesetz (AVmEG) (Δu3 -2.0; areas d)
- 2002: Hartz I (ALG indexation part) (Δu3 -0.9; areas b)
- 2007: RV-Altersgrenzenanpassungsgesetz (Δu3 -1.6; areas d)

## Episode-level variants

| Variant | Episodes with core cut | Rise in unemployment in those episodes | Episodes without |
|---|---|---|---|
| All core cuts; window trough+1; overlap to earlier | 1973-75, 1979-83, 1991-93, 2001-05, 2007-09 | +3.5, +5.3, +2.5, +2.7, -1.0 | 1965-67 (+1.4), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| All core cuts; window trough+1; overlap to later | 1973-75, 1979-83, 1991-93, 2001-05, 2007-09 | +3.5, +5.3, +2.5, +2.7, -1.0 | 1965-67 (+1.4), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| All core cuts; window trough+2; overlap to earlier | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| All core cuts; window trough+2; overlap to later | 1973-75, 1979-83, 1991-93, 2001-05, 2007-09 | +3.5, +5.3, +2.5, +2.7, -1.0 | 1965-67 (+1.4), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| All core cuts; window trough+3; overlap to earlier | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| All core cuts; window trough+3; overlap to later | 1973-75, 1979-83, 1991-93, 2001-05, 2007-09 | +3.5, +5.3, +2.5, +2.7, -1.0 | 1965-67 (+1.4), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| Without pensions; window trough+1; overlap to earlier | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| Without pensions; window trough+1; overlap to later | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| Without pensions; window trough+2; overlap to earlier | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| Without pensions; window trough+2; overlap to later | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| Without pensions; window trough+3; overlap to earlier | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| Without pensions; window trough+3; overlap to later | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| Without pensions and strike rule; window trough+1; overlap to earlier | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| Without pensions and strike rule; window trough+1; overlap to later | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| Without pensions and strike rule; window trough+2; overlap to earlier | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| Without pensions and strike rule; window trough+2; overlap to later | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| Without pensions and strike rule; window trough+3; overlap to earlier | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
| Without pensions and strike rule; window trough+3; overlap to later | 1973-75, 1979-83, 1991-93, 2001-05 | +3.5, +5.3, +2.5, +2.7 | 1965-67 (+1.4), 2007-09 (-1.0), 2011-13 (-0.2), 2017-20 (+0.2), 2022-25 (+1.0) |
