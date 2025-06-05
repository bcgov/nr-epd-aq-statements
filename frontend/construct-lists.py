import datetime
import os
import re

import yaml

"""
This script generates two files as part of the pre-render process for quarto site generation

RECENTS_FILE_NAME will contain a yaml list of files with a date attribute newer than RECENT_THRESHOLD_DAYS 
or that is present in the metro van warnings yaml 

WILDFIRE_FILE_NAME will contain any with an `wildfire_smoke` meta attribute in type

These are then used in custom listings within the qmd markup
"""

# editable -- consider posts less than RECENT_THRESHOLD_DAYS days old to be "recent"
# Hardcoded below to 1 day for smoky skies bulletins with ice = Issue metadata
RECENT_THRESHOLD_DAYS = 5

# file names for different warning types
RECENTS_FILE_NAME = '_recent_warnings.yaml'
WILDFIRE_FILE_NAME = '_wildfire.yaml'

# globals. do not modify.
INPUT_FILES = os.getenv('QUARTO_PROJECT_INPUT_FILES').split("\n")
HEADER_REGEX = re.compile('^---\n((.*\n)+)---\n', re.MULTILINE)

# define where the metro vancouver warnings will be
METRO_VAN_FILE_NAME = '_metro_van_warnings.yaml'

RECENT_WARNINGS = []
WILDFIRE_SMOKE_WARNINGS = []


def process_yaml_files():
    # for warnings issued by Metro Vancouver and added to METRO_VAN_FILE_NAME
    with open(METRO_VAN_FILE_NAME, 'r') as file:
        print("processing input file: {file}".format(file=METRO_VAN_FILE_NAME))
        metro_van_warnings = yaml.safe_load(file)

        if metro_van_warnings:
            for entry in metro_van_warnings:
            # append all entrieds that are within the threshold number of days
                if 'date' in entry: 
                    age = (datetime.date.today() - parsed_header['date']).days
                    if age < RECENT_THRESHOLD_DAYS:
                        RECENT_WARNINGS.append(entry)  

def process_input_files():
    # for warnings in the quarto project
    for f in INPUT_FILES:
        if not f:
            continue  # skip empty input lines

        print("processing input file: {file}".format(file=f))

        with open(f, 'r') as file:
            contents = file.read()
            match = HEADER_REGEX.search(contents)
            if match:
                doc_preamble = match.group(1)
                parsed_header = yaml.safe_load(doc_preamble)

                # what goes in the generated yaml
                entry_from_header = {
                    'path': f,
                    'title': parsed_header['title'],
                    'type': parsed_header['type'] if 'type' in parsed_header else 'N/A',
                    'ice': parsed_header['ice'] if 'ice' in parsed_header else 'N/A',
                    'date': parsed_header['date'] if 'date' in parsed_header else None,
                    'location': parsed_header['location'] if 'location' in parsed_header else None,
                }

                if 'type' in parsed_header and parsed_header['type'].lower() == 'wildfire_smoke':
                    if 'date' in parsed_header:
                        age = (datetime.date.today() - parsed_header['date']).days
                        threshold = RECENT_THRESHOLD_DAYS

                        if 'ice' in parsed_header and parsed_header['ice'].lower() == 'issue':
                            threshold = 1  # Only 1 day for wildfire_smoke with ice = Issue

                        if age < threshold:
                            WILDFIRE_SMOKE_WARNINGS.append(entry_from_header)

                # not mutually exclusive with wildfire_smoke
                if 'date' in parsed_header:
                    skip = False

                    # only add the most recent issued wildfire_smoke due to the differences in warning
                    # comment this out to not have separate behaviour for wildfire_smoke
                    if 'type' in parsed_header and parsed_header['type'].lower() == 'wildfire_smoke':
                        if 'ice' in parsed_header and parsed_header['ice'].lower() == 'issue':
                            age = (datetime.date.today() - parsed_header['date']).days
                            threshold = 1  # Only 1 day for wildfire_smoke with ice = Issue

                        if age >= threshold:
                            skip = True

                    if not skip:
                        age = (datetime.date.today() - parsed_header['date']).days
                        if age < RECENT_THRESHOLD_DAYS:
                            RECENT_WARNINGS.append(entry_from_header)

print(METRO_VAN_FILE_NAME)

process_yaml_files()

print(yaml.safe_dump(INPUT_FILES))

process_input_files()

with open(RECENTS_FILE_NAME, 'w') as output_file:
    yaml.safe_dump(RECENT_WARNINGS, output_file)

with open(WILDFIRE_FILE_NAME, 'w') as output_file:
    yaml.safe_dump(WILDFIRE_SMOKE_WARNINGS, output_file)
