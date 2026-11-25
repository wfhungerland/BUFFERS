# Labour-capital conflict series, (West) Germany 1950-2025: source note

File: `conflict_series.csv` (long format: year, variable, value, unit, source, source_url, confirmed, note). 1,086 rows. Compiled 2026-11-25.
`confirmed=true` means the compiler saw the value in the source file or page. `confirmed=false` marks values derived by the compiler, or values taken from a web-search summary because the source host was blocked.

## Series and coverage

| Variable | Years | Source | Confirmed |
|---|---|---|---|
| strike_days_lost_total (strikes and lockouts) | 1950-56 | ILO Year Book of Labour Statistics 1957, Tab. 34 (archive.org scan, p. 496) | true |
| | 1960-83 | CPDS 1960-2020 (`wdlost`, ILO-based) | true |
| | 1984-2025 | BA Streikstatistik, strike days + lockout days (sum) | false (derived) |
| strike_days_lost_strikes, lockout_days_lost, workers_involved_strikes, workers_locked_out, establishments_* | 1984-2025 | [BA Streikstatistik 2025, Tab. 1](https://statistik.arbeitsagentur.de/Statistikdaten/Detail/202512/iiia6/streik/streik-dl-0-202512-xlsx.xlsx?__blob=publicationFile&v=1) | true |
| strike_days_lost_strikes_only / workers_involved_strikes_only | 1966-71, 1982-83 | Statistisches Jahrbuch, national tables | true |
| workers_involved_total | 1950-56; 1964-68; 1971-83; 1984-2025 | ILO 1957; Statistisches Jahrbuch international tables (in 1,000s); BA (sum, derived) | true / derived |
| strike_days_per_1000_employees | 1995-2025 | [Destatis quality-of-employment indicator](https://www.destatis.de/DE/Themen/Arbeit/Arbeitsmarkt/Indikatoren-Qualitaet-Arbeit/Dimension-5/_Interaktiv/Daten/5-3-streiks.csv?__blob=value&v=9) (BA days / employees) | true |
| | 1991-94 | BA days / Eurostat employees (SAL_DC) | false (derived) |
| strike_days_per_1000_cpds | 1960-2020 | CPDS `strike` index ("per 1000 workers"; implied denominator is about the labour force, not employees) | true |
| strike_days_lost_total_cpds_ilo | 1984-2020 | CPDS/ILO, kept for comparison with BA | true |
| wsi_strike_days_lost / wsi_workers_involved / wsi_disputes | 2019-2025 (2023 participants and disputes only) | WSI Arbeitskampfbilanz report abstracts on [RePEc](https://ideas.repec.org/s/zbw/wsirep.html) | true |
| | 2007-2018, 2023 days | web-search summaries of the WSI Tarif-Taschenbuch and press releases | **false** (wsi.de and boeckler.de blocked) |
| wsi_strike_days_per_1000_employees | 2007-2025 | WSI days / Eurostat employees | false (derived) |
| union_density | 1960-2024 | [OECD/AIAS ICTWSS, OECD Data Explorer DF_TUD](https://sdmx.oecd.org/public/rest/data/OECD.ELS.SAE,DSD_TUD_CBC@DF_TUD,1.0/DEU..) | true |
| bargaining_coverage_oecd | 1960-90 every 5 years, then 1995-2024 annual | [OECD/AIAS DF_CBC](https://sdmx.oecd.org/public/rest/data/OECD.ELS.SAE,DSD_TUD_CBC@DF_CBC,1.0/DEU..) | true |
| iab_cov_{sector,firm,none}_{west,east,germany} | 1996-2025 | [IAB-Betriebspanel data tables 4/6/8](https://iab.de/daten/daten-zur-tarifbindung-und-betrieblichen-interessenvertetung/) (share of employees) | true |
| iab_cov_total_* | 1996-2025 | 100 minus the share with no collective agreement | false (derived) |
| major_dispute | 11 events | compiler summary; the numbers in it point to series in this file | false |

## Gaps
- **Days lost: no value for 1957-59.**
- **Workers involved: no value for 1957-63, and none for 1969-70 on a strikes-plus-lockouts basis.** The strikes-only national values cover those two years.
- WSI estimates for 2006, and 2007 participants: not found.
- IAB East coverage starts in 1996 here: the IAB tables include East Germany from 1996.
- ILOSTAT, wsi.de, boeckler.de, gewerkschaftsgeschichte.de, Wikipedia, cpds-data.org and GDZ were unreachable through the proxy.

## Breaks
- 1950: ILO figures cover the Bizone only. 1950-56 also exclude the Saar.
- 1991 (union density) and 1993 (BA strike data): West Germany becomes unified Germany. BA data for 1984-92 cover the former West only.
- From 1983 the strike data come from the BA instead of the Federal Statistical Office. The BA notes that its data undercount strikes, especially short warning strikes. For 2022 it reports at least 50,000-60,000 days missing (strikes in the NRW health sector were not reported).
- 1984: CPDS/ILO gives 5.62m days, while the BA's strikes plus lockouts come to 6.49m.
- 1971: the national table (strikes only, 2.60m days) differs from the international table (strikes and lockouts, 4.48m days).
- OECD bargaining coverage: 1960-90 is a constant 85%, and 1995 carries an OECD break flag.
- IAB: the shares are reported by establishments and rounded to whole percentages.
- WSI vs BA: WSI estimates run about 2-3 times higher (2023 about 1.5m vs 0.59m days; 2024 0.95m vs 0.48m).
