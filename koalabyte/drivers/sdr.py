from .base import BaseDriver


class SdrDriver(BaseDriver):
    name = "sdr"

    def self_test(self):
        p = self.config.peripherals
        ok = p.rtl_sdr_bus == "USB3"
        return {"name": self.name, "status": "pass" if ok else "fail", "detail": p.rtl_sdr_bus}
