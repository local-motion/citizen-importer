# import_citizens.py

This importer allows to seed our database with citizens that have indicated
that they're interested in making venues, such as children playgrounds, smoke-free.

Note - It currently doesn't support auth, so it assumes a `kube port-forward` in case of
non-local environments.

In general, the script:
1. takes a citizen CSV file
1. turns it into JSON 
1. sends it to a `/citizens` endpoint


## Docker
### Run it as an executable (not a service)
```
docker run --rm -v $(PWD)/samples:/imports \
    localmotion/citizen-importer \
    http://localhost:8082/citizens \
    3_citizens.csv \
    <sentry-dsn>
```

### Build Docker image from source
```
docker build -t localmotion/citizen-importer .
```


## Command line
### Run it from command line

To setup:
```
virtualenv -p python3 citizens
source citizens/bin/activate
pip install -r requirements.txt
```

Then to subsequently run locally:
```
source citizens/bin/activate
CSV_SOURCE_DIRECTORY=$(pwd)/samples python src/import_citizens.py http://localhost:8082/citizens 3_citizens.csv <sentry-dsn> 
```

### Samples

Samples can be found at [Samples](./samples) in this repository.
