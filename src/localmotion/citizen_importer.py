import os
import uuid
import logging
import csv

from raven import Client
from ..localmotion.domain.citizen import Citizen
from ..localmotion.domain.result import Result
from ..localmotion.handler.mailchimp_api import MailchimpApi
from ..localmotion.handler.community_api import CommunityApi


class CitizenImporter:
    def __init__(self, namespace: str, source: str) -> None:
        self.namespace = namespace
        self.source = source
        self.sentry = CitizenImporter.__configure_sentry()
        self.mailchimp = self.__configure_mailchimp()
        self.community = self.__configure_community_api()

    @staticmethod
    def noop_row_handler(subsystem_name):
        return lambda citizen: logging.info("{} is disabled and not handling {}".format(subsystem_name, citizen.email))

    @staticmethod
    def __configure_sentry():
        sentry_dsn = os.getenv('SENTRY_DSN')
        if sentry_dsn is None:
            logging.warning("You are NOT using Sentry")
            return None
        logging.info("Connecting to Sentry using DSN {}".format(sentry_dsn))
        return Client(sentry_dsn)

    def __configure_mailchimp(self):
        # Mailchimp related configuration
        mailchimp_api_key_ = os.getenv('MAILCHIMP_API_KEY')
        if mailchimp_api_key_ is None:
            logging.warning('You are NOT using Mailchimp')
            return None

        mailchimp_user_ = os.environ['MAILCHIMP_USER']
        mailchimp_namespace_ = self.namespace
        mailchimp_local_template_path_ = os.environ['MAILCHIMP_TEMPLATE_PATH']
        mailchimp_local_logo_path = os.environ['MAILCHIMP_LOGO_PATH']

        logging.info('Connecting to Mailchimp using {} and API key {}'.format(mailchimp_user_, mailchimp_api_key_))
        return MailchimpApi(
            mailchimp_api_key_,
            mailchimp_user_,
            mailchimp_namespace_,
            mailchimp_local_template_path_,
            mailchimp_local_logo_path)

    def __configure_community_api(self):
        target_endpoint = os.getenv('COMMUNITY_API')
        if target_endpoint is None:
            logging.warning("You are NOT using Local Motion community API")
            return None
        logging.info("Connecting to Local Motion community API using {}".format(target_endpoint))
        return CommunityApi(self.namespace, target_endpoint)

    def __report_exception(self, msg, *args, **kwargs):
        logging.error(msg, args, kwargs)
        if self.sentry is not None:
            self.sentry.captureException()

    def parse_citizens(self):
        row_callbacks = [
            self.noop_row_handler('Community API') if self.community is None else self.community.create_or_update,
            self.noop_row_handler('Mailchimp') if self.mailchimp is None else self.mailchimp.create_or_update,
        ]

        results = []
        with open(self.source, 'rt') as csv_file:
            reader = csv.DictReader(csv_file)

            for row in reader:
                try:
                    logging.info(row)

                    name_ = row['name']
                    email_ = row['email']
                    ip_ = row['ip']
                    onboarding_uuid = str(uuid.uuid4())[:8]

                    citizen = Citizen(name_, email_, ip_, onboarding_uuid)

                    for row_callback in row_callbacks:
                        result = row_callback(citizen) or \
                                 Result.general_failure(citizen, "Function didn't return a result")
                        results.append(result)
                        result.assign_line_number(reader.line_num)
                except BaseException as e:
                    self.__report_exception("Parsing CSV failed: {}".format(e))

        for result in results:
            if result.is_failure():
                failure_message = "Failed line #{}: {} {}".format(
                    result.line_number, result.message, result.exception)
                logging.error(failure_message)
            else:
                logging.info("Success line #{}: {}".format(result.line_number, result.message))

