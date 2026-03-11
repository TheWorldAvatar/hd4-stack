import json
import requests
from pathlib import Path

path = Path('input/generate_results_inputs.json')

if not path.exists():
    raise FileNotFoundError('generate_results_inputs.json does not exist')

with path.open("r", encoding="utf-8") as f:
    inputs = json.load(f)

url = inputs['url']

print(
    f"Submitting request to {url}, check the agent container logs for more details")
result = requests.post(url=url, json=inputs)
if result.status_code != 200:
    print('Something wrong happened, check the agent container logs for more details')
