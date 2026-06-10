from .base import BaseDriver


class IrDriver(BaseDriver):
    name = "ir"

    def self_test(self):
        p = self.config.peripherals
        ok = p.ir_rx_gpio != p.ir_tx_gpio
        return {"name": self.name, "status": "pass" if ok else "fail", "detail": f"rx {p.ir_rx_gpio}, tx {p.ir_tx_gpio}"}
