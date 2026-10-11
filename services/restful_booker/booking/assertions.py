import allure
from requests import Response

from utils.assertions import assert_response_text, assert_status_code


@allure.step("Проверка успешного создания брони")
def assert_booking_created(response: Response, validated, expected_data: dict) -> None:
    assert_status_code(response, 200)
    assert validated.booking.firstname == expected_data["firstname"], (
        f"Ожидали firstname '{expected_data['firstname']}', а получили '{validated.booking.firstname}'"
    )
    assert validated.booking.totalprice == expected_data["totalprice"], (
        f"Ожидали totalprice {expected_data['totalprice']}, а получили {validated.booking.totalprice}"
    )


@allure.step("Проверка соответствия полей брони ожидаемым значениям")
def assert_booking_matches(response: Response, validated, expected_data: dict) -> None:
    assert_status_code(response, 200)
    assert validated.firstname == expected_data["firstname"], (
        f"Ожидали firstname '{expected_data['firstname']}', а получили '{validated.firstname}'"
    )
    assert validated.lastname == expected_data["lastname"], (
        f"Ожидали lastname '{expected_data['lastname']}', а получили '{validated.lastname}'"
    )


@allure.step("Проверка наличия брони в списке")
def assert_booking_in_list(response: Response, validated, booking_id: int) -> None:
    assert_status_code(response, 200)
    ids = [item.bookingid for item in validated.root]
    assert booking_id in ids, f"Ожидали id {booking_id} в списке бронирований, но его нет"


@allure.step("Проверка запрета доступа")
def assert_forbidden(response: Response) -> None:
    assert_status_code(response, 403)


@allure.step("Проверка, что сущность не найдена")
def assert_not_found(response: Response) -> None:
    assert_status_code(response, 404)
    assert_response_text(response, "Not Found")


@allure.step("Проверка, что список бронирований не пустой")
def assert_booking_list_not_empty(response: Response, validated) -> None:
    assert_status_code(response, 200)
    assert len(validated.root) > 0, "Ожидали непустой список бронирований"


@allure.step("Проверка значения firstname в ответе")
def assert_booking_firstname_equals(response: Response, expected_firstname: str) -> None:
    actual_firstname = response.json().get("firstname")
    assert actual_firstname == expected_firstname, (
        f"Ожидали firstname '{expected_firstname}', а получили '{actual_firstname}'"
    )


@allure.step("Проверка, что firstname не изменился")
def assert_booking_firstname_not_equals(response: Response, unexpected_firstname: str) -> None:
    actual_firstname = response.json().get("firstname")
    assert actual_firstname != unexpected_firstname, (
        f"Firstname не должен быть '{unexpected_firstname}', но получили именно его"
    )


@allure.step("Проверка, что поле firstname присутствует в ответе")
def assert_booking_has_firstname(response: Response) -> None:
    body = response.json()
    assert "firstname" in body, "Ожидали поле 'firstname' в ответе, но оно отсутствует"


@allure.step("Проверка ответа 500 Internal Server Error")
def assert_internal_server_error(response: Response) -> None:
    """Текущее поведение restful-booker на части невалидных тел — 500.

    По REST ожидались бы 4xx и тело ошибки; когда сервер поправят,
    замените этот ассерт на проверку ожидаемого 4xx и структуры ошибки.
    """
    assert_status_code(response, 500)
    assert_response_text(response, "Internal Server Error")


@allure.step("Проверка статус-кода 405 Method Not Allowed")
def assert_method_not_allowed(response: Response) -> None:
    assert_status_code(response, 405)


@allure.step("Проверка ответа restful-booker на DELETE брони (код 201)")
def assert_delete_booking_returns_201_restful_booker(response: Response) -> None:
    # restful-booker возвращает 201 Created на успешное удаление — не стандартные 200/204.
    assert_status_code(response, 201)
