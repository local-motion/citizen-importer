import logging
import os
import sys
import http.client as http_client

from src.localmotion.citizen_importer import CitizenImporter
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(verbose=True, override=True)
debug_mode = os.getenv('DEBUG')

# Initialize logging
logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG if debug_mode else logging.INFO)

if len(sys.argv) != 3:
    logging.info("Usage: python {} $(whoami) $(pwd)/samples/3_citizens.csv".format(Path(__file__).name))
    logging.info("""Environment variables to consider:
    
    COMMUNITY_API=http://localhost:8082/citizens
    SENTRY_DSN=<sentry-dsn>
    MAILCHIMP_USER=<mailchimp-user>
    MAILCHIMP_API_KEY=<mailchimp-api-key>
    MAILCHIMP_TEMPLATE_PATH=/html_templates/mail_template.html
    MAILCHIMP_LOGO_PATH=/html_templates/logo.png
    DEBUG=true
    """)
    sys.exit(1)


def configure_http_logging():
    http_client.HTTPConnection.debuglevel = 1

    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG if debug_mode else logging.INFO)
    requests_log.propagate = True


namespace = sys.argv[1]
source = sys.argv[2]

logging.info("Namespacing everything in: {}".format(namespace))
logging.info("CSV source file: {}".format(source))

if __name__ == '__main__':
    citizen_importer = CitizenImporter(namespace, source)
    citizen_importer.parse_citizens()

