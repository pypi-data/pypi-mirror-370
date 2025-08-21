from typing import TYPE_CHECKING
from .models import (
    RuleTypesResponse,
    RuleResponse,
    Rule,
    AddRuleResponse,
    DeleteRuleResponse,
    Cacher,
    CachersResponse,
    AddCacherResponse,
    DeleteCacherResponse,
    AttackResponse,
)

if TYPE_CHECKING:
    from .client import APIClient


class AttacksEndpoint:
    def __init__(self, client: "APIClient"):
        self._client = client

    def get(self, ip: str) -> AttackResponse:
        """
        Fetches the available attack types from the API.

        Returns:
            A dictionary containing attack types and their details.
        """
        data = self._client.request(
            "GET", "/api/attacks/get_attacks", params={"ip": ip}
        )

        return AttackResponse.model_validate(data)


class CachersEndpoint:
    def __init__(self, client: "APIClient"):
        self._client = client

    def get(self, ip: str) -> CachersResponse:
        """
        Fetches all cachers from the API.

        Returns:
            A dictionary containing all cachers and their details.
        """
        data = self._client.request(
            "GET", "/api/cachers/get_cachers", params={"ip": ip}
        )

        return CachersResponse.model_validate(data)

    def add(self, cacher: Cacher) -> AddCacherResponse:
        """
        Adds a new cacher to the API.

        Args:
            cacher: A dictionary containing the cacher details.

        Returns:
            A dictionary containing the response message and the added cacher.
        """
        data = self._client.request(
            "POST", "/api/cachers/add_cacher", json=cacher.model_dump()
        )

        return AddCacherResponse.model_validate(data)

    def delete(self, cacher: Cacher) -> DeleteCacherResponse:
        """
        Deletes a cacher from the API.

        Args:
            cacher: A dictionary containing the cacher details to be deleted.

        Returns:
            A dictionary containing the response message and success status.
        """
        data = self._client.request(
            "DELETE", "/api/cachers/delete_cacher", json=cacher.model_dump()
        )

        return DeleteCacherResponse.model_validate(data)


class RulesEndpoint:
    def __init__(self, client: "APIClient"):
        self._client = client

    def get_types(self) -> RuleTypesResponse:
        """
        Fetches the available rule types from the API.

        Returns:
            A dictionary containing rule types and their details.
        """
        data = self._client.request("GET", "/api/rules/get_rule_types")

        return RuleTypesResponse.model_validate(data)

    def get(self, ip: str) -> RuleResponse:
        """
        Fetches all rules from the API.

        Returns:
            A dictionary containing all rules and their details.
        """
        data = self._client.request("GET", "/api/rules/get_rules", params={"ip": ip})

        return RuleResponse.model_validate(data)

    def add(self, rule: Rule) -> AddRuleResponse:
        """
        Adds a new rule to the API.

        Args:
            rule: A dictionary containing the rule details.

        Returns:
            A dictionary containing the response message and the added rule.
        """
        data = self._client.request(
            "POST", "/api/rules/add_rule", json=rule.model_dump()
        )

        return AddRuleResponse.model_validate(data)

    def delete(self, rule: Rule) -> DeleteRuleResponse:
        """
        Deletes a rule from the API.

        Args:
            rule: A dictionary containing the rule details to be deleted.

        Returns:
            A dictionary containing the response message and success status.
        """
        data = self._client.request(
            "DELETE", "/api/rules/delete_rule", json=rule.model_dump()
        )

        return DeleteRuleResponse.model_validate(data)
