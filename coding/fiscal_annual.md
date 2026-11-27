# German fiscal and institutional series, 1965-2026: source note

File: `fiscal_annual.csv`, in long format with columns `year, variable, value, unit, source, source_url, confirmed, note`. It has 863 rows and was compiled on 2026-11-27. The build script is `build_fiscal.py`, kept in the session scratchpad.

**`confirmed`** takes three values:
- `true`: the compiler saw the value in the named source.
- `partly`: the source implies the value (for example "raised from X to Y", which fixes the earlier year), or the value is preliminary or cited at second hand.
- `false`: the value is the compiler's statutory knowledge or the compiler's own calculation, and no fetched source shows it. Use these with care.

When `value` is empty, the value was not obtained.

## Variables
| variable | coverage | source | confirmed |
|---|---|---|---|
| `gg_net_lending_pct_gdp` | 1991-2025 | AMECO `1.0.319.0.UBLG` (Germany, ESA 2010, % of GDP). AMECO has **no West German (D_W) series** for net lending, so nothing is available before 1991 | true |
| `gg_gross_debt_pct_gdp` | 1995-2025 | AMECO `1.0.319.0.UDGG` (ESA 2010) | true |
| `gg_gross_debt_pct_gdp_linked` | 1970-1990 West Germany, 1991-2025 Germany | AMECO `1.0.319.0.UDGGL` (linked with former definitions) | true |
| `unemployment_rate_ilo` | 1965-1990 West Germany, 1991-2025 Germany | AMECO `1.0.0.0.ZUTN` (Eurostat definition) | true |
| `bund_net_borrowing` | 1969, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010; 2015-2024 | BMF Monatsbericht, Tab. 6.1 Gesamtübersicht (Ist, bn EUR); the Finanzierungssaldo is given in the note | true for those years. The other years are empty (not obtained) |
| `ui_contribution_rate` | 1965-2026 | see the rates section below | mixed |
| `pension_contribution_rate` | 1965-2026 | see the rates section below | mixed |
| `ba_reserve_total`, `ba_reserve_general` | 2005-2025 (2023 missing) | see the reserve section below | mixed |
| `hartz4_registration_effect*` | 2005 | IAB and BA, see the Hartz IV section below | see that section |
| `epl_regular_v1..v4`, `epl_regular_individual_*`, `epl_collective_*`, `epl_temporary_v1/v3/v4` | v1 1985-2025, v2 1998-2025, v3 2008-2025, v4 2013-2025 | OECD SDMX `OECD.ELS.JAI,DSD_EPL@DF_EPL,1.0` | true |
| `nrr_single_aw67_{m2,m13,m60}_{no_sa_hb,with_sa_hb}` | 2001-2025 | OECD SDMX `DSD_TAXBEN_NRR@DF_NRR`: single person, 67 % of the average wage, months 2, 13 and 60 of unemployment, with or without social assistance and housing benefit | true |
| `grr_summary_oecd` | 1965-2005, odd years only | OECD SDMX `DSD_TAXBEN_HGRR@DF_HGRR`: the historical **gross** replacement rate summary measure | true |
| `cwed_replacement_rate` | none | CWED2 (Scruggs): cwed2.org was not reachable | not obtained |

## AMECO
- The URL pattern is `https://ec.europa.eu/economy_finance/ameco/wq/series?fullVariable=<unit.code>&countries=DEU,D_W&years=1960,...,2027&lastYear=0&defaultCountries=0`, fetched with a User-Agent header.
- The vintage is the online database as of 2026-11-27. The latest years may still be revised.
- `1.0.310.0.*` returned no data. No variant of UBLG exists for D_W, so West German net lending would need another source, for example the Bundesbank or the Statistisches Bundesamt (VGR 1950-1990).

## OECD
- EPL: `https://sdmx.oecd.org/public/rest/data/OECD.ELS.JAI,DSD_EPL@DF_EPL,1.0/all?format=csvfilewithlabels`.
  - Version 1 has regular contracts (EPL_OV = EPL_R), temporary contracts (EPL_T) for 1985-2025. Version 2 has regular contracts and collective dismissals for 1998-2025. Version 3 (2008-) and version 4 (2013-) are the current methodology.
  - The version labels say "1985-2019", "2013-2019" and so on, but the database carries values to 2025. The note column records this.
  - Germany, version 1:
    - EPL_OV is 2.5 for 1985-1993 and 2.595 from 1994.
    - EPL_T is 4.625 in 1985, 2.875 for 1986-94, 2.75 for 1995-96, 2.125 in 1997, 1.625 for 1998-2002, 1.125 in 2003, 0.625 for 2004-12, 0.75 for 2013-17 and 1.0 from 2018.
- NRR: `.../DSD_TAXBEN_NRR@DF_NRR,1.0/DEU..........`. Other household types and earnings levels are in the dataflow.
- HGRR: `.../DSD_TAXBEN_HGRR@DF_HGRR,1.0/DEU...`. This is the OECD "benefit generosity" summary measure, which is gross and is published for odd years only.

