# import_citizens.py [![Build Status](https://travis-ci.org/local-motion/citizen-importer.svg?branch=master)](https://travis-ci.org/local-motion/citizen-importer)

This importer allows to seed our database with citizens that have indicated
that they're interested in making venues, such as children playgrounds, smoke-free.

Note - It currently doesn't support auth, so it assumes a `kube port-forward` in case of
non-local environments.

In general, the script:
1. Sets up mailchimp for testing
    1. Creates campaign
    1. Creates list
    1. Creates template
    1. Creates merge tags
    1. Uploads logo
    1. Note that each import run will re-use existing campaigns, lists, templates, etc
1. Takes a citizen CSV file
1. Turns it into JSON
1. For each citizen
    1. Generates a unique onboarding code 
    1. Adds citizen to Local Motion (requires env `COMMUNITY_API`)
    1. Adds citizen to Mailchimp list (requires env `MAILCHIMP_API_KEY`)
1. After import, login to your Mailchimp account and find the test campaign
1. Simply click `Send` to test sending to **all** imported accounts 



## Docker
### Run it as an executable (not a service)
```
docker run --rm -v $(PWD)/samples:/imports -v $(PWD)/html_templates:/html_templates \
    -e COMMUNITY_API=http://localhost:8082/citizens \
    -e MAILCHIMP_API_KEY=<mailchimp-api-key> \
    -e MAILCHIMP_USER=<mailchimp-user> \
    -e MAILCHIMP_TEMPLATE_PATH=/html_templates/mail_template.html \
    -e MAILCHIMP_LOGO_PATH=/html_templates/logo.png \
    localmotion/citizen-importer \
    $(whoami)_docker
    /imports/3_citizens.csv
```

### Build Docker image from source
```
docker build -t localmotion/citizen-importer .
```


## Command line

### Install dependencies
To setup:
```
virtualenv -p python3 citizens
source citizens/bin/activate
pip install -r requirements.txt
```

### Configure
Then to subsequently add the following to a local `.env` file. Enable Mailchimp and Sentry
integrations by setting respective env variables.
```
COMMUNITY_API=http://localhost:8082/citizens

# Mailchimp.com account that can be used for testing
MAILCHIMP_API_KEY=
MAILCHIMP_USER=
MAILCHIMP_TEMPLATE_PATH=$PWD/html_templates/mail_template.html
MAILCHIMP_LOGO_PATH=$PWD/html_templates/logo.png

# Sentry.io configuration
SENTRY_DSN=
```

### Run it from command line
Make sure you switched to the correct `virtualenv`:
```
source citizens/bin/activate
```

And then simply run:
```
python start.py $(whoami)_automated $(pwd)/samples/3_citizens.csv 
```

### CSV import samples
Samples can be found at [Samples](./samples) in this repository.
 