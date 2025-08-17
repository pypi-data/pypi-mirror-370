from web.dto import CommonDto
from pydantic import Field


class ProcessingException(Exception):
    def __init__(self, message):
        self.message = message


class RestException(CommonDto):
    type: str
    message: str = Field(None)
    details: list[dict] = Field(None)
