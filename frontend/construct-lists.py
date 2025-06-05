import datetime
import pytz
import os
import re

import yaml

"""
This script generates two files as part of the pre-render process for quarto site generation

RECENTS_FILE_NAME will contain a yaml list of files with a date attribute newer than RECENT_THRESHOLD_DAYS

WILDFIRE_FILE_NAME will contain any with an `wildfire_smoke` meta attribute set to True

These are then used in custom listings within the qmd markup
"""

# editable -- consider posts less than RECENT_THRESHOLD_DAYS days old to be "recent"
# Hardcoded below to 1 day for smoky skies bulletins with ice = Issue metadata
RECENT_THRESHOLD_DAYS = 5
RECENTS_FILE_NAME = '_recent_warnings.yaml'

WILDFIRE_FILE_NAME = '_wildfire.yaml'

# globals. do not modify.
INPUT_FILES = os.getenv('QUARTO_PROJECT_INPUT_FILES').split("\n")
HEADER_REGEX = re.compile('^---\n((.*\n)+)---\n', re.MULTILINE)

RECENT_WARNINGS = []
WILDFIRE_SMOKE_WARNINGS = []


def get_today_in_bc_timezone():
    # Use Pacific Time (Vancouver)
    bc_tz = pytz.timezone("America/Vancouver")
    now_in_bc = datetime.datetime.now(pytz.utc).astimezone(bc_tz)
    return now_in_bc.date()


def process_input_files():
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
                        age = (get_today_in_bc_timezone() - parsed_header["date"]).days
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
                            age = (get_today_in_bc_timezone() - parsed_header["date"]).days
                            threshold = 1  # Only 1 day for wildfire_smoke with ice = Issue

                        if age >= threshold:
                            skip = True

                    if not skip:
                        age = (get_today_in_bc_timezone() - parsed_header["date"]).days
                        if age < RECENT_THRESHOLD_DAYS:
                            RECENT_WARNINGS.append(entry_from_header)


print(yaml.safe_dump(INPUT_FILES))

process_input_files()

with open(RECENTS_FILE_NAME, 'w') as output_file:
    yaml.safe_dump(RECENT_WARNINGS, output_file)

with open(WILDFIRE_FILE_NAME, 'w') as output_file:
    yaml.safe_dump(WILDFIRE_SMOKE_WARNINGS, output_file)
