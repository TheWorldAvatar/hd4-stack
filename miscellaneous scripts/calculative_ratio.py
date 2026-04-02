# calculate ratio of values between two output files from the exposure calculation agent
# e.g. ratio of area with imputed public access over net area
# used to calculate confidence levels of GGPA3 results

import csv
from collections import defaultdict
import json
import pandas as pd
from pathlib import Path

path = Path('input/calculate_ratio_input.json')
if not path.exists():
    raise FileNotFoundError('calculate_ratio_input.json does not exist')

with path.open("r", encoding="utf-8") as f:
    inputs = json.load(f)

numerator_data = pd.read_csv(inputs['numerator'])
denominator_data = pd.read_csv(inputs['denominator'])

numerator_data_cols = numerator_data.columns
denominator_data_cols = denominator_data.columns

if set(numerator_data_cols) != set(denominator_data_cols):
    raise Exception('Columns of provided files must be the same')

exclude_columns = ["postal_code", "iri", "lat", "lng"]

result_columns = []

for col in numerator_data_cols:
    if col not in exclude_columns:
        result_columns.append(col)

subject_result_value_dict_numerator = defaultdict(dict)
subject_result_value_dict_denominator = defaultdict(dict)
subject_to_postal_code = {}
subject_to_lat = {}
subject_to_lng = {}
subject_result_ratio_dict = defaultdict(dict)

for row in numerator_data.itertuples(index=False):
    row_data = {}

    for col, value in zip(numerator_data_cols, row):
        row_data[col] = value

    iri = row_data["iri"]
    postal_code = row_data["postal_code"]
    lat = row_data["lat"]
    lng = row_data["lng"]

    subject_to_postal_code[iri] = postal_code
    subject_to_lat[iri] = lat
    subject_to_lng[iri] = lng

    for result_column in result_columns:
        subject_result_value_dict_numerator[iri][result_column] = row_data[result_column]

for row in denominator_data.itertuples(index=False):
    row_data = {}

    for col, value in zip(denominator_data_cols, row):
        row_data[col] = value

    iri = row_data["iri"]

    for result_column in result_columns:
        subject_result_value_dict_denominator[iri][result_column] = row_data[result_column]

for iri in subject_result_value_dict_numerator:
    for result_column in result_columns:
        numerator = subject_result_value_dict_numerator[iri][result_column]
        denominator = subject_result_value_dict_denominator[iri][result_column]

        if denominator == 0:
            ratio = None
        else:
            ratio = numerator/denominator

        subject_result_ratio_dict[iri][result_column] = ratio

data_for_csv = []
for iri in subject_result_ratio_dict:
    row_for_csv = {}
    row_for_csv['postal_code'] = subject_to_postal_code[iri]
    row_for_csv['iri'] = iri
    row_for_csv['lat'] = subject_to_lat[iri]
    row_for_csv['lng'] = subject_to_lng[iri]

    for result_column in result_columns:
        row_for_csv[result_column] = subject_result_ratio_dict[iri][result_column]

    data_for_csv.append(row_for_csv)

with open(inputs['output_file'], 'w', newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=data_for_csv[0].keys())
    writer.writeheader()
    writer.writerows(data_for_csv)
