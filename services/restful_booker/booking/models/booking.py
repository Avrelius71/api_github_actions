from datetime import date

from pydantic import BaseModel, RootModel


class BookingDates(BaseModel):
    checkin: date
    checkout: date


class Booking(BaseModel):
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str | None = None


class RequestCreateBooking(BaseModel):
    firstname: str
    lastname: str
    totalprice: int
    depositpaid: bool
    bookingdates: BookingDates
    additionalneeds: str | None = None


class ResponseCreateBooking(BaseModel):
    bookingid: int
    booking: Booking


class BookingSummary(BaseModel):
    bookingid: int


class BookingIdsResponse(RootModel[list[BookingSummary]]):
    root: list[BookingSummary]


class PatchRequest(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    totalprice: int | None = None
    depositpaid: bool | None = None
    bookingdates: BookingDates | None = None
    additionalneeds: str | None = None
