import requests

from services.base_api import BaseAPI


class PingClient(BaseAPI):
    def ping(self) -> tuple[requests.Response, None]:
        response = self.get("/ping")
        return response, None
