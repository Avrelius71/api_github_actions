import requests

from services.base_api import BaseAPI
from services.restful_booker.auth.models.auth import RequestPostAuth, ResponsePostAuth


class AuthClient(BaseAPI):
    def post_auth(
        self,
        data: dict,
        validate: bool = True,
    ) -> tuple[requests.Response, ResponsePostAuth | None]:
        if validate:
            RequestPostAuth.model_validate(data)
        response = self.post("/auth", json=data)
        if not validate:
            return response, None
        return response, ResponsePostAuth.model_validate(response.json())
