import logging
import requests

from src.localmotion.domain.result import Result
from src.localmotion.domain.citizen import Citizen


class CommunityApi:

    def __init__(self, namespace: str, target_endpoint: str) -> None:
        self.namespace = namespace
        self.target_endpoint = target_endpoint

    def create_or_update(self, citizen: Citizen):
        email = citizen.email
        try:
            r = requests.post(self.target_endpoint, data=citizen)
            logging.info(r)
            Result.success(citizen, "Added citizen {} to Local Motion".format(email))
        except BaseException as e:
            failure_message = "Could not add citizen {} to Local Motion at {}".format(email, self.target_endpoint)
            return Result.failure(citizen, failure_message, e)

