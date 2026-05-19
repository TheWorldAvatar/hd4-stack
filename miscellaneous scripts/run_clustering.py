import json
import requests
from pathlib import Path
from shapely import wkt
import csv

path = Path('input/clustering_input.json')

if not path.exists():
    raise FileNotFoundError('clustering_input.json does not exist')

with path.open("r", encoding="utf-8") as f:
    inputs = json.load(f)

url = inputs['url']

print(
    f"Submitting request to {url}, check the agent container logs for more details")
result = requests.get(url=url, json=inputs)

parsed_result = json.loads(result.text)

subject_to_lat_dict = {}
subject_to_lng_dict = {}
subject_to_point_dict = parsed_result['subject_to_point_dict']

for subject, point in subject_to_point_dict.items():
    point = wkt.loads(point)
    subject_to_lat_dict[subject] = point.y
    subject_to_lng_dict[subject] = point.x

for i, combination in enumerate(parsed_result['combinations']):
    data_for_cluster_csv = []

    for subject, cluster in combination['subject_to_cluster'].items():
        row_for_csv = {}
        row_for_csv['iri'] = subject
        row_for_csv['lat'] = subject_to_lat_dict[subject]
        row_for_csv['lng'] = subject_to_lng_dict[subject]
        row_for_csv['cluster'] = cluster

        data_for_cluster_csv.append(row_for_csv)

    data_for_cluster_info_csv = []

    for cluster, info in combination['cluster_info'].items():
        row_for_csv = {}
        row_for_csv['cluster'] = cluster
        row_for_csv['centre'] = info['centre']
        row_for_csv['min'] = info['min']
        row_for_csv['max'] = info['max']
        row_for_csv['count'] = info['count']
        data_for_cluster_info_csv.append(row_for_csv)

    with open(f"processed/cluster_{i}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data_for_cluster_csv[0].keys())
        writer.writeheader()
        writer.writerows(data_for_cluster_csv)

    with open(f"processed/cluster_info_{i}.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=data_for_cluster_info_csv[0].keys())
        writer.writeheader()
        writer.writerows(data_for_cluster_info_csv)


if result.status_code != 200:
    print(result.text)
    print('Something wrong happened, check the agent container logs for more details')
