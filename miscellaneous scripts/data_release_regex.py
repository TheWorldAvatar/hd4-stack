import pandas as pd
from shapely import Point
from collections import defaultdict
import csv
from pathlib import Path
import json
from itertools import product
import math
import statistics

num_postcode_header = 'GAD1_latlon_postcode'

path = Path('input/data_release_regex_inputs.json')
if not path.exists():
    raise FileNotFoundError('data_release_regex_inputs.json does not exist')

with path.open("r", encoding="utf-8") as f:
    inputs = json.load(f)

data = pd.read_csv(inputs['input_file'], dtype={'postal_code': 'string'})
columns = list(data.columns)
columns.remove('postal_code')
columns.remove('iri')
columns.remove('lat')
columns.remove('lng')

data_dictionaries = inputs['data_dictionaries']

key_mappings = inputs['key_mappings']

list_of_key_list = []
tuple_size = len(key_mappings)
for key_mapping in key_mappings:
    list_of_key_list.append(list(key_mapping.keys()))

key_combinations = list(product(*list_of_key_list))
my_header_to_dd_dict = {}
for key_combination in key_combinations:
    keys_in_dd = []
    for i, key_mapping in enumerate(key_mappings):
        keys_in_dd.append(key_mapping[key_combination[i]])

    # find column that contains all elements in key_combination
    matched_column = None
    for column in columns:
        parts = column.split('_')
        if all(word in parts for word in key_combination) and matched_column is not None:
            raise Exception('duplicate column match?')

        elif all(word in parts for word in key_combination):
            matched_column = column

    matched_dd = None

    for dd in data_dictionaries:
        if all(word in dd for word in keys_in_dd) and matched_dd is not None:
            raise Exception('duplicate dd match?')
        elif all(word in dd for word in keys_in_dd):
            matched_dd = dd

    my_header_to_dd_dict[matched_column] = matched_dd

postcode_to_subjects = {}
subject_to_point = {}
subject_to_dd_to_value = defaultdict(dict)

cols = data.columns
for row in data.itertuples(index=False):
    postal_code = row.postal_code
    point = Point(row.lng, row.lat)
    subject = row.iri

    if postal_code not in postcode_to_subjects:
        postcode_to_subjects[postal_code] = set()

    postcode_to_subjects[postal_code].add(subject)
    subject_to_point[subject] = point

    row_data = {}

    for col, value in zip(cols, row):
        row_data[col] = value

    subject = row.iri
    del row_data['postal_code']
    del row_data['lng']
    del row_data['lat']
    del row_data['iri']

    for k, v in row_data.items():
        if k not in my_header_to_dd_dict:
            continue
        dd = my_header_to_dd_dict[k]
        subject_to_dd_to_value[subject][dd] = v


data_for_csv = []
# now calculate average for each postal code if there are duplicates
for postcode, subjects in postcode_to_subjects.items():
    seen = defaultdict(list)

    # this will detect duplicate points within a postcode
    for subject in subjects:
        seen[subject_to_point[subject]].append(subject)

    subjects_to_consider = []
    # for coordinates that are repeated, only pick the first element
    for values in seen.values():
        subjects_to_consider.append(values[0])

    num_points = len(subjects_to_consider)

    result_headers = subject_to_dd_to_value[subjects_to_consider[0]].keys()

    list_for_average = defaultdict(list)

    for subject in subjects_to_consider:
        for result_header in result_headers:
            if not math.isnan(subject_to_dd_to_value[subject][result_header]):
                list_for_average[result_header].append(
                    subject_to_dd_to_value[subject][result_header])

    row_for_csv = {}
    row_for_csv['postal_code'] = postcode
    row_for_csv[num_postcode_header] = num_points

    for result_header in result_headers:
        row_for_csv[result_header] = statistics.mean(
            list_for_average[result_header])

    data_for_csv.append(row_for_csv)


def format_row(row, decimals):
    return {
        k: f"{v:.{decimals}f}" if isinstance(v, float) else v
        for k, v in row.items()
    }


with open(inputs['output_file'], 'w', newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=data_for_csv[0].keys())
    writer.writeheader()
    number_of_decimals = inputs['number_of_decimals']
    for row in data_for_csv:
        writer.writerow(format_row(row, decimals=number_of_decimals))