## Contribution rates (UI = Arbeitslosenversicherung, pension = allgemeine Rentenversicherung)
- The value is the rate in force for most of the year. Changes during a year are described in the note column: UI in 1985 and 1991, and pension in 1983, 1985, 1991 and 1999.
- The direct government sources were not reachable from this session: DRV, BAS, bpb, BMAS, arbeitsagentur.de, sozialpolitik-aktuell and Wikipedia were all blocked by the proxy. Rates were therefore confirmed from these sources:
  - Sachverständigenrat Jahresgutachten (BT-Drucksachen). JG 1985/86, Tabelle 23 gives both rates for 1981-1985.
  - The chronologies in JG 1976/77, 1982/83, 1987/88, 1990/91, 1992/93, 1996/97, 1998/99, 2000/01, 2001/02, 2007/08, 2008/09, 2012/13 and 2013/14.
  - Ausschussdrucksache 19(11)425, Tabelle 1, which gives the UI rate for 1999-2017.
  - Kiel Policy Brief 119 and BT-Drs. 19/9668 for the 2019 change.
- **Not confirmed** (`false`, statutory values from the compiler's knowledge):
  - UI 1965-1975 (1.3 / 1.7 / 2.0), 1977-1980, 1994-1998 and 2020-2022 (2.4).
  - Pension 1969-1980, 1988-1991, 1994, 1995, 1997, 1998, 2002, 2005-2006, 2008-2011, 2014-2016, 2018-2019, 2021-2022 and 2024-2026.
- **Planned versus enacted rates:**
  - SVR JG 1996/97 expected 20.2 % for 1997. The compiler has 20.3 %.
  - SVR JG 1998/99 reported the 1999 cut to 19.5 % as "ab 1. Januar 1999". The compiler dates the enacted cut to 1 April 1999.
  - SVR JG 2013/14 projected 18.4 % for 2014, but the cut was suspended.
- A DRV or BAS table of rates since 1957 would settle all of these.

## Reserve of the Federal Employment Agency (year end, bn EUR)
- **2005-2017:** Ausschussdrucksache 19(11)425 (Materialzusammenstellung Beitragsentlastung, BT-Ausschuss für Arbeit und Soziales), Tabelle 1 "BA-Haushalt 1999-2017".
  - The table gives the total reserve and the contribution-financed (general) reserve.
  - Values: 2006 11.2; 2007 17.9; 2008 16.7; 2009 2.9; 2010 0; 2011 0.04; 2012 2.6; 2013 2.7 (general 2.4); 2014 4.3; 2015 8.0; 2016 13.4; 2017 19.4 (preliminary).
  - The table is an expert compilation from BA figures. It matches SVR JG 2009/10 (end-2008: 16.7), SVR JG 2010/11 ("knapp 3" at end-2009) and Kiel Policy Brief 124 (2013-2017, from BA information).
- **2018:** Kiel Policy Brief 124 gives a general reserve of 23.5 and a total of 25.6.
- **2019:** hib 1065/2020 on BT-Drs. 19/22932 gives 25.8.
- **2020:** 5.4. This is derived by the compiler from the BMF withdrawal of 20.4 and is marked `false`.
- **2021:** 0 (BMF).
- **2022:** 0, implied by the federal loan. Marked `false`.
- **2023:** not obtained.
- **2024:** 3.2 (BT-Drs. 21/7611).
- **2025:** 0 (BT-Drs. 21/7611). A federal loan of 1.4 bn was drawn in 2025.

## Hartz IV registration break, 2005
- **BA (2006b), cited in IAB-Forschungsbericht 9/2007, p. 16:**
  - The quantifiable annual-average Hartz IV effect was about **+380,000** registered unemployed. In the original wording: "beziffert die BA den quantifizierbaren jahresdurchschnittlichen Hartz-IV-Effekt mit einem Plus von etwa 380.000 Arbeitslosen".
  - IAB-FB 1/2011 (p. 12) repeats this: "Von den zusätzlichen 480.000 Arbeitslosen können 380.000 mit der Veränderung der Arbeitslosenstatistik ... erklärt werden". The effect came mostly from the Stille Reserve moving into registration.
- **West Germany only:** about +340,000, which raised the West German rate by about 1 point. Source: BA (2006), cited in IAB-FB 11/2010, p. 23.
- **Ex-ante IAB estimate (IAB-Kurzbericht 10/2005):**
  - The merger of Arbeitslosenhilfe and Sozialhilfe adds **0.4-0.5 million** registered unemployed.
  - About 0.2 million de-registrations offset this, so the net effect is **+0.2-0.3 million**.
- The BA original (Arbeitsmarkt 2005) was not reachable. Only the citations of it were seen, so those rows are marked `partly`.

## Not obtained, and next steps
- **West German general government net lending before 1991.** It is not in AMECO.
- **Federal net borrowing (Nettokreditaufnahme) in non-benchmark years before 2015, and 2025.** Sources to try: BMF Finanzbericht tables, Bundesbank time series, Statistisches Jahrbuch.
- **CWED2 replacement rates.** cwed2.org is blocked.
- **BA reserve at end-2023.**
- **The contribution rates marked `false`.**
