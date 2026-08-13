import json
import requests
from pathlib import Path

path = Path('input/create_layer_input.json')

if not path.exists():
    raise FileNotFoundError('create_layer_input.json does not exist')

with path.open("r", encoding="utf-8") as f:
    inputs = json.load(f)

url = inputs['url']

print(
    f"Submitting request to {url}, check the agent container logs for more details")
result = requests.post(url=url, json=inputs)
if result.status_code != 200:
    print(result.text)
    print('Something wrong happened, check the agent container logs for more details')
