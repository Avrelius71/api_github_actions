import json
import random
import warnings
from collections.abc import Callable, Generator
from pathlib import Path

import pytest
from faker import Faker

from config.environments import Environment, load_environment
from services.restful_booker.api import RestfulBookerApi
from test_data.loader import load_negative_auth_payloads, load_negative_create_booking_payloads

fake = Faker()


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default=Environment.DEV.value,
        choices=[Environment.DEV.value, Environment.STAGE.value],
        help="Target environment for API tests: dev or stage",
    )


def pytest_generate_tests(metafunc):
    env = metafunc.config.getoption("--env")
    names = metafunc.fixturenames
    if "negative_auth_payload" in names:
        metafunc.parametrize("negative_auth_payload", load_negative_auth_payloads(env))
    if "negative_create_payload" in names:
        metafunc.parametrize("negative_create_payload", load_negative_create_booking_payloads(env))


@pytest.fixture(scope="session")
def env(request) -> Environment:
    return Environment(request.config.getoption("--env"))


@pytest.fixture(scope="session")
def env_config(env):
    return load_environment(env)


@pytest.fixture(scope="session")
def test_data(env: Environment):
    data_path = Path(__file__).resolve().parent / "test_data" / f"{env.value}.json"
    with data_path.open("r", encoding="utf-8") as data_file:
        return json.load(data_file)


def pytest_report_header(config):
    env = config.getoption("--env")
    return f"Окружение: {env}"


@pytest.fixture
def cleanup() -> Generator[list[Callable[[], None]], None, None]:
    tasks = []
    yield tasks
    errors = []
    for task in reversed(tasks):
        try:
            task()
        except Exception as exc:
            errors.append(exc)
    if errors:
        warnings.warn(f"Cleanup errors: {errors}", stacklevel=2)


@pytest.fixture()
def api(env_config):
    return RestfulBookerApi(env_config)


@pytest.fixture()
def create_booking_and_filters(api, test_data):
    booking_cfg = test_data["booking"]
    data = {
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "totalprice": random.randint(0, 1000),
        "depositpaid": random.choice([True, False]),
        "bookingdates": {
            "checkin": booking_cfg["default_checkin"],
            "checkout": booking_cfg["default_checkout"],
        },
    }
    response, _ = api.booking.create(data, validate=False)
    booking_id = response.json()["bookingid"]
    yield {
        "bookingid": booking_id,
        "request_data": data,
        "firstname": response.json()["booking"]["firstname"],
        "lastname": response.json()["booking"]["lastname"],
        "checkin": response.json()["booking"]["bookingdates"]["checkin"],
        "checkout": response.json()["booking"]["bookingdates"]["checkout"],
    }


@pytest.fixture()
def set_token(api, env_config):
    data = {"username": env_config.booker_username, "password": env_config.booker_password}
    response, _ = api.auth.post_auth(data, validate=False)
    token = response.json()["token"]
    yield token
