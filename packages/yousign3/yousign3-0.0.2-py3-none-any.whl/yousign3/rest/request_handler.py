from requests import request as req
from enum import StrEnum
import json


class RequestHandler:
    __token: str
    debug: bool

    def __init__(self, token: str, debug: bool = False):
        if token is None and token is not str:
            raise Exception('Token is invalid')

        self.__token = f"Bearer {token}"
        self.debug = debug

    ACCEPTED_STATUS = {
        "GET": [200],
        "POST": [201],
        "PATCH": [200],
        "DELETE": [204]
    }

    class ContentType(StrEnum):
        NONE = ''
        JSON = 'application/json'
        FORM = 'multipart/form-data'

    def _req(
        self,
        method: str,
        url: str,
        content_type: ContentType = ContentType.NONE,
        ** kwargs
    ):
        kwargs['headers'] = {}

        # add our authroization
        kwargs['headers']['authorization'] = self.__token
        kwargs['headers']['accept'] = 'application/json'

        if content_type != RequestHandler.ContentType.NONE:
            kwargs['headers']['content-type'] = str(content_type)

        res = req(method, url, **kwargs)

        if self.debug:
            print("to: ", url)
            print(kwargs.get('json'))
            print(res.content)

        if res.status_code not in RequestHandler.ACCEPTED_STATUS[method]:
            content = json.loads(res.content)
            raise Exception(
                f'{res.status_code} Not the return awaited \n {content['detail']}'
            )

        content = res.content
        if method != "DELETE":
            content = json.loads(content)

        return content
