from .base import BaseDriver


class CameraDriver(BaseDriver):
    name = "camera"

    def self_test(self):
        cam = self.config.camera
        ok = cam.model in {"IMX219", "IMX708"} and cam.interface.startswith("CSI")
        return {"name": self.name, "status": "pass" if ok else "fail", "detail": f"{cam.model} on {cam.interface} at {cam.location}"}
