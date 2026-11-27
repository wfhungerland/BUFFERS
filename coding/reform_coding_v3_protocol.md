# Reform coding v3: protocol note

File: `reform_coding_v3.yaml` (166 items, 1965-2026). Compiled 27 Nov 2026. This note records how the sweep was done, what it can and cannot claim, and how it compares with `reform_coding_v2.yaml`.

## 1. Fixed protocol

The sweep had to be blind to the business cycle.

- **No cycle data.** No unemployment, output, output-gap or recession data were looked up or used. No year or episode was given priority. An earlier session had left macro files (AMECO downloads) in a scratch folder. They were neither opened nor used. The v2 file's `fixed_rules` and episode summaries mention output gaps. They were not read for this sweep.
- **The same steps for every year 1965-2026:**
  1. Build a complete list of all federal laws passed by the Bundestag in that year (the frame, section 2).
  2. Apply one fixed keyword-and-committee filter to every title.
  3. Screen the remaining titles by hand against scope a-j.
  4. For each candidate, read the Bundestag passage record and the bill Drucksache: the cover sheet "A. Problem/Zielsetzung, B. Lösung", or the opening of the Begründung for pre-1972 bills.
  5. Run at most one or two targeted keyword searches in the bill for the main number.
  6. Code the item.
- **Passage dates.** The date is that of the final Bundestag reading. If a Vermittlungsausschuss or an Einspruch followed, the first Gesetzesbeschluss date is used and the later step is noted.
- **What is not coded.** There is no episode assignment and no core/margin coding.
- **Stated motive.** The motive is taken from the bill's problem statement or Begründung. Where the bill is silent, it comes from the government statement at passage. The first-stated aim decides the category:
  - Lowering non-wage costs "for jobs" counts as jobs/employment only if jobs are the first-stated aim.
  - Stabilising contribution rates or pension finances counts as demography/contribution rate.
  - Constitutional Court and EU obligations count as EU/legal requirement.

  Some bills describe the economic situation in their problem statement, for example Hartz I/II, the 1975 Haushaltsstrukturgesetz and the 2026 Neue Grundsicherung. Those sentences are bill text. They were not used as cycle data and were not quoted as the motive.

## 2. Sources and access

**Reachable:**

- dserver.bundestag.de: the Bundestag Parlamentsarchiv law documentation (GESTA), Drucksachen, and plenary protocols (PDF for WP 4-7, XML for WP 19-21).
- doku.iab.de: IAB chronicle documents. The main one is "Die wesentlichen Änderungen im Bereich des AFG seit 1969" (after J. Steffen 1993), which covers 1969-1993.
- Web search.

**Not reachable or not usable:**

- The DIP API ("Vorgänge" by Sachgebiet) needs an API key. The public example key in the DIP information sheet was rejected, and extracting a key from the web front-end was declined.
- sozialpolitik-aktuell.de, bmas.de and bgbl.de: blocked (DNS) in this session.
- recht.bund.de: its search returns 403.
- The IAB "Chronik der Arbeitsmarktpolitik" exists only as scattered documents (doku.iab.de/chronik/31, 32, 2x, 4x). Their coverage is uneven, roughly 1978-2013, so the chronicle could not serve as the year-by-year frame. It was used only as a secondary content source.

**Sampling frame by period:**

| Period | Frame | Size |
|---|---|---|
| Jan 1965-Dec 1976 (WP 4 part, 5, 6, 7) | Every plenary protocol was downloaded. Text extraction took every "Zweite (und dritte) / Dritte Beratung des Entwurfs eines ..." item with its Drucksache. | 1,249 reading records |
| Dec 1976-2021 (WP 8-19) | GESTA "Gesetzesmaterialien" index of every promulgated law, numbers 1..n per Wahlperiode, with title, BGBl citation, lead committees and the dated readings. Scanned files (about 570, WP 8-12) were OCRed on pages 1-2. | 5,200 laws |
| 2018-2026 (WP 19, 20, 21 up to session 21/111) | XML plenary protocols, same extraction. Added because GESTA has no files yet for about 190 WP 19 laws, mostly from 2020-21. | 1,382 reading records |

