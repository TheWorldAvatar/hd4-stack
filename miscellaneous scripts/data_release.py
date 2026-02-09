import pandas as pd
from shapely import Point
from collections import defaultdict
import csv
from pathlib import Path
import json

path = Path('input/data_release_inputs.json')
if not path.exists():
    raise FileNotFoundError('data_release_inputs.json does not exist')

with path.open("r", encoding="utf-8") as f:
    inputs = json.load(f)

input_file_to_data_dictionary_filter = inputs['input_file_to_data_dictionary_filter']

data_dictionary = pd.read_excel(
    inputs['data_dictionary'], sheet_name='text join GGPA', na_values="\xa0")

num_postcode_header = 'GAD1_latlon_postcode'
output_file = inputs['output_file']

postcode_to_subjects = {}
subject_to_point = {}
# subject_to_result = {}
subject_to_dd_to_value = defaultdict(dict)

years = range(2016, 2026)
distances = [400, 800, 1000]
my_header_to_dd_dict = {}

row_number = 0

# generate postcode_to_subjects and subject_to_point which should be the same across different input files
# so just pick the first input file
data = pd.read_csv(next(iter(input_file_to_data_dictionary_filter)), dtype={
                   'postal_code': 'string'})
row_number = data.shape[0]
for row in data.itertuples(index=False):
    postal_code = row.postal_code
    point = Point(row.lng, row.lat)
    subject = row.iri

    if postal_code not in postcode_to_subjects:
        postcode_to_subjects[postal_code] = set()

    postcode_to_subjects[postal_code].add(subject)
    subject_to_point[subject] = point

# generate result_dict
for input_file, data_dictionary_filter in input_file_to_data_dictionary_filter.items():
    print(f"Reading {input_file}")
    data = pd.read_csv(input_file, dtype={'postal_code': 'string'})

    if row_number != data.shape[0]:
        # check number of rows is the same with previous, may not be the strongest check
        raise Exception('Number of rows across input files is not consistent')

    cols = data.columns

    my_header_to_dd_dict = {}

    # find the corresponding data dictionary for my headers
    for y in years:
        for d in distances:
            mask = pd.Series(True, index=data_dictionary.index)
            mask &= data_dictionary["period"] == y
            mask &= data_dictionary["buffer"] == d

            for k, v in data_dictionary_filter.items():
                if v is None:
                    mask &= data_dictionary[k].isna()
                else:
                    mask &= data_dictionary[k] == v

            values = data_dictionary.loc[
                mask,
                "SG100K_variable_name (Formula)"
            ]
            if values.size != 1:
                raise Exception('Cannot find corresponding data dictionary')
            # hardcoded in exposure calculation agent
            my_header_to_dd_dict[f"d{d}_y{y}"] = values.iloc[0]

    # row loop
    for row in data.itertuples(index=False):
        row_data = {}

        for col, value in zip(cols, row):
            row_data[col] = value

        subject = row.iri
        del row_data['postal_code']
        del row_data['lng']
        del row_data['lat']
        del row_data['iri']

        for k, v in row_data.items():
            dd = my_header_to_dd_dict[k]
            subject_to_dd_to_value[subject][dd] = v

# now calculate average for each postal code if there are duplicates
data_for_csv = []
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

    total_val = {}
    for result_header in result_headers:
        total_val[result_header] = 0

    for subject in subjects_to_consider:
        for result_header in result_headers:
            total_val[result_header] += subject_to_dd_to_value[subject][result_header]

    row_for_csv = {}
    row_for_csv['postal_code'] = postcode
    row_for_csv[num_postcode_header] = num_points

    for result_header in result_headers:
        row_for_csv[result_header] = total_val[result_header] / num_points

    data_for_csv.append(row_for_csv)

with open(output_file, 'w', newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=data_for_csv[0].keys())
    writer.writeheader()
    writer.writerows(data_for_csv)
