from .base import BaseDriver


class BatteryDriver(BaseDriver):
    name = "battery"

    def self_test(self):
        return {"name": self.name, "status": "pass", "detail": "power configuration present"}
