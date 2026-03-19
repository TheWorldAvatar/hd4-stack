import json
import requests
from pathlib import Path

path = Path('input/download_results_inputs.json')

if not path.exists():
    raise FileNotFoundError('download_results_inputs.json does not exist')

with path.open("r", encoding="utf-8") as f:
    inputs = json.load(f)

response = requests.post(url=inputs['url'], json=inputs)

with open(inputs['output_file'], "wb") as f:
    f.write(response.content)
