import csv
import os
from pathlib import Path

import requests
import sys

from raven import Client

imports_directory = os.environ['CSV_SOURCE_DIRECTORY']
print("CSV source directory: {}".format(imports_directory))

if len(sys.argv) != 4:
    print("Usage: python {} http://localhost:8082/citizens samples/3_citizens.csv <sentry-dsn>".format(Path(__file__).name))
    sys.exit(1)

target_endpoint = sys.argv[1]
source = imports_directory + "/" + sys.argv[2]
sentry_dsn = sys.argv[3]

print("Endpoint: {}".format(target_endpoint))
print("CSV source file: {}".format(source))
print("Connecting to Sentry using DSN {}".format(sentry_dsn))

sentry = Client(sentry_dsn)

with open(source, 'rt') as csv_file:
    reader = csv.DictReader(csv_file)

    for row in reader:
        print(row)
        # noinspection PyBroadException
        try:
            r = requests.post(target_endpoint, data=row)
            print(r)
        except BaseException:
            sentry.captureException()