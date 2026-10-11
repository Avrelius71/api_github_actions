import allure
import pytest

from utils.assertions import assert_status_code


@allure.feature("Ping")
class TestPingRequest:
    @pytest.mark.smoke
    @allure.title("Проверка ping")
    def test_ping(self, api):
        with allure.step("Отправка пинг запроса"):
            response, _ = api.ping.ping()

        assert_status_code(response, 201)
