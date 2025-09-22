from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class ApiRequest:
    method: str
    url: str
    request_headers: Dict[str, str]
    request_body: Any
    response_status: int
    response_headers: Dict[str, str]
    response_body: Any


@dataclass
class ProviderCall:
    method: str
    request_payload: Dict[str, Any]
    response_payload: Dict[str, Any]


Event = ProviderCall | ApiRequest


@dataclass
class ResourceOperation:
    address: str
    events: List[Event] = field(default_factory=list)


@dataclass
class ExecutionPhase:
    name: str
    operations: Dict = field(default_factory=dict)


@dataclass
class ExecutionTrace:
    phases: List[ExecutionPhase] = field(default_factory=list)
