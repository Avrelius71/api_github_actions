"""Pydantic-фабрики payload для тестов бронирования."""

from typing import Any, Mapping
from random import choice, randint

from faker import Faker
from pydantic import BaseModel, Field

from services.restful_booker.booking.models.booking import BookingDates

fake = Faker()


def booking_dates_from_booking_cfg(booking_cfg: Mapping[str, Any]) -> BookingDates:
    """Даты из test_data/*.json (единый источник с default_checkin / default_checkout)."""

    return BookingDates.model_validate(
        {
            "checkin": booking_cfg["default_checkin"],
            "checkout": booking_cfg["default_checkout"],
        },
    )


class MinimalBookingCreateRequest(BaseModel):
    """Обязательные поля создания брони (без additionalneeds в модели)."""

    firstname: str = Field(default_factory=lambda: fake.first_name())
    lastname: str = Field(default_factory=lambda: fake.last_name())
    totalprice: int = Field(default_factory=lambda: randint(0, 1000))
    depositpaid: bool = Field(default_factory=lambda: choice([True, False]))
    bookingdates: BookingDates


class CreateBookingRequest(MinimalBookingCreateRequest):
    """Полный набор полей с additionalneeds."""

    additionalneeds: str | None = Field(default_factory=lambda: fake.text(max_nb_chars=20))
