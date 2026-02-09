from itertools import product
import json
import requests
from datetime import datetime, timezone
from pathlib import Path

path = Path('input/generate_results_inputs.json')

if not path.exists():
    raise FileNotFoundError('generate_results_inputs.json does not exist')

with path.open("r", encoding="utf-8") as f:
    inputs = json.load(f)

exposure_table = inputs['exposure_table']
rdf_types = inputs['rdf_types']
distances = inputs['distances']

dataset_filter_values = inputs['dataset_filter_values']

# produces a cartesian product between the dataset_filter_values
dataset_filters = [
    dict(zip(dataset_filter_values.keys(), combo))
    for combo in product(*dataset_filter_values.values())
]

base_url = inputs['url']


def post(distance, dataset_filter, rdf_type):
    params = {"distance": distance,
              "dataset_filter": json.dumps(dataset_filter),
              "exposure_table": exposure_table,
              "subject_query_file": "subject_query.sparql",
              "rdf_type": rdf_type}
    result = requests.post(url=base_url, params=params)
    print(datetime.now(timezone.utc))
    if result.status_code != 200:
        print(
            f"Failed request, distance = {distance}, dataset_filter = {dataset_filter}, rdf_type = {rdf_type}")
        print(result.content)
    else:
        print(
            f"Success, distance = {distance}, dataset_filter = {dataset_filter}, rdf_type = {rdf_type}")


for rdf_type in rdf_types:
    for distance in distances:
        for dataset_filter in dataset_filters:
            post(distance, dataset_filter, rdf_type)
