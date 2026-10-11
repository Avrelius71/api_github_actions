import allure
from requests import Response

from utils.assertions import assert_status_code


@allure.step("Проверка успешной авторизации")
def assert_auth_successful(response: Response, validated) -> None:
    assert_status_code(response, 200)
    assert validated.token, "Ожидали непустой токен в ответе авторизации"


@allure.step("Проверка ошибки авторизации")
def assert_auth_failed(response: Response, expected_error: str) -> None:
    assert_status_code(response, 200)
    error = response.json().get("reason")
    assert error == expected_error, f"Ожидали текст ошибки '{expected_error}', а получили '{error}'"
