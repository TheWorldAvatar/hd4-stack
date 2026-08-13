import pandas as pd
from shapely import Point
from collections import defaultdict
import csv

# this script is written for a release that bypass using the data dictionary

input_file = 'downloads/closest_park.csv'

num_postcode_header = 'GAD1_latlon_postcode'
output_file = 'processed/closest_park_release.csv'

postcode_to_subjects = {}
subject_to_point = {}

subject_to_dd_to_value = defaultdict(dict)

my_header_to_dd_dict = {"d0": "GGPA646_ed_n_2023"}

# generate postcode_to_subjects and subject_to_point
data = pd.read_csv(input_file, dtype={'postal_code': 'string'})
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


def format_row(row):
    # limit 2 decimal places
    return {
        k: f"{v:.2f}" if isinstance(v, float) else v
        for k, v in row.items()
    }


with open(output_file, 'w', newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=data_for_csv[0].keys())
    writer.writeheader()
    for row in data_for_csv:
        writer.writerow(format_row(row))
