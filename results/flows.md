# Labour-market flows: does Germany adjust at the hiring gate? (Stand 25.11.2026)

Data: BA, „Chancen und Risiken am Arbeitsmarkt nach Personengruppen“ (Dezember 2025, Monatszahlen 2007-2025, annual averages of monthly rates); ANBA Jahreszahlen 2017-2025; Destatis 21211-0004 (training contracts). Tidy file: `data/raw/ba_flows/flows_de.csv` (not committed), scripts `scripts/fetch_ba_flows.py`, `scripts/build_ba_flows_csv.py`.

| | 2008 | 2009 | 2019 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|
| Risk of becoming unemployed from a job, % per month | 0.86 | 0.97 | 0.61 | 0.51 | 0.54 | 0.57 | 0.59 |
| Chance of leaving unemployment for a job, % per month | 6.53 | 6.08 | 7.41 | 6.14 | 5.74 | 5.71 | 5.65 |
| Under 25: chance of leaving for a job | 14.2 | 12.2 | 13.7 | 11.9 | 10.8 | 10.2 | 9.9 |
| Germans: chance of leaving for a job | 6.9 | 6.4 | 7.7 | 6.6 | 6.5 | 6.2 | 6.0 |
| Foreigners: chance of leaving for a job | 4.7 | 4.2 | 6.6 | 5.2 | 4.5 | 4.9 | 5.1 |
| New training contracts (Destatis), thousands | | | 511 | 470 | 480 | 475 | 462 |

Steady-state check (u* = inflow risk / (inflow risk + exit chance), an index, not the official rate):
- 2019 to 2025: u* rises from 7.6 to 9.5. With only the exit chance changing it would rise to 9.8; with only the inflow risk changing it would fall to 7.4. Measured from 2019, the whole rise comes from fewer exits into work.
- 2022 to 2025: u* rises from 7.7 to 9.5. Only the inflow risk changing: 8.8 (+1.1); only the exit chance changing: 8.3 (+0.6). Measured from the unusually calm year 2022, rising dismissals contribute somewhat more than slower hiring.
- 2008 to 2009: only inflow 12.9 (+1.3), only outflow 12.3 (+0.7): the crisis ran through dismissals.

Reading:
- The risk of losing a job and becoming unemployed was 0.59 % a month in 2025, back at the 2019 level but far below 2008-09. Dismissals have risen from an unusually low 2022, not to crisis levels.
- The chance of finding a job out of unemployment fell by a quarter since 2019, to the lowest value in the series, below 2009. For under-25s it fell from 13.7 to 9.9 %.
- New training contracts were 10 % below 2019 in 2025.
- Flow evidence for the hiring-gate mechanism, with a qualification: against 2019 the rise comes entirely from slower exits into work; against 2022 dismissals matter as much. The essay should say both.
