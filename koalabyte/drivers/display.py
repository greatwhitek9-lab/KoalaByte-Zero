from .base import BaseDriver


class DisplayDriver(BaseDriver):
    name = "display"

    def self_test(self):
        display = self.config.display
        ok = display.width == 800 and display.height == 480 and display.interface == "HDMI"
        return {"name": self.name, "status": "pass" if ok else "fail", "detail": f"{display.width}x{display.height} {display.interface}"}
