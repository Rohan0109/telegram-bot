from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ServiceStatus:
    name: str
    healthy: bool
