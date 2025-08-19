import json, uuid
from urllib import request, error
from .enums import Direction, SpeedLevel

class MoskitClient:
    def __init__(self, base_url: str, timeout: float = 5.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = float(timeout)
        self._headers = {
            "Content-Type": "application/json",
            "X-Client-Type": "python",
        }

    def _post(self, path: str, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        req = request.Request(self.base_url + path, data=data, headers=self._headers, method="POST")
        try:
            with request.urlopen(req, timeout=self.timeout) as resp:
                body = resp.read().decode("utf-8", "replace")
                if 200 <= resp.status < 300:
                    try:
                        return json.loads(body)
                    except Exception:
                        return body
                raise RuntimeError(f"{path} HTTP {resp.status}: {body}")
        except error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")
            raise RuntimeError(f"{path} HTTP {e.code}: {body}") from None
        except error.URLError as e:
            raise RuntimeError(f"{path} network error: {e}") from None

    @staticmethod
    def _val(x):

        return getattr(x, "value", x)

    def home(self, motor_id: int):
        return self._post("/api/home", {"motor_id": int(motor_id)})

    def drive_to_position(self, motor_id: int, position: int, speed_level: SpeedLevel):
        payload = {
            "motor_id": int(motor_id),
            "position": int(position),
            "speedLevel": self._val(speed_level),
        }
        return self._post("/api/driveToPosition", payload)

    def drive_velocity(self, motor_id: int, direction: Direction, speed_level: SpeedLevel, scale: float = 1.0):
        payload = {
            "motor_id": int(motor_id),
            "dir": self._val(direction),
            "speedLevel": self._val(speed_level),
            "speedScale": float(scale),
        }
        return self._post("/api/driveVelocity", payload)