**Filter.** One keyword list was applied identically to every title of every year. It covers dismissal, unemployment, the SGB books, pensions, sick pay, short-time work, fixed-term, agency and marginal work, social assistance, minimum wage, codetermination, budget-accompanying laws, consolidation and "Beschäftigung". Bills whose lead committee was Arbeit/Sozialordnung/Arbeit und Soziales were also kept. Treaties, health and long-term care, accident insurance, BAföG, civil-service pay and similar subjects were then removed unless the title also hit a core term. In total 1,023 title hits were screened by hand; the per-year counts are in section 5.

## 3. Coding rules

- **direction:** coded from the protected worker's or claimant's point of view. Lower or shorter benefits, or stricter eligibility, are a "cut". Less protection is "deregulation". New or stricter protective rules are "re-regulation". "mixed" means a substantial change in both directions.
- **size:** 3 if a large group's level, duration or protection changes substantially, for example ALG duration 1987 and 2003, the 1996 KSchG and sick-pay changes, Rente mit 63/67, the minimum wage, Hartz IV and Bürgergeld. 2 for moderate changes. 1 for technical or group-specific changes.
- **Areas and splits:** a law that changes several areas substantially is split into one item per area, as v2 did for the 1996 and 2003 laws.
- **Group-specific dismissal protection** is area a: mothers, severely disabled people, apprentices on works councils, East German public service, works-council initiators, and bank risk-takers (Brexit-Steuerbegleitgesetz 2019).
- **Exclusion rules** (listed in `excluded_by_scope`):
  - routine pension adjustments that only apply the formula;
  - disability and survivor pensions;
  - laws that only change financing or contribution rates;
  - administrative and federal-municipal finance laws;
  - SGB XII-only (non-employable) rules;
  - unification transfer laws;
  - tax-only laws;
  - part-time-only, working-time, tenancy and procurement rules.
- **confirmed** is true only if the passage date and the main content of `what` were seen in the cited source. Bill content counts as seen even where committee amendments were not compared; where the final text is known to differ (Vermittlungsausschuss), confirmed=false.
- **source_type:** primary means the main number comes from a Drucksache, protocol or GESTA. Secondary means it comes from the IAB chronicle; the date is always from a primary record.

## 4. Check against v2

v2 was opened only after the sweep, to count overlap. It was not used to choose years or items.

- **v2 episode items: 65 in total.**
  - **59** were found independently. Several v2 split items map to one v3 item (HStruktG 1975, AF/RVÄndG 1984) or several (the 1996 and 2003 laws).
  - **2** were missed by the sweep and added during the check:
    - EGEStRG 1974 (v2 E2-01): its title was split across columns in the 1974 protocol and the extractor missed it.
    - 9. SGB II-ÄndG 2016 (v2 E7-03): an exclusion term ("Insolvenz") in the title removed it.
    - Both are flagged `found_via_v2_check: true`.
  - **4** are ordinances (Kug duration 2008, 2009, 2025, 2026) and are outside the frame (section 6).
- **v2 outside_windows: 10/10** found independently.
- **v2 excluded_by_scope:** the Tarifautonomiestärkungsgesetz 2014 (minimum wage) is coded here, because minimum wage is now in scope.
- **New items not in v2: 95.**
  - Mostly areas newly in scope: i (9), j (14) and group-specific a.
  - Also laws in years v2 did not cover, for example 1965-1968, 1971-1973, 1980, 1986-1990 and 1995.
  - Also laws v2 had not listed, for example the 2009 pension guarantee, the 2. SGB VI-ÄndG 2003 zero adjustment, the 2010 and 2022 Kug extensions, the 2019 Brexit KSchG rule and the 2022 sanctions moratorium.

## 5. Effort and yield per year

"Title hits screened" counts the frame titles that passed the fixed filter and were read by hand. 2019-2021 are double-counted because GESTA and the protocols overlap. A year with zero items means no in-scope law was found in that year's frame, not that the year was skipped.

