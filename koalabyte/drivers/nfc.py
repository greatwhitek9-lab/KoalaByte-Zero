from .base import BaseDriver


class NfcDriver(BaseDriver):
    name = "nfc"

    def self_test(self):
        p = self.config.peripherals
        ok = p.pn532_i2c_bus == 1 and p.nfc_coil_location == "inside left ear"
        return {"name": self.name, "status": "pass" if ok else "fail", "detail": p.nfc_coil_location}
