import allure
import pytest
from faker import Faker

from services.restful_booker.booking.assertions import (
    assert_booking_created,
    assert_booking_firstname_equals,
    assert_booking_firstname_not_equals,
    assert_booking_has_firstname,
    assert_booking_in_list,
    assert_booking_list_not_empty,
    assert_booking_matches,
    assert_delete_booking_returns_201_restful_booker,
    assert_forbidden,
    assert_internal_server_error,
    assert_method_not_allowed,
    assert_not_found,
)
from services.restful_booker.booking.factories import (
    CreateBookingRequest,
    MinimalBookingCreateRequest,
    booking_dates_from_booking_cfg,
)

fake = Faker()


@allure.feature('Booking')
class TestBooking:

    @pytest.mark.smoke
    @pytest.mark.regression
    @allure.title('Проверка создания брони со всеми параметрами')
    def test_create_booking_all_params(self, api, set_token, cleanup, test_data):
        booking_cfg = test_data["booking"]
        new_booking = CreateBookingRequest(
            bookingdates=booking_dates_from_booking_cfg(booking_cfg),
        )
        payload = new_booking.model_dump(mode='json')
        with allure.step('Создание брони'):
            response, validated = api.booking.create(payload)
            cleanup.append(lambda: api.booking.remove(validated.bookingid, set_token))

        assert_booking_created(response, validated, payload)

    @pytest.mark.regression
    @allure.title('Проверка создания брони с обязательными параметрами')
    def test_create_booking_required_params(self, api, set_token, cleanup, test_data):
        booking_cfg = test_data["booking"]
        new_booking = MinimalBookingCreateRequest(
            bookingdates=booking_dates_from_booking_cfg(booking_cfg),
        )
        payload = new_booking.model_dump(mode='json')
        with allure.step('Создание брони'):
            response, validated = api.booking.create(payload)
            cleanup.append(lambda: api.booking.remove(validated.bookingid, set_token))

        assert_booking_created(response, validated, payload)

    @pytest.mark.regression
    @allure.title('Проверка создания брони с невалидными данными')
    def test_negative_create_booking(self, api, negative_create_payload):
        # Сейчас API отвечает 500; при появлении корректной 4xx-валидации заменить ассерт и payload-кейсы.
        with allure.step('Cоздание брони'):
            response, _ = api.booking.create(negative_create_payload, validate=False)
        assert_internal_server_error(response)

    @pytest.mark.smoke
    @pytest.mark.regression
    @allure.title('Проверка получения брони по id')
    def test_get_book(self, api, create_booking_and_filters, cleanup, set_token):
        booking_id = create_booking_and_filters['bookingid']
        request_data = create_booking_and_filters['request_data']
        cleanup.append(lambda: api.booking.remove(booking_id, set_token))
        with allure.step('Получение брони по ID'):
            response, validate_data = api.booking.get_by_id(booking_id)
        assert_booking_matches(response, validate_data, request_data)

    @pytest.mark.regression
    @allure.title('Проверка получения брони с несуществующим id')
    def test_negative_get_book(self, api, test_data):
        with allure.step('Получение брони по ID'):
            response, _ = api.booking.get_by_id(test_data['booking']['non_existent_id'], validate=False)
        assert_not_found(response)

    @pytest.mark.regression
    @allure.title('Проверка получения всех бронирований')
    def test_get_all_booking_ids(self, api):
        with allure.step('Получение списка бронирования'):
            response, validate_data = api.booking.list()
        assert_booking_list_not_empty(response, validate_data)

    @pytest.mark.regression
    @allure.title('Проверка получения бронирований по фильтру')
    @pytest.mark.parametrize('key', ['lastname', 'firstname'])
    def test_get_booking_ids(self, api, create_booking_and_filters, key, cleanup, set_token):
        booking_id = create_booking_and_filters['bookingid']
        cleanup.append(lambda: api.booking.remove(booking_id, set_token))
        with allure.step(f'Получение списка бронирования по {key}'):
            filter_value = create_booking_and_filters[key]
            response, validate_data = api.booking.list(filter_key=key, filter_value=filter_value)
        assert_booking_in_list(response, validate_data, booking_id)

    @pytest.mark.smoke
    @pytest.mark.regression
    @allure.title('Проверка полного обновления брони авторизованным пользователем')
    def test_put_update_authoriz(self, api, create_booking_and_filters, set_token, cleanup, test_data):
        booking_id = create_booking_and_filters['bookingid']
        cleanup.append(lambda: api.booking.remove(booking_id, set_token))
        put_payload = CreateBookingRequest(
            bookingdates=booking_dates_from_booking_cfg(test_data["booking"]),
        ).model_dump(mode='json')

        with allure.step('редактирование брони'):
            response, validate_data = api.booking.update_put(
                booking_id=booking_id,
                token=set_token,
                data=put_payload,
            )
        assert_booking_matches(response, validate_data, put_payload)

        with allure.step('Получение данных по id брони'):
            response2, _ = api.booking.get_by_id(booking_id, validate=False)

        assert_booking_firstname_equals(response2, put_payload['firstname'])

    @pytest.mark.regression
    @allure.title('Проверка обновления брони неавторизованным пользователем')
    def test_put_update_not_authoriz(self, api, create_booking_and_filters, cleanup, set_token, test_data):
        booking_id = create_booking_and_filters['bookingid']
        cleanup.append(lambda: api.booking.remove(booking_id, set_token))
        put_payload = CreateBookingRequest(
            bookingdates=booking_dates_from_booking_cfg(test_data["booking"]),
        ).model_dump(mode='json')

        with allure.step('редактирование брони'):
            response, _ = api.booking.update_put(booking_id, data=put_payload, validate=False)
        assert_forbidden(response)

        with allure.step('Получение данных по id брони'):
            response2, _ = api.booking.get_by_id(booking_id, validate=False)

        assert_booking_firstname_not_equals(response2, put_payload['firstname'])

    @pytest.mark.regression
    @allure.title('Проверка обновления брони с невалидным токеном')
    def test_put_update_invalid_token(self, api, create_booking_and_filters, cleanup, set_token, test_data):
        token = test_data['booking']['invalid_token']
        booking_id = create_booking_and_filters['bookingid']
        cleanup.append(lambda: api.booking.remove(booking_id, set_token))

        put_payload = CreateBookingRequest(
            bookingdates=booking_dates_from_booking_cfg(test_data["booking"]),
        ).model_dump(mode='json')

        with allure.step('редактирование брони'):
            response, _ = api.booking.update_put(
                booking_id=booking_id,
                token=token,
                data=put_payload,
                validate=False,
            )
        assert_forbidden(response)

        with allure.step('Получение данных по id брони'):
            response2, _ = api.booking.get_by_id(booking_id, validate=False)

        assert_booking_firstname_not_equals(response2, put_payload['firstname'])

    @pytest.mark.regression
    @allure.title('Проверка обновления несуществующей брони')
    def test_put_update_not_found_bok(self, api, set_token, test_data):
        booking_id = test_data['booking']['non_existent_id']

        with allure.step('редактирование брони'):
            response, _ = api.booking.update_put(booking_id=booking_id, token=set_token, validate=False)
        assert_method_not_allowed(response)

    @pytest.mark.regression
    @allure.title('Проверка частичного обновления брони авторизованным пользователем')
    def test_patch_update_authoriz(self, api, create_booking_and_filters, set_token, cleanup):
        booking_id = create_booking_and_filters['bookingid']
        cleanup.append(lambda: api.booking.remove(booking_id, set_token))
        patch_payload = {"firstname": fake.first_name(), "lastname": fake.last_name()}

        with allure.step('редактирование брони'):
            response, validate_data = api.booking.update_patch(
                booking_id=booking_id,
                token=set_token,
                data=patch_payload,
            )
        assert_booking_matches(response, validate_data, patch_payload)

        with allure.step('Получение данных по id брони'):
            response2, _ = api.booking.get_by_id(booking_id, validate=False)

        assert_booking_firstname_equals(response2, patch_payload['firstname'])

    @pytest.mark.regression
    @allure.title('Проверка частичного обновления брони неавторизованным пользователем')
    def test_patch_update_not_authoriz(self, api, create_booking_and_filters, cleanup, set_token):
        booking_id = create_booking_and_filters['bookingid']
        cleanup.append(lambda: api.booking.remove(booking_id, set_token))
        patch_payload = {"firstname": fake.first_name(), "lastname": fake.last_name()}

        with allure.step('редактирование брони'):
            response, _ = api.booking.update_patch(booking_id=booking_id, data=patch_payload, validate=False)
        assert_forbidden(response)

        with allure.step('Получение данных по id брони'):
            response2, _ = api.booking.get_by_id(booking_id, validate=False)

        assert_booking_firstname_not_equals(response2, patch_payload['firstname'])

    @pytest.mark.regression
    @allure.title('Проверка частичного обновления брони c невалидным токеном')
    def test_patch_update_invalid_token(self, api, create_booking_and_filters, cleanup, set_token, test_data):
        token = test_data['booking']['invalid_token']
        booking_id = create_booking_and_filters['bookingid']
        cleanup.append(lambda: api.booking.remove(booking_id, set_token))

        patch_payload = {"firstname": fake.first_name(), "lastname": fake.last_name()}

        with allure.step('редактирование брони'):
            response, _ = api.booking.update_patch(
                booking_id=booking_id,
                token=token,
                data=patch_payload,
                validate=False,
            )
        assert_forbidden(response)

        with allure.step('Получение данных по id брони'):
            response2, _ = api.booking.get_by_id(booking_id, validate=False)

        assert_booking_firstname_not_equals(response2, patch_payload['firstname'])

    @pytest.mark.regression
    @allure.title('Проверка частичного обновления несуществующей брони')
    def test_patch_update_not_found(self, api, set_token, test_data):
        booking_id = test_data['booking']['non_existent_id']
        with allure.step('редактирование брони'):
            response, _ = api.booking.update_patch(booking_id=booking_id, token=set_token, validate=False)
        assert_method_not_allowed(response)

    @pytest.mark.smoke
    @pytest.mark.regression
    @allure.title('Проверка удаления брони')
    def test_delete_booking(self, api, create_booking_and_filters, set_token):
        booking_id = create_booking_and_filters['bookingid']
        with allure.step('Удаление брони'):
            response, _ = api.booking.remove(booking_id, set_token)
        assert_delete_booking_returns_201_restful_booker(response)

        with allure.step('Получение данных по удаленной брони'):
            response2, _ = api.booking.get_by_id(booking_id, validate=False)

        assert_not_found(response2)

    @pytest.mark.regression
    @allure.title('Проверка удаления брони неавторизованным пользователем')
    def test_delete_booking_not_autoriz(self, api, create_booking_and_filters, cleanup, set_token):
        booking_id = create_booking_and_filters['bookingid']
        cleanup.append(lambda: api.booking.remove(booking_id, set_token))
        with allure.step('Удаление брони'):
            response, _ = api.booking.remove(booking_id)
        assert_forbidden(response)

        with allure.step('Проверка получения брони'):
            response2, _ = api.booking.get_by_id(booking_id, validate=False)

        assert_booking_has_firstname(response2)

    @pytest.mark.regression
    @allure.title('Проверка удаления брони c невалидным токеном')
    def test_delete_booking_invalid_token(self, api, create_booking_and_filters, cleanup, set_token, test_data):
        booking_id = create_booking_and_filters['bookingid']
        cleanup.append(lambda: api.booking.remove(booking_id, set_token))
        token = test_data['booking']['invalid_token']
        with allure.step('Удаление брони'):
            response, _ = api.booking.remove(booking_id, token)
        assert_forbidden(response)

        with allure.step('Проверка получения брони'):
            response2, _ = api.booking.get_by_id(booking_id, validate=False)

        assert_booking_has_firstname(response2)

    @pytest.mark.regression
    @allure.title('Проверка удаления несуществующей брони')
    def test_delete_booking_not_found(self, api, set_token, test_data):
        booking_id = test_data['booking']['non_existent_id']
        with allure.step('Удаление брони'):
            response, _ = api.booking.remove(booking_id, set_token)
        assert_method_not_allowed(response)
