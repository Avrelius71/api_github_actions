from services.restful_booker.auth.client import AuthClient
from services.restful_booker.booking.client import BookingClient
from services.restful_booker.ping.client import PingClient


class RestfulBookerApi:
    def __init__(self, env_config):
        self.auth = AuthClient(env_config)
        self.booking = BookingClient(env_config)
        self.ping = PingClient(env_config)
