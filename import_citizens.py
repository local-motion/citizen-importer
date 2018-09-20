import csv
from pathlib import Path

import requests
import sys

if len(sys.argv) != 3:
    print("Usage: python {} http://localhost:8082/citizens samples/3_citizens.csv".format(Path(__file__).name))
    sys.exit(1)

target_endpoint = sys.argv[1]
source = sys.argv[2]

with open(source, 'rt') as csv_file:
    reader = csv.DictReader(csv_file)

    for row in reader:
        print(row)
        r = requests.post(target_endpoint, data=row)
        print(r)
