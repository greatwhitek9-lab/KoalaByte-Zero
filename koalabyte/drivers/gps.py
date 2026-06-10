from .base import BaseDriver


class GpsDriver(BaseDriver):
    name = "gps"

    def self_test(self):
        p = self.config.peripherals
        ok = p.gps_port.startswith("/dev/") and p.gps_baudrate > 0
        return {"name": self.name, "status": "pass" if ok else "fail", "detail": f"{p.gps_port} @ {p.gps_baudrate}"}
