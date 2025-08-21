from typing import List, Any
from pydantic import BaseModel, field_validator
from ipaddress import ip_network


## Rules
class RuleType(BaseModel):
    name: str
    description: str
    identifier: int
    allowed_protocols: list[str]


class RuleTypesResponse(BaseModel):
    rule_types: List[RuleType]
    message: str


class Rule(BaseModel):
    ip: str
    source_ip: str
    dst_port: int
    protocol: str
    action: str

    @field_validator("source_ip")
    def source_ip_must_be_valid(cls, v: str):
        if v in ["0", "0.0.0.0", "0.0.0.0/0"]:
            return "0.0.0.0/0"

        try:
            ip_network(v, strict=False)
        except Exception:
            raise ValueError(f"Invalid source_ip format: '{v}'")
        return v

    @field_validator("protocol")
    def protocol_must_be_valid(cls, v: str):
        allowed_protocols = ["TCP", "UDP", "ICMP"]
        if v not in allowed_protocols:
            raise ValueError(
                f"Invalid protocol: {v}. Must be one of {allowed_protocols}."
            )
        return v


class RuleResponse(BaseModel):
    rules: list[Rule]
    message: str


class AddRuleResponse(BaseModel):
    message: str
    rule: dict[str, Any]


class DeleteRuleResponse(BaseModel):
    message: str
    success: bool


## Cachers
class Cacher(BaseModel):
    ip: str
    dst_port: int
    type: str

    @field_validator("type")
    def type_must_be_valid(cls, v: str):
        allowed_types = ["A2S", "Bedrock"]
        if v not in allowed_types:
            raise ValueError(f"Invalid type: {v}. Must be one of {allowed_types}.")
        return v


class CachersResponse(BaseModel):
    message: str
    cachers: list[Cacher]


class AddCacherResponse(BaseModel):
    message: str
    success: bool


class DeleteCacherResponse(BaseModel):
    message: str = "Cacher deleted successfully."
    success: bool


## Attacks
class Attack(BaseModel):
    unix_start_time: int
    unix_end_time: int
    destination_ip: str
    max_packets_per_second: float
    max_bits_per_second: float


class AttackResponse(BaseModel):
    attacks: list[Attack]
    message: str = "Successfully retrieved all attacks."
    success: bool = True
