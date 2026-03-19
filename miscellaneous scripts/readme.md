# Miscellaneous scripts

This folder contains scripts to interact with the exposure calculation agent (generate_results.py and download_results.oy)

## generate_result.py

Prepare a file called `generate_results_inputs.json` in the `input` folder (a template is given - [input/generate_results_inputs.example.json](input/generate_results_inputs.example.json)). This sends the contents of the input file to the specified url (trigger_calculation of the exposure calculation agent). For details on the inputs please refer to <https://github.com/TheWorldAvatar/exposure-calculation-agent>

## download_results.py

Similar to generate_result.py, prepare a file called `download_results_inputs.json` in the `input` folder (a template is given - [input/download_results_inputs.example.json](input/download_results_inputs.example.json)). For details on the inputs please refer to <https://github.com/TheWorldAvatar/exposure-calculation-agent>

## data_release.py

This script converts CSV output from the exposure calculation agent to match it with the corresponding data dictionaries, also calculates average for each repeated postal code.

## preprocess_greenspace_properties.py

This script prepares the greenspace_properties vector file required to augment the accompanying raster data. It removes unncessary properties for calculations and converts values into boolean. Example input file: [preprocess_greenspace_properties_inputs.example.json](preprocess_greenspace_properties_inputs.example.json).

## generate_contour_from_tif.py

Purely for visualisation, reads in raster files and produces geojson files with polygons with accompanying colours.
