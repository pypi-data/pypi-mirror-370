import requests
from typing import Any
from .exceptions import APIClientError, APIRequestError
from .endpoints import RulesEndpoint, CachersEndpoint, AttacksEndpoint


class APIClient:
    def __init__(self, api_key: str, base_url: str = "https://api.example.com"):
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        self.base_url = base_url.rstrip("/")

        self.rules = RulesEndpoint(self)
        self.cachers = CachersEndpoint(self)
        self.attacks = AttacksEndpoint(self)

    def request(self, method: str, endpoint: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        resp: requests.Response = requests.Response()  # typing
        try:
            resp = self.session.request(method, url, **kwargs)
            resp.raise_for_status()
            return resp.json()
        except requests.HTTPError as e:
            raise APIRequestError(
                f"The request to {url} failed with status code {resp.status_code}: {str(e)}"
            ) from e
        except requests.RequestException as e:
            raise APIClientError(
                f"An unexpected error occurred while making a request to {url}: {str(e)}"
            ) from e
