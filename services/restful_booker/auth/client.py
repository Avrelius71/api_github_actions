import requests

from services.base_api import BaseAPI
from services.restful_booker.auth.models.auth import RequestPostAuth, ResponsePostAuth
from utils.schema import validate_schema


class AuthClient(BaseAPI):
    def post_auth(
        self,
        data: dict,
        validate: bool = True,
    ) -> tuple[requests.Response, ResponsePostAuth | None]:
        if validate:
            validate_schema(
                RequestPostAuth,
                data,
                "Валидация тела запроса авторизации по схеме RequestPostAuth",
            )
        response = self.post("/auth", json=data)
        if not validate:
            return response, None
        return response, validate_schema(
            ResponsePostAuth,
            response.json(),
            "Валидация ответа авторизации по схеме ResponsePostAuth",
        )
