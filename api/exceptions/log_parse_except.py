from .base import APIException
from api.models.types.exception import APIErrorCode


class ParserError(APIException):
    pass


class PatternFileNotFound(ParserError):
    def __init__(self, payload: dict = {}):
        super().__init__(error=APIErrorCode.PATTERN_FILE_NOT_FOUND, payload=payload)


class InvalidPatternFormat(ParserError):
    def __init__(self, payload: dict = {}):
        super().__init__(error=APIErrorCode.INVALID_PATTERN_FORMAT, payload=payload)


class NoPatternMatchError(ParserError):
    def __init__(self, payload: dict = {}):
        super().__init__(error=APIErrorCode.NO_PATTERN_MATCH, payload={})


class InvalidRegexPattern(ParserError):
    def __init__(self, payload: dict = {}):
        super().__init__(
            error=APIErrorCode.INVALID_REGEX_PATTERN,
            payload=payload,
        )
