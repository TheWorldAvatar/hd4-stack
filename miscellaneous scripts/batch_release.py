import pandas as pd
from collections import defaultdict
import csv
from pathlib import Path
import json
import math

# combines multiple files into a single file
path = Path('input/batch_release_input.json')
if not path.exists():
    raise FileNotFoundError('batch_release_input.json does not exist')

with path.open("r", encoding="utf-8") as f:
    inputs = json.load(f)

files = list(Path(inputs['folder']).glob("*.csv"))

headers = set()
# collect headers, and make sure each file has a postal_code header
for file in files:
    data = pd.read_csv(file, dtype={'postal_code': 'string'})
    cols = list(data.columns)

    if 'postal_code' not in cols:
        raise Exception('postal_code must be present')
    headers.update(cols)

postal_codes_not_equal = set()
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
                if key == 'GAD1_latlon_postcode' and postal_code_to_header_to_value[postal_code][key] != item:
                    postal_codes_not_equal.add(postal_code)
            postal_code_to_header_to_value[postal_code][key] = item

if len(postal_codes_not_equal) > 0:
    print(postal_codes_not_equal)

data_for_csv = []
result_headers_set = set()

for key, item in postal_code_to_header_to_value.items():
    row_for_csv = {}
    row_for_csv['postal_code'] = key

    for header, value in item.items():
        if math.isnan(value):
            row_for_csv[header] = ''
        else:
            row_for_csv[header] = value
        result_headers_set.add(header)

    data_for_csv.append(row_for_csv)

with open(inputs['output_file'], 'w', newline="", encoding="utf-8") as f:
    headers = ['postal_code']
    headers.append('GAD1_latlon_postcode')

    remaining_headers = list(result_headers_set)
    remaining_headers.remove('GAD1_latlon_postcode')
    remaining_headers.sort()

    headers.extend(remaining_headers)
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for row in data_for_csv:
        writer.writerow(row)
