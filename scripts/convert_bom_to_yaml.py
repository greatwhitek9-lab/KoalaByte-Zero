#!/usr/bin/env python3
"""Convert legacy docs/BOM (tab-separated) into docs/bom.yaml.

Usage: python3 scripts/convert_bom_to_yaml.py
Writes to docs/bom.yaml overwriting if present.
"""
from pathlib import Path
import csv
import yaml

repo_root = Path(__file__).resolve().parents[1]
tsv = repo_root / 'docs' / 'BOM'
out = repo_root / 'docs' / 'bom.yaml'

if not tsv.exists():
    print("No legacy BOM file found at", tsv)
    raise SystemExit(1)

items = []
with tsv.open(encoding='utf-8') as fh:
    reader = csv.DictReader(fh, delimiter='\t')
    for row in reader:
        ref = (row.get('Ref') or row.get('ref') or '').strip()
        if not ref:
            continue
        entry = {
            'ref': ref,
            'qty': int(row.get('Qty') or row.get('qty') or 1),
            'manufacturer': row.get('Manufacturer/Series') or row.get('Manufacturer') or '',
            'mpn': row.get('MPN / Module') or row.get('MPN') or '',
            'footprint': row.get('Footprint strategy') or '',
            'mount': row.get('Mount') or '',
            'notes': row.get('Notes') or '',
        }
        items.append(entry)

with out.open('w', encoding='utf-8') as fh:
    yaml.safe_dump(items, fh, sort_keys=False)

print('Wrote', out)
