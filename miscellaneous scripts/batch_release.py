import pandas as pd
from shapely import Point
from collections import defaultdict
import csv
from pathlib import Path
import json
from itertools import product

# combines multiple files into a single file
path = Path('input/batch_release_input.json')
if not path.exists():
    raise FileNotFoundError('batch_release_input.json does not exist')

with path.open("r", encoding="utf-8") as f:
    inputs = json.load(f)

files = inputs['input_files']

postal_code_to_header_to_value = defaultdict(dict)
for file in files:
    data = pd.read_csv(file, dtype={'postal_code': 'string'})
    cols = data.columns
    for row in data.itertuples(index=False):
        row_data = {}

        for col, value in zip(cols, row):
            row_data[col] = value

        postal_code = row_data['postal_code']
        del row_data['postal_code']

        for key, item in row_data.items():
            if key in postal_code_to_header_to_value[postal_code]:
                if postal_code_to_header_to_value[postal_code][key] != item:
                    raise Exception('not equal?')
            postal_code_to_header_to_value[postal_code][key] = item

data_for_csv = []
for key, item in postal_code_to_header_to_value.items():
    row_for_csv = {}
    row_for_csv['postal_code'] = key

    for header, value in item.items():
        row_for_csv[header] = value

    data_for_csv.append(row_for_csv)

with open(inputs['output_file'], 'w', newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=data_for_csv[0].keys())
    writer.writeheader()
    for row in data_for_csv:
        writer.writerow(row)