| Year | Frame | Title hits screened | Items coded | of which match v2 (found independently) | added only via v2 check | new (not in v2) |
|---|---|---|---|---|---|---|
| 1965 | PlPr WP4-7 (PDF) | 28 | 1 | 0 | 0 | 1 |
| 1966 | PlPr WP4-7 (PDF) | 10 | 0 | 0 | 0 | 0 |
| 1967 | PlPr WP4-7 (PDF) | 14 | 1 | 0 | 0 | 1 |
| 1968 | PlPr WP4-7 (PDF) | 9 | 0 | 0 | 0 | 0 |
| 1969 | PlPr WP4-7 (PDF) | 25 | 5 | 2 | 0 | 3 |
| 1970 | PlPr WP4-7 (PDF) | 19 | 0 | 0 | 0 | 0 |
| 1971 | PlPr WP4-7 (PDF) | 16 | 2 | 0 | 0 | 2 |
| 1972 | PlPr WP4-7 (PDF) | 13 | 4 | 0 | 0 | 4 |
| 1973 | PlPr WP4-7 (PDF) | 19 | 1 | 0 | 0 | 1 |
| 1974 | PlPr WP4-7 (PDF) | 26 | 4 | 0 | 1 | 3 |
| 1975 | PlPr WP4-7 (PDF) | 15 | 1 | 1 | 0 | 0 |
| 1976 | PlPr WP4-7 (PDF) | 17 | 1 | 0 | 0 | 1 |
| 1977 | GESTA WP8-19 | 5 | 2 | 1 | 0 | 1 |
| 1978 | GESTA WP8-19 | 6 | 3 | 1 | 0 | 2 |
| 1979 | GESTA WP8-19 | 11 | 2 | 1 | 0 | 1 |
| 1980 | GESTA WP8-19 | 10 | 1 | 0 | 0 | 1 |
| 1981 | GESTA WP8-19 | 7 | 3 | 1 | 0 | 2 |
| 1982 | GESTA WP8-19 | 4 | 1 | 1 | 0 | 0 |
| 1983 | GESTA WP8-19 | 4 | 1 | 1 | 0 | 0 |
| 1984 | GESTA WP8-19 | 12 | 2 | 1 | 0 | 1 |
| 1985 | GESTA WP8-19 | 15 | 2 | 2 | 0 | 0 |
| 1986 | GESTA WP8-19 | 13 | 3 | 1 | 0 | 2 |
| 1987 | GESTA WP8-19 | 9 | 2 | 2 | 0 | 0 |
| 1988 | GESTA WP8-19 | 12 | 3 | 1 | 0 | 2 |
| 1989 | GESTA WP8-19 | 16 | 2 | 2 | 0 | 0 |
| 1990 | GESTA WP8-19 | 21 | 1 | 0 | 0 | 1 |
| 1991 | GESTA WP8-19 | 14 | 1 | 0 | 0 | 1 |
| 1992 | GESTA WP8-19 | 12 | 2 | 1 | 0 | 1 |
| 1993 | GESTA WP8-19 | 16 | 4 | 3 | 0 | 1 |
| 1994 | GESTA WP8-19 | 17 | 2 | 0 | 0 | 2 |
| 1995 | GESTA WP8-19 | 5 | 3 | 0 | 0 | 3 |
| 1996 | GESTA WP8-19 | 21 | 9 | 4 | 0 | 5 |
| 1997 | GESTA WP8-19 | 11 | 4 | 2 | 0 | 2 |
| 1998 | GESTA WP8-19 | 11 | 3 | 3 | 0 | 0 |
| 1999 | GESTA WP8-19 | 15 | 6 | 0 | 0 | 6 |
| 2000 | GESTA WP8-19 | 12 | 2 | 1 | 0 | 1 |
| 2001 | GESTA WP8-19 | 15 | 4 | 3 | 0 | 1 |
| 2002 | GESTA WP8-19 | 14 | 3 | 2 | 0 | 1 |
| 2003 | GESTA WP8-19 | 13 | 6 | 4 | 0 | 2 |
| 2004 | GESTA WP8-19 | 13 | 3 | 1 | 0 | 2 |
| 2005 | GESTA WP8-19 | 9 | 1 | 0 | 0 | 1 |
| 2006 | GESTA WP8-19 | 16 | 5 | 2 | 0 | 3 |
| 2007 | GESTA WP8-19 | 14 | 7 | 1 | 0 | 6 |
| 2008 | GESTA WP8-19 | 16 | 5 | 2 | 0 | 3 |
| 2009 | GESTA WP8-19 | 9 | 4 | 1 | 0 | 3 |
| 2010 | GESTA WP8-19 | 10 | 3 | 2 | 0 | 1 |
| 2011 | GESTA WP8-19 | 15 | 2 | 1 | 0 | 1 |
| 2012 | GESTA WP8-19 | 12 | 1 | 1 | 0 | 0 |
| 2013 | GESTA WP8-19 | 16 | 0 | 0 | 0 | 0 |
| 2014 | GESTA WP8-19 | 15 | 3 | 1 | 0 | 2 |
| 2015 | GESTA WP8-19 | 15 | 0 | 0 | 0 | 0 |
| 2016 | GESTA WP8-19 | 11 | 6 | 3 | 1 | 2 |
| 2017 | GESTA WP8-19 | 17 | 0 | 0 | 0 | 0 |
| 2018 | GESTA WP8-19 | 23 | 3 | 3 | 0 | 0 |
| 2019 | GESTA WP19 + PlPr XML | 49 | 1 | 0 | 0 | 1 |
| 2020 | GESTA WP19 + PlPr XML | 80 | 8 | 5 | 0 | 3 |
| 2021 | GESTA WP19 + PlPr XML | 64 | 2 | 0 | 0 | 2 |
| 2022 | PlPr XML WP20-21 | 22 | 8 | 2 | 0 | 6 |
| 2023 | PlPr XML WP20-21 | 16 | 2 | 0 | 0 | 2 |
| 2024 | PlPr XML WP20-21 | 18 | 2 | 1 | 0 | 1 |
| 2025 | PlPr XML WP20-21 | 16 | 1 | 1 | 0 | 0 |
| 2026 | PlPr XML WP20-21 | 15 | 2 | 1 | 0 | 1 |

