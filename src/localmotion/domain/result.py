from src.localmotion.domain.citizen import Citizen


class Result:
    def __init__(self, citizen: Citizen, message=None, exception=None) -> None:
        self.citizen = citizen
        self.message = message
        self.exception = exception
        self.line_number = 0

    @classmethod
    def success(cls, citizen: Citizen, message: str) -> 'Result':
        return cls(citizen=citizen, message=message, exception=None)

    @classmethod
    def failure(cls, citizen: Citizen, message: str, exception: BaseException) -> 'Result':
        return cls(citizen=citizen, message=message, exception=exception)

    @classmethod
    def general_failure(cls, citizen: Citizen, message: str) -> 'Result':
        return cls(citizen=citizen, message=message, exception=None)

    def assign_line_number(self, line_number: int):
        self.line_number = line_number

    def is_failure(self):
        return self.exception is not None
