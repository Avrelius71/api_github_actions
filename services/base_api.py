import json
import logging
import time
import uuid

import allure
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, RequestException, Timeout
from urllib3.util.retry import Retry

from services.exceptions import ApiConnectionError, ApiError, ApiTimeoutError

# Секунды: один лимит на connect и read (Heroku часто отвечает по 5–15+ с на 500/очереди).
# Раньше timeout=None — один зависший DELETE мог занимать минуты из‑за ретраев urllib3.
_DEFAULT_TIMEOUT = 120


class BaseAPI:
    def __init__(self, env_config):
        self.base_url = str(env_config.booker_url).rstrip("/")
        self.env_config = env_config
        self.session = self._build_session()
        self.logger = logging.getLogger("api")

    def _build_session(self) -> requests.Session:
        retry = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            raise_on_status=False,
        )
        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=20,
            pool_maxsize=20,
        )
        session = requests.Session()
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    @staticmethod
    def _safe_json(payload):
        if payload is None:
            return None
        try:
            return json.dumps(payload, ensure_ascii=False, indent=2)
        except (TypeError, ValueError):
            return str(payload)

    def _attach_request(self, request_id: str, method: str, url: str, kwargs):
        request_payload = {
            "request_id": request_id,
            "method": method.upper(),
            "url": url,
            "headers": kwargs.get("headers", {}),
            "params": kwargs.get("params"),
            "json": kwargs.get("json"),
            "data": kwargs.get("data"),
        }
        allure.attach(
            self._safe_json(request_payload) or "",
            name=f"REQUEST [{request_id}]",
            attachment_type=allure.attachment_type.JSON,
        )

    def _attach_response(self, request_id: str, response: requests.Response):
        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type.lower():
            try:
                body = self._safe_json(response.json()) or ""
                attachment_type = allure.attachment_type.JSON
            except ValueError:
                body = response.text
                attachment_type = allure.attachment_type.TEXT
        else:
            body = response.text
            attachment_type = allure.attachment_type.TEXT

        response_payload = (
            f"request_id: {request_id}\n"
            f"status_code: {response.status_code}\n"
            f"url: {response.url}\n"
            f"headers: {dict(response.headers)}\n"
            f"body:\n{body}"
        )
        allure.attach(
            response_payload,
            name=f"RESPONSE [{request_id}]",
            attachment_type=attachment_type,
        )

    def _request(self, method: str, path: str, **kwargs):
        request_id = uuid.uuid4().hex
        headers = dict(kwargs.pop("headers", {}) or {})
        headers["X-Request-Id"] = request_id
        kwargs["headers"] = headers
        kwargs.setdefault("timeout", _DEFAULT_TIMEOUT)
        url = f"{self.base_url}{path}"
        step_title = f"HTTP {method.upper()} {path}"
        with allure.step(step_title):
            self._attach_request(request_id=request_id, method=method, url=url, kwargs=kwargs)
            started_at = time.perf_counter()
            try:
                response = self.session.request(method=method.upper(), url=url, **kwargs)
            except Timeout as exc:
                raise ApiTimeoutError(f"Timeout for {method.upper()} {url}, request_id={request_id}") from exc
            except ConnectionError as exc:
                raise ApiConnectionError(
                    f"Connection error for {method.upper()} {url}, request_id={request_id}"
                ) from exc
            except RequestException as exc:
                raise ApiError(f"Request failed for {method.upper()} {url}, request_id={request_id}") from exc

            elapsed_ms = int((time.perf_counter() - started_at) * 1000)
            self.logger.info(
                "api_request method=%s url=%s status=%s request_id=%s elapsed_ms=%s",
                method.upper(),
                url,
                response.status_code,
                request_id,
                elapsed_ms,
            )
            self._attach_response(request_id=request_id, response=response)
            return response


    def get(self, path: str, **kwargs):
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs):
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs):
        return self._request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs):
        return self._request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs):
        return self._request("DELETE", path, **kwargs)
