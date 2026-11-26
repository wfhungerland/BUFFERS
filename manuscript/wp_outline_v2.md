# Working paper, outline v2 (26.11.2026)

Working title: **Cushioned: how Germany's labour-market buffers took unemployment out of its politics, and why reform stalls**

## Thesis

Germany's post-war model was built to protect workers from the labour-market costs of downturns. By the 2020s it does this so well for most people that a deep slump no longer produces the signal that used to force reform: visible unemployment and open conflict between labour and capital over who pays. In 2022-25 output fell well short of its path, but unemployment barely rose, people judged their own situation as good as in boom years, and parliament argued about prices, location and bureaucracy rather than about the labour market. Core labour-market institutions were extended, cuts fell on the margin. Historically, Germany cut its core institutions only when unemployment rose sharply. The buffers that make the model socially successful thus also remove the trigger for adjusting it to an external shock (energy, China, demography) that needs adjustment. And the protected core is shrinking: union density and bargaining coverage have fallen for decades, so the buffers protect a smaller group, while the burden falls on entrants and the unemployed.

Claim status: the pattern is documented over 75 years with four independent measures; the causal step (no visible losers -> no reform coalition) is an interpretation, consistent with the data but not proven.

## Sections

| # | Section | Content | Evidence (status) |
|---|---|---|---|
| 1 | Introduction | Puzzle: large slump, calm households, no labour-market reform; thesis; contribution | |
| 2 | Literature | Crisis and reform (Drazen-Grilli, Pitlik-Wirth, Høj et al.); Olson's distributional coalitions; Modell Deutschland and its end (Streeck); dualisation (Palier-Thelen, Emmenegger et al., Hassel); sociotropic vs pocketbook judgements (Kinder-Kiewiet) | to write; references partly verified |
| 3 | Data | AMECO/OECD, BA flows, CPP-BT plenary corpus, Politbarometer ZA2391, reform coding, strike and bargaining series | done |
| 4 | The slump and the labour market | Shortfall 3-5 points of potential; Okun response 2022-25 about -0.3 vs -0.55 before 2006 (with s.e.); adjustment through fewer exits from unemployment (vs 2015-18 and 2019), dismissals since 2022; no hours hoarding unlike 2009; supply share of the employment gap 46-70 % | done (results/okun_inference.md, flows_groups.md, okun_hours.md, employment_split.md) |
| 5 | What people saw | Unemployment named as top problem: 84 % (2005) -> 4 % (2024), r = 0.97 with the rate; own economic situation net +49 in 2024 against +31/+32 in 1993/2003 while the country is judged bad; prices top problem 2022-23 | done (results/politbarometer.md) |
| 6 | What parliament debated | Topic map 1949-2026: before 2003, unemployment moved wages, social justice, debt and location debates with it; after 2003 the link is gone; 2022 prices and energy; 2020s record for location/competitiveness/bureaucracy; worker-protection talk 12 vs 109 (2003). Dictionary precision 0.75-1.00 | done (results/plenum_topics.md, plenum_attention.md, precision files) |
| 7 | Conflict between labour and capital | Strike days per 1,000 employees 14 (2023) vs 5 (2003): conflict moved to wages after inflation, not to jobs or reform; union density 34 % (1960) -> 14 % (2024); sector-agreement coverage 69 -> 43 % West since 1996: a shrinking protected core | done (coding/conflict_series.csv) |
| 8 | When reform happened | Fixed-window coding of 65 laws in nine downturns: core cuts in 1973-75, 1979-83, 1991-93, 2001-05, exactly the episodes with unemployment rises of at least 2.5 points; none otherwise; 2022-26 extensions at the core, cuts at the margin; BA deficit as rival explanation, with counter-examples (1977, 1986, pensions) | done (coding/reform_coding_v2.yaml, ba_budget.csv) |
| 9 | Mechanism and discussion | Buffers -> few visible losers among voters and members -> no coalition for core reform; reform pressure redirected to energy, location, bureaucracy; why adjustment to an external shock stalls; risks (shrinking core, burden on outsiders, Japan) | interpretation |
| 10 | Limits and tests | Few episodes; text measures; survey coding; causal step; what would refute it before 2029 | |
| 11 | Conclusion | | |

Length: about 9,000 words plus appendix. Figures: (1) unemployment salience in survey and parliament vs unemployment rate, 1977-2025; (2) own vs country judgement 1977-2024; (3) topic groups by decade; (4) reform episodes vs rise in unemployment.

Dropped from v1: the claim that 2022-25 is unique in parliamentary attention (the break came after 2000); the employment split extrapolating falling unemployment; Länder flows.
