import random
from typing import Optional, Tuple

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

fake = Faker()


class BookingClient(BaseAPI):

    def create(
        self,
        data: Optional[dict] = None,
        *,
        validate: bool = True,
    ) -> Tuple[requests.Response, Optional[ResponseCreateBooking]]:
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
            RequestCreateBooking.model_validate(data)
        response = self.post("/booking", json=data)
        if not validate:
            return response, None
        return response, ResponseCreateBooking.model_validate(response.json())

    def get_by_id(
        self,
        booking_id: int,
        *,
        validate: bool = True,
    ) -> Tuple[requests.Response, Optional[Booking]]:
        response = self.get(f"/booking/{booking_id}")
        if not validate:
            return response, None
        return response, Booking.model_validate(response.json())

    def list(  # noqa: A003
        self,
        filter_key: Optional[str] = None,
        filter_value: Optional[str] = None,
        *,
        validate: bool = True,
    ) -> Tuple[requests.Response, Optional[BookingIdsResponse]]:
        params = {}
        if filter_key is not None and filter_value is not None:
            params[filter_key] = filter_value
        response = self.get("/booking", params=params)
        if not validate:
            return response, None
        return response, BookingIdsResponse.model_validate(response.json())

    def update_put(
        self,
        booking_id: int,
        data: Optional[dict] = None,
        token: Optional[str] = None,
        *,
        validate: bool = True,
    ) -> Tuple[requests.Response, Optional[Booking]]:
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
            Booking.model_validate(data)
        response = self.put(f"/booking/{booking_id}", json=data, headers=headers)
        if not validate:
            return response, None
        return response, Booking.model_validate(response.json())

    def update_patch(
        self,
        booking_id: int,
        data: Optional[dict] = None,
        token: Optional[str] = None,
        *,
        validate: bool = True,
    ) -> Tuple[requests.Response, Optional[Booking]]:
        if data is None:
            data = {"firstname": fake.first_name(), "lastname": fake.last_name()}
        headers = {}
        if token:
            headers = {"Cookie": f"token={token}"}
        if validate:
            PatchRequest.model_validate(data)
        response = self.patch(f"/booking/{booking_id}", json=data, headers=headers)
        if not validate:
            return response, None
        return response, Booking.model_validate(response.json())

    def remove(
        self,
        booking_id: int,
        token: Optional[str] = None,
    ) -> Tuple[requests.Response, None]:
        headers = {}
        if token:
            headers = {"Cookie": f"token={token}"}
        response = self.delete(f"/booking/{booking_id}", headers=headers)
        return response, None
