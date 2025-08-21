'''httpx_service.py'''

from httpx import Response
import httpx


class HTTPXService:
    '''HTTPXService'''

    def __init__(self, timeout: float = 5.0):
        self._timeout = timeout

    def post(self, url: str, headers: dict, json: dict) -> Response:
        '''post'''
        return httpx.post(url=url, headers=headers, json=json, timeout=self._timeout)
