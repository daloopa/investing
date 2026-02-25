---
name: guidance-tracker
description: Track management guidance accuracy over time for a given company
argument-hint: TICKER
---

Track management guidance accuracy for the company specified by the user: $ARGUMENTS

**Before starting, read the `data-access.md` reference (co-located with this skill) for data access methods and `design-system.md` for formatting conventions.** Follow the data access detection logic and design system throughout this skill.

Follow these steps:

## 1. Company Lookup
Look up the company by ticker. Extract company_id and latest available quarter.

## 2. Discover Guidance Series
Search for series with keywords like "guidance", "outlook", "estimate", "forecast", "target" to find all available guidance metrics. Common guidance series include:

**Financial guidance:**
- Revenue guidance (quarterly and/or annual)
- EPS guidance
- Operating income / margin guidance
- EBITDA guidance
- Segment-level revenue guidance
- CapEx guidance
- Free Cash Flow guidance

**Operational KPI guidance** — many companies guide on KPIs, and tracking these beats/misses is often more informative than financial guidance:
- Subscriber / user count guidance (e.g., "we expect to add X million subscribers")
- Unit shipment guidance (e.g., "iPhone units", "deliveries")
- ARPU / ASP guidance
- Same-store sales guidance
- GMV / bookings guidance
- Net revenue retention guidance
- Store openings / closings guidance
- Production volume / capacity guidance

Search explicitly for KPI-specific guidance series using terms like "subscriber guidance", "unit guidance", "ARPU guidance", "same-store sales outlook", "deliveries forecast", "bookings target". These are separate from financial guidance and often reside in different series.

## 3. Pull Guidance Data
Pull all discovered guidance series for the last 8+ quarters.

## 4. Pull Actual Results
For each guidance metric, pull the corresponding actual result series for the same periods.

## 5. Build Guidance vs Actuals Tracker
CRITICAL OFFSET RULES:
- **Quarterly guidance**: Guidance from Q(N) earnings call applies to Q(N+1) results. Compare Q(N) guidance -> Q(N+1) actual.
- **Annual guidance from Q1/Q2/Q3**: Applies to current fiscal year. Compare to FY actual.
- **Annual guidance from Q4**: Applies to NEXT fiscal year. Compare to next FY actual.

For each guidance-actual pair, calculate:
- Guidance value
- Actual value
- Delta (Actual - Guidance)
- Beat/Miss % ((Actual - Guidance) / |Guidance| x 100)
- Classification: Beat / In-line / Miss (use +/-1% threshold for in-line)

## 6. Pattern Analysis
Analyze the guidance track record:
- Overall beat rate (% of quarters where actual > guidance)
- Average beat/miss magnitude
- Trend in guidance accuracy (getting tighter? more conservative? less reliable?)
- Any metrics where management is notably conservative or aggressive
- Guidance range width trends (if range guidance is given)

**Management credibility assessment:**
- If the company consistently beats by a similar margin, call out sandbagging — this suggests management is deliberately setting low bars, which can mask underlying deceleration. A 100% beat rate is not necessarily bullish; it may mean guidance is uninformative.
- If guidance has been cut or missed, assess whether management acknowledged the miss honestly or buried it in adjusted metrics.
- Flag any pattern where qualitative language ("strong demand," "robust pipeline") didn't translate to actual results.

## 7. Commentary from Filings
Search SEC filings/documents across multiple queries to build a complete picture of guidance practices. If any search returns empty, try alternative keywords before giving up.

- **Explicit guidance language**: Try "guidance", "outlook"; fallback to "expect", "anticipate", "forecast"
- **Qualitative / directional guidance**: Try "similar to", "consistent with", "growth rate"; fallback to "low single digit", "mid single digit", "high single digit", "double digit", "sequential"
  - Many companies provide directional revenue guidance on earnings calls (e.g., "similar to the March quarter" or "low-to-mid-single-digit growth") rather than numeric ranges. Capture these and compare against actual growth rates.
- **Guidance methodology changes**: Try "change", "methodology", "no longer providing"; fallback to "withdraw", "suspend", "discontinue"
  - Flag any quarters where the company changed what metrics it guides on, or withdrew guidance entirely
- **Key drivers behind guidance**: Try "assumes", "includes", "excludes"; fallback to "headwind", "tailwind", "impact"
  - Capture what management said about the assumptions underpinning their guidance (e.g., FX assumptions, macro assumptions, one-time items included/excluded)

Extract direct management quotes where available and cite the document source.

## 8. Save Report
Save to `reports/{TICKER}_guidance_tracker.md`. The report should include:
- Summary header with company name, ticker, and period covered
- Quarter mapping table showing guidance source -> actual result period
- Main tracker table:

| Guidance Source | Metric | Guidance | Actual Period | Actual | Delta | Beat/Miss |
{with Daloopa citations on all values}

- Summary statistics (beat rate, avg beat/miss by metric)
- Pattern analysis narrative
- Key guidance quotes from filings with document citations
- All financial figures must use Daloopa citation format: [$X.XX million](https://daloopa.com/src/{fundamental_id})

## 9. Render PDF
Render the markdown report to PDF (see data-access.md Section 5 for infrastructure):
`python3 infra/pdf_renderer.py --input reports/{TICKER}_guidance_tracker.md --output reports/{TICKER}_guidance_tracker.pdf`

Tell the user where the PDF was saved. If PDF rendering fails, note the error and point them to the markdown file.

Highlight the key patterns (e.g., "Management has beat revenue guidance 7 of the last 8 quarters by an average of 2.3%"). Include an honest credibility verdict: Is management's guidance informative or performative? Should investors trust the forward guidance, and if not, what should they anchor to instead?
