# import_citizens.py

This importer allows to seed our database with citizens that have indicated
that they're interested in making venues, such as children playgrounds, smoke-free.

Note - It currently doesn't support auth, so it assumes a `kube port-forward` in case of
non-local environments.

In general, the script:
1. takes a citizen CSV file
1. turns it into JSON 
1. sends it to a `/citizens` endpoint

Run as:
```
python import_citizens.py <server-endpoint> <csv-file>
```

### Run it

To setup:
```commandline
virtualenv -p python3 citizens
source citizens/bin/activate
pip install -r requirements.txt
```

Then to subsequently run locally:
```commandline
source citizens/bin/activate
python import_citizens.py http://localhost:8082/citizens samples/3_citizens.csv 
```

### Samples

Samples can be found at [Samples](./samples) in this repository.
