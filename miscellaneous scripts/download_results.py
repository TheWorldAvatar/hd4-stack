import json
import requests
from itertools import product
from pathlib import Path

path = Path('input/download_results_inputs.json')

if not path.exists():
    raise FileNotFoundError('download_results_inputs.json does not exist')

with path.open("r", encoding="utf-8") as f:
    inputs = json.load(f)

exposure_table = inputs['exposure_table']
rdf_type = inputs['rdf_type']

dataset_filter_values = inputs['dataset_filter_values']

# produces a cartesian product between the dataset_filter_values
dataset_filters = [
    dict(zip(dataset_filter_values.keys(), combo))
    for combo in product(*dataset_filter_values.values())
]

dataset_filters_as_string = [json.dumps(d) for d in dataset_filters]

base_url = inputs['url']

# for dataset_filter in dataset_filters:
params = {"subject_query_file": "subject_query.sparql",
          "subject_label_query_file": "subject_label_query.sparql",
          "rdf_type": rdf_type,
          "exposure_table": exposure_table,
          "dataset_filter": dataset_filters_as_string,
          "multiplication_factor": inputs['multiplication_factor']}

response = requests.get(url=base_url, params=params)

with open(inputs['output_file'], "wb") as f:
    f.write(response.content)
