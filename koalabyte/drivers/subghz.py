from .base import BaseDriver


class SubGhzDriver(BaseDriver):
    name = "subghz"

    def self_test(self):
        p = self.config.peripherals
        ok = p.cc1101_bus >= 0 and p.cc1101_cs >= 0
        return {"name": self.name, "status": "pass" if ok else "fail", "detail": f"bus {p.cc1101_bus}, cs {p.cc1101_cs}"}
