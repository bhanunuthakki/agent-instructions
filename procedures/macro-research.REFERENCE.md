# Econvitals source notes

Reviewed 2026-10-25. Use Econvitals as a convenient macro entry point. This was a
sample review, not validation of all series, models, or narratives.

## Retrieval

The HTML is largely a shell. Read the topic page or follow the current public
loader in [shared.js](https://econvitals.org/assets/shared.js). It resolves a commit
of [econvitals/econvitals-data](https://github.com/econvitals/econvitals-data) and
reads repository files from that commit. Pin related files to one commit.

At review, repository dashboard data were dated October 25, while
[the same-origin fallback](https://econvitals.org/data/dashboard.json) was dated
August 10. Check observation periods and source timestamps. Never assume a
successful request or current page date means the underlying figures are current.
Separate overlays can have different timestamps.

[Calendar data](https://econvitals.org/data/calendar.json) and
[methods](https://econvitals.org/methods/methods.json) were loaded directly from the
site. Repository paths are observed implementation, not a stable API contract.
Recheck the loader if paths, schemas, or rendered values diverge.

Fetch on demand. Reuse unchanged verified evidence and conditional HTTP responses.
No crawler, embedding store, scheduled indexing, or application integration is
needed for the current workflow.

## Evidence and limits

These displayed readings matched official releases at review:

| Reading | Official evidence |
| --- | --- |
| September 2026 payroll change +29,000; unemployment 4.2% | [BLS jobs release](https://www.bls.gov/news.release/archives/empsit_10022026.htm) |
| September 2026 core CPI, 12-month change 2.6% | [BLS CPI release](https://www.bls.gov/news.release/archives/cpi_10142026.htm) |
| Q2 2026 real GDP, quarterly annual rate 2.2% | [BEA](https://apps.bea.gov/scb/issues/2026/10-october/1026-charting-economy.htm) |

The [About page](https://econvitals.org/about/) describes mainly U.S. coverage.
The [terms](https://econvitals.org/terms/) state that most writing is AI-generated
without review before publication. Keep official observations, calculations,
site estimates, market expectations, and commentary distinct. Verify material
narrative claims and decision-driving facts with primary evidence when needed.
Today's revised series cannot establish what was known at a historical date.
