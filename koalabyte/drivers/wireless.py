from .base import BaseDriver


class WirelessDriver(BaseDriver):
    name = "wireless"

    def self_test(self):
        wireless = self.config.wireless
        ok = wireless.wifi_chipset == "MediaTek MT7921K"
        return {"name": self.name, "status": "pass" if ok else "fail", "detail": wireless.wifi_chipset}
