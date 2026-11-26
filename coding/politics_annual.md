# German federal political variables, 1965-2026: source note

File: `politics_annual.csv`. It has one row per year (62 rows, 1965-2026) and 33 columns. Compiled 2026-11-26.
Each group of variables has a `*_confirmed` column and a `*_source` column. `true` means the compiler saw the value, or the figures it is computed from, in the named source. `false` means the value was computed or carried forward by the compiler, or comes from coding that could not be checked against a reachable source. Nothing was taken from memory without being flagged `false`.

## Sources (all fetched 2026-11-26)
- **CPDS**: Armingeon et al., Comparative Political Data Set 1960-2020 (update 2022), `CPDS_1960-2020_Update_2022.dta`, copy in a Harvard Dataverse replication package: [datafile 6770136](https://dataverse.harvard.edu/api/access/datafile/6770136). cpds-data.org was unreachable. No copy covering 2021 or later was found on Dataverse; `CPDS2021.tab` (Blossey 2025) ends in 2019 for Germany.
- **DHB**: Deutscher Bundestag, Datenhandbuch zur Geschichte des Deutschen Bundestages, online edition from 1990:
  - [Kap. 1.2 Tag der Wahl](https://www.bundestag.de/resource/blob/196080/Kapitel_01_02_Tag_der_Wahl_zum_Bundestag.pdf)
  - [1.6 Wahlergebnisse auf Bundesebene](https://www.bundestag.de/resource/blob/196090/2e3fbc0745110fe23fd306fd96e1ea03/Kapitel_01_06_Wahlergebnis_auf_Bundesebene-data.pdf)
  - [1.7 Wahlergebnisse nach Parteien](https://www.bundestag.de/resource/blob/196092/Kapitel_01_07_Wahlergebnisse_nach_Parteien.pdf)
  - [1.15 Ungültige Stimmen](https://www.bundestag.de/resource/blob/196102/Kapitel_01_15_Ung__ltige_Stimmen.pdf) (valid second votes)
  - [6.1 Bundeskanzler](https://www.bundestag.de/resource/blob/196244/Kapitel_06_01_Wahl_und_Amtszeit_der_Bundeskanzler.pdf)
  - [6.2 Kabinette, Namensliste](https://www.bundestag.de/resource/blob/196242/Kapitel_06_02_Zusammensetzung_der_Bundeskabinette_-_Namensliste.pdf)
  - [6.6 Koalitionen](https://www.bundestag.de/resource/blob/196254/Kapitel_06_06_Koalitionen_und_Opposition_im_Bundestag.pdf)
  - [10.3 Bundestag und Bundesrat](https://www.bundestag.de/resource/blob/274406/Kapitel_10_03_Bundestag_und_Bundesrat.pdf) (dated 04.02.2026)
- **BWL 1949-2013**: Der Bundeswahlleiter, *Ergebnisse früherer Bundestagswahlen* (Stand 3.8.2015), Tab. 6 Zweitstimmen, [statistischebibliothek.de copy](https://www.statistischebibliothek.de/mir/servlets/MCRFileNodeServlet/DEHeft_derivate_00016450/btw_ab49_gesamt.pdf). bundeswahlleiterin.de itself was unreachable.
- **ParlGov 2024**: `view_cabinet`, [Harvard Dataverse doi:10.7910/DVN/2VZ5ZC](https://doi.org/10.7910/DVN/2VZ5ZC). Used for cabinet start dates before 1990.

## Variables
| Column | Definition | Years and source | Confirmed |
|---|---|---|---|
| chancellor, chancellor_party, coalition | The holder or coalition in office for the most days of the year. Minority interludes: Erhard, CDU/CSU alone (28.10.-30.11.1966); Schmidt, SPD alone (17.9.-30.9.1982); Scholz, SPD-Greens (7.11.2024-5.5.2025) | DHB 6.1, 6.2 and 6.6 (1990-); ParlGov and CPDS (before 1990) | true (the exact days of the 1966 and 1982 FDP exits are the compiler's; DHB 6.6 says only "Ende 1966" and "September 1982") |
| cabinets_in_year | Each government in office during the year, with its start date and days in office | as above | true |
| grand_coalition | 1 if CDU/CSU and SPD governed together for more than half the year: 1967-69, 2006-09, 2014-21, 2025-26 | as above | true |
| new_government | 1 if a new chancellor, or a new set of coalition parties, took office during the year: 1966, 1969, 1974, 1982, 1998, 2005, 2009, 2013, 2021, 2024 (FDP exit), 2025. A re-elected chancellor with the same coalition counts as 0 (e.g. 1972, 1983, 2018) | as above | true |
| cabinet_left_share | % of cabinet posts held by SPD/Greens/Linke, weighted by days in office | 1965-2020: **CPDS `gov_left1`**. 2021-2026: **computed** with the CPDS method from DHB 6.2 (see below) | 1965-2020 true; 2021-26 false (derived) |
| bundesrat_* | see the Bundesrat section | | |
| federal_election_year, election_date, years_to_next_election | years_to_next_election is 0 in an election year, otherwise the next election year minus this year. For 2026 the next election is assumed to be the regular one in 2029, which is not yet scheduled | BWL; DHB 1.2 | true; 2026 false |
| far_right_vote_share | % of valid second votes for NPD + DVU + REP + AfD in the most recent federal election. In an election year this is that year's election (lag the column if you need the pre-election value) | BWL (1965-2013), DHB 1.7 and 1.15 (2017-25); computed as votes / valid second votes | true |
| radical_left_vote_share | PDS / Die Linke + BSW, same construction. 0 before 1990, when these parties did not exist | as above | true |
| potrafke_ideology | Not obtained: no reachable copy of Potrafke's government-ideology index was found | | not obtained |

## Second-vote results by party (votes; % of valid second votes)
Shares are computed from the vote counts. The official one-decimal figures match in every case.
| Election | Valid | NPD | REP | DVU | AfD | PDS/Linke | BSW |
|---|---|---|---|---|---|---|---|
| 19.9.1965 | 32,620,442 | 664,193 (2.04) | - | - | - | - | - |
| 28.9.1969 | 32,966,024 | 1,422,010 (4.31) | - | - | - | - | - |
| 19.11.1972 | 37,459,750 | 207,465 (0.55) | - | - | - | - | - |
| 3.10.1976 | 37,822,500 | 122,661 (0.32) | - | - | - | - | - |
| 5.10.1980 | 37,938,981 | 68,096 (0.18) | - | - | - | - | - |
| 6.3.1983 | 38,940,687 | 91,095 (0.23) | - | - | - | - | - |
| 25.1.1987 | 37,867,319 | 227,054 (0.60) | - | - | - | - | - |
| 2.12.1990 | 46,455,772 | 145,776 (0.31) | 987,269 (2.13) | - | - | 1,129,578 (2.43) | - |
| 16.10.1994 | 47,105,174 | did not run | 875,239 (1.86) | - | - | 2,066,176 (4.39) | - |
| 27.9.1998 | 49,308,512 | 126,571 (0.26) | 906,383 (1.84) | 601,192 (1.22) | - | 2,515,454 (5.10) | - |
| 22.9.2002 | 47,996,480 | 215,232 (0.45) | 280,671 (0.58) | - | - | 1,916,702 (3.99) | - |
| 18.9.2005 | 47,287,988 | 748,568 (1.58) | 266,101 (0.56) | - | - | 4,118,194 (8.71) | - |
| 27.9.2009 | 43,371,190 | 635,525 (1.47) | 193,396 (0.45) | 45,752 (0.11) | - | 5,155,933 (11.89) | - |
| 22.9.2013 | 43,726,856 | 560,828 (1.28) | 91,193 (0.21) | - | 2,056,985 (4.70) | 3,755,699 (8.59) | - |
| 24.9.2017 | 46,515,492 | 176,020 (0.38) | - | - | 5,878,115 (12.64) | 4,297,270 (9.24) | - |
| 26.9.2021 | 46,442,023 | 64,574 (0.14) | - | - | 4,803,902 (10.34) | 2,270,906 (4.89) | - |
| 23.2.2025 | 49,649,512 | - | - | - | 10,328,780 (20.80) | 4,356,532 (8.77) | 2,472,947 (4.98) |

A dash means the party had no Landeslisten in that election. That is confirmed from 1990 on by DHB 1.7, which lists every party with lists. Before 1990 it rests on the BWL Tab. 6 listing. NPD (renamed Die Heimat in 2023) did not run in 2025. Not included: DRP (before 1965), DKP, DFU, ADF and the other small far-left parties of 1965-87; DIE RECHTE and pro Deutschland (2013: 0.0 and 0.2%). The 2021 figures are those in the current DHB, which reflect the partial Berlin repeat election of 11.2.2024.

## Cabinet left share, 2021-2026 (computed, false)
The CPDS denominator is the chancellor plus all federal ministers, including the minister for special tasks. This reproduces CPDS 2018-20: SPD 6 of 16 = 37.5. The compiler's composition from DHB 6.2:
- Merkel IV: 6/16 = 37.50
- Scholz from 8.12.2021: SPD 8, Greens 5, FDP 4 → 13/17 = 76.47
- From 7.11.2024: Kukies (SPD) and Özdemir (Greens, a second portfolio) took FDP posts, and Wissing, now without a party, held two posts. Counting by post that is 15/17 = 88.24; counting by person it is 14/15 = 93.3. The file uses posts.
- Merz from 6.5.2025: CDU 7 + Merz, CSU 3, SPD 7 → 7/18 = 38.89. The changes of 29.7.2026 were CDU for CDU.

Day-weighted yearly values: 2021 40.06; 2022-23 76.47; 2024 78.24; 2025 55.79; 2026 38.89.

## Bundesrat
- **bundesrat_opposition_majority** (main variable) uses the standard political-science dating. It is 1 when the federal governing parties lacked a majority of Bundesrat votes for most of the year, outside grand coalitions. "Lacked a majority" means that Länder governed only by federal governing parties (DHB "R-Länder") held no more than half of the votes. Coded 1: 1972-82, 1991-98, 1999-2005, 2011-13, 2022-24.
- **bundesrat_opp_strict_majority**: 1 when Länder governed only by federal opposition parties ("O-Länder") held a majority of votes for most of the year: 1996-98, 2002-05, 2013. Grand coalitions are never 1 on either variable, because O = 0 or close to it.
- **bundesrat_mixed_majority = 1** marks **mixed-majority years**: the government lacked a majority, but opposition-only Länder did not have one either, so mixed coalitions held the balance. These are 1991-95 (in 1995 O had exactly 34 of 68), 1999-2001, 2011-12 and 2022-24. In 2022-24 O was only Bavaria (6 votes): many authors would call these years "no majority" rather than opposition control.
- **bundesrat_{gov,opp,mixed}_votes_pct**: % of Bundesrat votes held by R-, O- and M-Länder. These are weighted by days, treating each DHB 10.3 "Stand" month as starting on the 1st. They are available from 1991.
- **Borderline year 2010**: R-Länder held 37 of 69 votes until the change of government in NRW ("Juli 2010"). Coded 0 because the majority held for more than half the year if the change came after 2 July. The compiler understands the date to be 14 July, but that date is not verified here.
- **DHB 10.3 gaps and errors**:
  - The table has no rows between April 2022 and May 2025. The 2023-25 vote shares therefore carry the April 2022 values forward (false). The 2022-24 coding does not depend on this, because R stayed far below 35.
  - The May 1991 row sums to 69, not 68. The file uses R and O as printed.
  - The May 2025 row lists HH twice and omits HE. The total of 12 R votes equals BE + HE + SL.
  - Saxony (CDU-SPD since December 2024) is not counted as R. That would make R 16. This does not affect the coding, because O = 0.
  - 2026 is carried forward from May 2025 (false).
- **1965-1990 (all false)**: DHB 10.3 refers to Datenhandbuch 1949-1999, ch. 11.8, which is not online. The FU Berlin table (webdoc.sub.gwdg.de), the MPIfG papers by Manow/Burkhart (pure.mpg.de, mpifg.de), bundesrat.de and bpb.de were all unreachable. Pre-1991 values follow the standard dating given in the brief: 1 in 1972-82, 0 otherwise.
  - A web-search summary of bpb texts says the CDU/CSU-led Länder already had a majority in 1969. That count includes Länder governed by CDU-led coalitions with the SPD or FDP, so 1970-71 were probably mixed-majority years.
  - In 1990, Lower Saxony changed government in mid-1990, and the five new Länder joined in October. Coded 0.

## Unreachable
bundeswahlleiterin.de, bundesrat.de, cpds-data.org, Wikipedia, bpb.de, wahlrecht.de, parlgov.org, pure.mpg.de, mpifg.de, webarchiv.bundestag.de, webdoc.sub.gwdg.de, digi.bib.uni-mannheim.de.
