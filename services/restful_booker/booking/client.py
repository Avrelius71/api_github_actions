import random

import requests
from faker import Faker

from services.base_api import BaseAPI
from services.restful_booker.booking.models.booking import (
    Booking,
    BookingIdsResponse,
    PatchRequest,
    RequestCreateBooking,
    ResponseCreateBooking,
)
from utils.schema import validate_schema

fake = Faker()


class BookingClient(BaseAPI):

    def create(
        self,
        data: dict | None = None,
        *,
        validate: bool = True,
    ) -> tuple[requests.Response, ResponseCreateBooking | None]:
        if data is None:
            data = {
                "firstname": fake.first_name(),
                "lastname": fake.last_name(),
                "totalprice": random.randint(0, 1000),
                "depositpaid": random.choice([True, False]),
                "bookingdates": {"checkin": "2018-01-01", "checkout": "2019-01-01"},
                "additionalneeds": fake.text(max_nb_chars=20),
            }
        if validate:
            validate_schema(
                RequestCreateBooking,
                data,
                "Валидация тела запроса создания брони по схеме RequestCreateBooking",
            )
        response = self.post("/booking", json=data)
        if not validate:
            return response, None
        return response, validate_schema(
            ResponseCreateBooking,
            response.json(),
            "Валидация ответа создания брони по схеме ResponseCreateBooking",
        )

    def get_by_id(
        self,
        booking_id: int,
        *,
        validate: bool = True,
    ) -> tuple[requests.Response, Booking | None]:
        response = self.get(f"/booking/{booking_id}")
        if not validate:
            return response, None
        return response, validate_schema(
            Booking,
            response.json(),
            f"Валидация ответа получения брони #{booking_id} по схеме Booking",
        )

    def list(  # noqa: A003
        self,
        filter_key: str | None = None,
        filter_value: str | None = None,
        *,
        validate: bool = True,
    ) -> tuple[requests.Response, BookingIdsResponse | None]:
        params = {}
        if filter_key is not None and filter_value is not None:
            params[filter_key] = filter_value
        response = self.get("/booking", params=params)
        if not validate:
            return response, None
        return response, validate_schema(
            BookingIdsResponse,
            response.json(),
            "Валидация списка бронирований по схеме BookingIdsResponse",
        )

    def update_put(
        self,
        booking_id: int,
        data: dict | None = None,
        token: str | None = None,
        *,
        validate: bool = True,
    ) -> tuple[requests.Response, Booking | None]:
        if data is None:
            data = {
                "firstname": fake.first_name(),
                "lastname": fake.last_name(),
                "totalprice": random.randint(0, 1000),
                "depositpaid": random.choice([True, False]),
                "bookingdates": {"checkin": "2018-01-01", "checkout": "2019-01-01"},
            }
        headers = {}
        if token:
            headers = {"Cookie": f"token={token}"}
        if validate:
            validate_schema(
                Booking,
                data,
                "Валидация тела запроса полного обновления брони по схеме Booking",
            )
        response = self.put(f"/booking/{booking_id}", json=data, headers=headers)
        if not validate:
            return response, None
        return response, validate_schema(
            Booking,
            response.json(),
            f"Валидация ответа полного обновления брони #{booking_id} по схеме Booking",
        )

    def update_patch(
        self,
        booking_id: int,
        data: dict | None = None,
        token: str | None = None,
        *,
        validate: bool = True,
    ) -> tuple[requests.Response, Booking | None]:
        if data is None:
            data = {"firstname": fake.first_name(), "lastname": fake.last_name()}
        headers = {}
        if token:
            headers = {"Cookie": f"token={token}"}
        if validate:
            validate_schema(
                PatchRequest,
                data,
                "Валидация тела запроса частичного обновления брони по схеме PatchRequest",
            )
        response = self.patch(f"/booking/{booking_id}", json=data, headers=headers)
        if not validate:
            return response, None
        return response, validate_schema(
            Booking,
            response.json(),
            f"Валидация ответа частичного обновления брони #{booking_id} по схеме Booking",
        )

    def remove(
        self,
        booking_id: int,
        token: str | None = None,
    ) -> tuple[requests.Response, None]:
        headers = {}
        if token:
            headers = {"Cookie": f"token={token}"}
        response = self.delete(f"/booking/{booking_id}", headers=headers)
        return response, None
