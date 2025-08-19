import logging


class AutomationException(Exception):
    def __init__(self, message="Automation problem detected"):
        super().__init__(message)
        logging.warning(message)


class LogoutException(AutomationException):
    def __init__(self, message="A logout event occured"):
        super().__init__(message)