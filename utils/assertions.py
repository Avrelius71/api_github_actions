import allure
from requests import Response


@allure.step("Проверка статус-кода: ожидаем {expected}")
def assert_status_code(response: Response, expected: int) -> None:
    assert response.status_code == expected, f"Ожидали статус-код {expected}, а получили {response.status_code}"


@allure.step("Проверка текста ответа")
def assert_response_text(response: Response, expected_text: str) -> None:
    assert response.text == expected_text, f"Ожидали текст ответа '{expected_text}', а получили '{response.text}'"
