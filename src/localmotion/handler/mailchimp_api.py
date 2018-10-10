import base64
import os
import hashlib
import logging

from mailchimp3 import MailChimp
from src.localmotion.domain.result import Result
from src.localmotion.domain.citizen import Citizen


class MailchimpApi:
    def __init__(self, api_key: str, user: str, unique_name: str, local_template_path_: str,
                 local_logo_path_: str) -> None:
        self.namespace = unique_name
        self.local_template_path = local_template_path_
        self.local_logo_path = local_logo_path_
        self.template_folder = self.namespace + '_templates'
        self.template_name = self.namespace + '_template'
        self.template_folder_id = None
        self.template_id = None
        self.list_id = None
        self.list_name = self.namespace + '_list'
        self.logo_url = None
        self.logo_name = self.namespace + '_logo.png'
        self.campaign_id = None
        self.client = MailChimp(mc_api=api_key, mc_user=user, timeout=10.0)
        self.__init_from_mailchimp()

    def __init_from_mailchimp(self):
        self.__init_logo_url()
        self.__init_template_folder_id()
        self.__init_template_id()
        self.__init_list_id()
        self.__init_campaign_id()

    def __init_logo_url(self):
        if self.logo_url is not None:
            return

        files = self.client.files.all(get_all=True)
        for file in files.get('files'):
            if file.get('name') == self.logo_name:
                logo_id = file.get('id')
                logo_url = file.get('full_size_url')
                # logo_url = file.get('thumbnail_url')
                logging.info('Reusing existing logo {} {}'.format(logo_id, logo_url))
                self.logo_url = logo_url
                return

        with open(self.local_logo_path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read())
            create_logo_response = self.client.files.create(data={
                'name': self.logo_name,
                'file_data': encoded_string.decode('ascii')
            })
            self.logo_url = create_logo_response['full_size_url']

    def __init_template_folder_id(self):
        if self.template_folder_id is not None:
            return

        template_folders = self.client.template_folders.all(get_all=False, fields="folders.id,folders.name")
        for folder in template_folders.get('folders'):
            if folder.get('name') == self.template_folder:
                folder_id = folder.get('id')
                logging.info('Reusing existing folder {} {}'.format(folder_id, self.template_folder))
                self.template_folder_id = folder_id
                return

        template_folder = self.client.template_folders.create(data={"name": self.template_folder})
        self.template_folder_id = template_folder['id']

    def __init_template_id(self):
        if self.template_id is not None:
            return

        templates = self.client.templates.all(get_all=False, fields="templates.id,templates.name")
        for template in templates.get('templates'):
            if template.get('name') == self.template_name:
                template_id = template.get('id')
                logging.info('Reusing existing template {} {}'.format(template_id, self.template_name))
                self.template_id = template_id
                return

        html = MailchimpApi.__read_file_contents(self.local_template_path)
        create_template_response = self.client.templates.create(data={
            "folder_id": self.template_folder_id,
            "name": self.template_name,
            "html": html
        })
        self.template_id = create_template_response['id']

        logging.info('Created new template {} with name {} in folder {}'.format(
            self.template_id, self.template_name, self.template_folder))

    def __init_list_id(self):
        if self.list_id is not None:
            return

        lists = self.client.lists.all(get_all=False, fields="lists.id,lists.name")

        for list_ in lists.get('lists'):
            if list_.get('name') == self.list_name:
                list_id = list_.get('id')
                logging.info('Reusing existing list {} {}'.format(list_id, self.list_name))
                self.list_id = list_id
                return

        create_list_response = self.client.lists.create(data={
            "name": self.list_name,
            "contact": {
                "company": self.namespace + " B.V.",
                "address1": self.namespace + " lane 123",
                "city": "Amsterdam",
                "state": "NH",
                "zip": "1000AA",
                "country": "Netherlands"
            },
            "permission_reminder": "Earlier this year, you've signed a petition supporting smoke-free "
                                   "playgrounds. This is our follow-up on that initiative!",
            "campaign_defaults": {
                "from_name": "Local Motion",
                "from_email": "no-reply@localmotion.community",
                "subject": "Please help us making playgrounds smoke-free!",
                "language": "EN"
            },
            "email_type_option": True
        })
        self.list_id = create_list_response['id']

        logging.info('Created new list {} with name {}'.format(self.list_id, self.list_name))

        self.client.lists.merge_fields.create(list_id=self.list_id, data={
            'tag': 'FULLNAME',
            'name': 'Fullname',
            'type': 'text',
            'required': True,
        })
        self.client.lists.merge_fields.create(list_id=self.list_id, data={
            'tag': 'ONBOARDING',
            'name': 'Onboarding URL',
            'type': 'text',
            'required': True,
        })
        self.client.lists.merge_fields.create(list_id=self.list_id, data={
            'tag': 'LOGO',
            'name': 'Public URL logo',
            'type': 'text',
            'required': True,
        })
        logging.info('Created new merge-tags [FULLNAME, ONBOARDING, LOGO] for list {}'.format(self.list_id))

    @staticmethod
    def __read_file_contents(path: str):
        with open(path, 'r') as handle:
            return handle.read()

    def __init_campaign_id(self):
        if self.campaign_id is not None:
            return

        campaigns = self.client.campaigns.all(get_all=False)
        for campaign in campaigns.get('campaigns'):
            if campaign.get('recipients').get('list_id') == self.list_id:
                campaign_id = campaign.get('id')
                logging.info('Reusing existing campaign {}'.format(campaign_id))
                self.campaign_id = campaign_id
                return

        create_campaign_response = self.client.campaigns.create(data={
            "recipients": {
                "list_id": self.list_id
            },
            "settings": {
                "subject_line": "It's time to take action!",
                "from_name": "Local Motion",
                "from_email": "no-reply@localmotion.community",
                "reply_to": "no-reply@localmotion.community",
                "title": "Please help us making playgrounds smoke-free!",
                "template_id": self.template_id
            },
            "type": "regular"
        })
        self.campaign_id = create_campaign_response['id']

        logging.info('Created new campaign {} for list {} using list {}'.format(self.campaign_id, self.list_id, self.list_name))

    def create_or_update(self, citizen: Citizen):
        def hash_email(member_email):
            member_email = member_email.lower().encode()
            m = hashlib.md5(member_email)
            return m.hexdigest()

        try:
            digest = hash_email(citizen.email)

            member = {
                "email_address": citizen.email,
                "status_if_new": "subscribed",
                # "full_name": citizen.name,
                'merge_fields': {
                    'FULLNAME': citizen.name,
                    'ONBOARDING': "http://localhost:10000/onboarding/{}".format(citizen.onboarding_uuid),
                    'LOGO': self.logo_url
                },
            }
            self.client.lists.members.create_or_update(self.list_id, digest, member)

            success_message = "Added citizen {} to Mailchimp".format(citizen.email)
            return Result.success(citizen, success_message)
        except BaseException as e:
            failure_message = "Could not add citizen {} to mailchimp list {}".format(citizen, self.list_id)
            return Result.failure(citizen, failure_message, e)


if __name__ == '__main__':
    mailchimp_user_ = os.environ['MAILCHIMP_USER']
    mailchimp_api_key_ = os.environ['MAILCHIMP_API_KEY']
    namespace = os.getenv('USER') + "_automated"
    local_template_path = os.environ['MAILCHIMP_TEMPLATE_PATH']
    local_logo_path = os.environ['MAILCHIMP_LOGO_PATH']
    mailchimp = MailchimpApi(mailchimp_api_key_, mailchimp_user_, namespace, local_template_path, local_logo_path)

    print(mailchimp.campaign_id)
