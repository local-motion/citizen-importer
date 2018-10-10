class Citizen:
    def __init__(self, name: str, email: str, ip: str, onboarding_uuid: str) -> None:
        self.name = name
        self.email = email
        self.ip = ip
        self.onboarding_uuid = onboarding_uuid
