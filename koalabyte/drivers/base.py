"""Shared driver primitives."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class DriverResult:
    name: str
    status: str
    detail: str

    def as_dict(self) -> Dict[str, str]:
        return {"name": self.name, "status": self.status, "detail": self.detail}


class BaseDriver:
    name = "base"

    def __init__(self, config: Any) -> None:
        self.config = config

    def initialize(self) -> str:
        return f"{self.name}: initialized"

    def self_test(self) -> Dict[str, str]:
        return DriverResult(self.name, "pass", "configuration accepted").as_dict()
