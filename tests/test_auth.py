import allure
import pytest
from faker import Faker

from services.restful_booker.auth.assertions import assert_auth_failed, assert_auth_successful
from services.restful_booker.auth.models.auth import RequestPostAuth

fake = Faker()


@allure.feature("Auth")
class TestAuth:

    @pytest.mark.smoke
    @pytest.mark.regression
    @allure.title("Проверка авторизации с валидными данными")
    def test_auth(self, api, env_config):
        auth_body = RequestPostAuth(
            username=env_config.booker_username,
            password=env_config.booker_password,
        )
        with allure.step("Получение токена"):
            response, validate_data = api.auth.post_auth(auth_body.model_dump())

        assert_auth_successful(response, validate_data)

    @pytest.mark.regression
    @allure.title("Проверка авторизации с неверными данными")
    def test_not_existent_user_auth(self, api, test_data):
        data = {"username": fake.user_name(), "password": fake.password()}
        with allure.step("Получение токена"):
            response, _ = api.auth.post_auth(data, validate=False)

        assert_auth_failed(response, test_data["auth"]["expected_error"])

    @pytest.mark.regression
    @allure.title("Проверка с невалидными данными авторизации")
    def test_negativ_data_auth(self, api, negative_auth_payload, test_data):
        with allure.step("Получение токена"):
            response, _ = api.auth.post_auth(negative_auth_payload, validate=False)

        assert_auth_failed(response, test_data["auth"]["expected_error"])
