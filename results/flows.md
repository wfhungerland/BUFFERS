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

Steady-state check (u* = inflow risk / (inflow risk + exit chance)): 2022-25 the index rises from 7.7 to 9.5. With only the exit chance changing it would rise to 10.0; with only the inflow risk changing, to 8.8. In 2008-09, by contrast, the inflow risk drove the rise.

Reading:
- The risk of losing a job and becoming unemployed was 0.59 % a month in 2025, back at the 2019 level but far below 2008-09. Dismissals have risen from an unusually low 2022, not to crisis levels.
- The chance of finding a job out of unemployment fell by a quarter since 2019, to the lowest value in the series, below 2009. For under-25s it fell from 13.7 to 9.9 %.
- New training contracts were 10 % below 2019 in 2025.
- This is direct flow evidence for the hiring-gate mechanism: unemployment rose mainly because exits into work slowed, not because inflows from jobs surged.
