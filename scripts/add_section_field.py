#!/usr/bin/env python3
"""
Add a 'section' field to each series in sp500_company_series.json.
Section = text before the first '|' in full_series_name, stripped.
"""

import json
import os

PROCESSED_DIR = os.path.join(os.path.dirname(__file__), '..', 'processed')
JSON_PATH = os.path.join(PROCESSED_DIR, 'sp500_company_series.json')

with open(JSON_PATH, 'r') as f:
    data = json.load(f)

total_series = 0
sections_seen = set()

for ticker, company in data.items():
    for series in company.get('series', []):
        name = series.get('full_series_name', '')
        section = name.split('|')[0].strip() if '|' in name else name.strip()
        series['section'] = section
        sections_seen.add(section)
        total_series += 1

with open(JSON_PATH, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Updated {total_series} series across {len(data)} companies")
print(f"\nUnique sections found ({len(sections_seen)}):")
for s in sorted(sections_seen):
    print(f"  - {s}")