Totals: 1,023 title hits screened; 166 items coded; 69 items match v2 items and were found independently; 2 were added only through the v2 check; 95 are new.

## 6. Limitations

**Ordinances.** Ordinances are in scope, but no Bundesgesetzblatt index was reachable for a uniform year-by-year sweep. To keep effort equal across years they are not in `items`. Seven short-time-work duration ordinances (2003-2025) found by a single web search are listed as unconfirmed leads in `ordinances_not_swept`.

**Recall of the frame.**
- In WP 4-7 the protocol extraction misses bills whose title is broken across columns; EGEStRG 1974 shows this happens.
- In WP 8-12 OCR titles are sometimes garbled; 32 GESTA records have no usable title.
- Some display filters used during hand screening were broad, for example "Steuer", "Insolvenz" or "Kinder". Laws that hide a labour change behind such a title can be missed. The 2016 SGB II law shows this happened; the 2025 Rentenpaket was caught on re-check.
- Recall is therefore probably lower for 1965-1976 and for omnibus laws.

**Content depth.**
- For about 70 items the main number was not found in the pages read, so confirmed=false. For 1969-1993 AFG laws the numbers are from the IAB chronicle (secondary).
- Pre-1972 bills have no summary sheet, so their motives are often "not seen".
- Bill versions can differ from enacted texts. Examples are Hartz II and IV, Bürgergeld, the 1996 Sozialhilfe reform, AlhiRG 1996 and Arbeitsmarktreformgesetz 2003 (threshold of ten in the final law versus fixed-term exclusion in the bill). Notes say so.

**Adoption check.** For protocol-frame items (1965-1976, 2018-2026), adoption is inferred from the reading record plus a government or coalition bill. The vote result was read for only a few. The 1967 8. AVAVG-ÄndG (an SPD group bill) is flagged.

**Very recent items.** The WissZeitVG reform passed on 12 Nov 2026; promulgation was not checked.

**Shares of cut items by stated motive** (43 cut items):

| Motive | Items | Share |
|---|---|---|
| budget/consolidation | 16 | 37% |
| demography/contribution rate | 10 | 23% |
| jobs/employment | 9 | 21% |
| other | 7 | 16% |
| EU/legal requirement | 1 | 2% |

These shares depend on the first-stated-aim rule in section 1.

## 7. Working files

The scripts and intermediate files are in the session scratchpad and may be deleted. They are:
- `scripts/parse_gm.py`, `parse_btp.py`, `parse_xml.py`, `kw.py`, `screen2.py`, `extract.py`, `grab.py`, `assemble.py`;
- the frame tables `gm_rows.json`, `btp_rows.json`, `xml_rows.json`;
- the screening lists `screen_*.txt`;
- the per-item extracts `review_*.txt`.

Every item in the YAML carries its frame reference and source URLs, so it can be re-checked without them.
