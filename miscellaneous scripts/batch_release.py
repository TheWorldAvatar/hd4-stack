import pandas as pd
from collections import defaultdict
import csv
from pathlib import Path
import json


def read_release_csv(file):
    data = pd.read_csv(file, dtype={'postal_code': 'string'})
    data = data.loc[:, ~data.columns.str.match(r'^Unnamed:')]
    if 'GAD_1_latlon_postcode' in data.columns:
        if 'GAD1_latlon_postcode' in data.columns:
            raise ValueError(f'{file}: both GAD postcode headers are present')
        data = data.rename(columns={'GAD_1_latlon_postcode': 'GAD1_latlon_postcode'})
    if 'postal_code' not in data.columns:
        raise ValueError(f'{file}: postal_code must be present')
    # Exclude blanks, NIL/NA markers, and other malformed Singapore postcodes.
    # String dtype preserves leading zeroes; valid codes must have six ASCII digits.
    data = data.loc[data['postal_code'].str.fullmatch(r'[0-9]{6}', na=False)].copy()
    if data['postal_code'].dropna().duplicated().any():
        raise ValueError(f'{file}: non-empty postal_code values must be unique')
    return data

# combines multiple files into a single file
path = Path('input/batch_release_input.json')
if not path.exists():
    raise FileNotFoundError('batch_release_input.json does not exist')

with path.open("r", encoding="utf-8") as f:
    inputs = json.load(f)

files = list(Path(inputs['folder']).glob("*.csv"))
if not files:
    raise ValueError(f"No CSV files found in {inputs['folder']}")

headers = set()
# collect headers, and make sure each file has a postal_code header
for file in files:
    data = read_release_csv(file)
    cols = list(data.columns)

    if 'postal_code' not in cols:
        raise Exception('postal_code must be present')
    headers.update(cols)

postal_codes_not_equal = set()
postal_code_to_header_to_value = defaultdict(dict)
for file in files:
    data = read_release_csv(file)
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
    print(f'Conflicting GAD1_latlon_postcode values: {len(postal_codes_not_equal)} postcodes')

# This file supplies only GAD values; other columns and extra postcodes are ignored.
if inputs.get('gad1_source_file'):
    source = read_release_csv(Path(inputs['gad1_source_file']))
    if 'GAD1_latlon_postcode' not in source.columns:
        raise ValueError('gad1_source_file must contain GAD1_latlon_postcode (or GAD_1_latlon_postcode)')
    gad_values = source.set_index('postal_code')['GAD1_latlon_postcode']
    gad_values = gad_values.to_dict()
    unmatched_count = 0
    for postal_code, values in postal_code_to_header_to_value.items():
        if postal_code in gad_values:
            values['GAD1_latlon_postcode'] = gad_values[postal_code]
        else:
            unmatched_count += 1
    print(f"Using GAD1_latlon_postcode from {inputs['gad1_source_file']}")
    print(f'Keeping existing GAD values for {unmatched_count} rows absent from the preferred source')

data_for_csv = []
result_headers_set = set()

for key, item in postal_code_to_header_to_value.items():
    row_for_csv = {}
    row_for_csv['postal_code'] = key

    for header, value in item.items():
        if pd.isna(value):
            row_for_csv[header] = ''
        else:
            row_for_csv[header] = value
        result_headers_set.add(header)

    data_for_csv.append(row_for_csv)

if 'GAD1_latlon_postcode' not in result_headers_set:
    raise ValueError('No GAD1_latlon_postcode column found; configure gad1_source_file')

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
