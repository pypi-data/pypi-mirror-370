class RTCVisException(Exception):
    """Base class for all rtcvis exceptions."""


class ValidationException(RTCVisException):
    def __init__(self, msg: str):
        """Exception for failed input validation.

        Args:
            msg (str): Error message.
        """
        super().__init__(msg)
        self.msg = msg
