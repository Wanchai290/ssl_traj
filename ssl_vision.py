import time
import hashlib
from .multicast_client import MulticastClient
from threading import Thread, Lock
from .com.ssl_vision_wrapper_pb2 import SSL_WrapperPacket


class SSLVision:
    def __init__(self, address: str = "224.5.23.2", port: int = 10020):
        self.client = MulticastClient(address, port)
        self.packet = SSL_WrapperPacket()
        self.new_data = False
        self._data = {}
        self.lock = Lock()

    def get_data(self) -> dict:
        with self.lock:
            return self._data.copy()

    def start_thread(self):
        self.thread = Thread(target=self.run)
        self.thread.start()

        # Waiting for the first frame
        while len(self._data) == 0:
            time.sleep(10e-3)

    def run(self):
        while True:
            self.update()

    def wait_for_data(self):
        while not self.new_data:
            time.sleep(1e-3)
        self.new_data = False

    def update(self):
        data = self.client.receive()
        self.packet.ParseFromString(data)

        with self.lock:
            self.new_data = True
            t_capture = self.packet.detection.t_capture
            for color, entries in [
                ("blue", self.packet.detection.robots_blue),
                ("yellow", self.packet.detection.robots_yellow),
            ]:
                for entry in entries:
                    key = f"{color}/{entry.robot_id}"
                    entry = {
                        "t": t_capture,
                        "color": color,
                        "id": entry.robot_id,
                        "x": entry.x / 1000,
                        "y": entry.y / 1000,
                        "vel_x": 0.0,
                        "vel_y": 0.0,
                        "orientation": entry.orientation,
                    }
                    if key in self._data:
                        if self._data[key]["t"] < t_capture:
                            dt = t_capture - self._data[key]["t"]
                            entry["vel_x"] = (entry["x"] - self._data[key]["x"]) / dt
                            entry["vel_y"] = (entry["y"] - self._data[key]["y"]) / dt
                        else:
                            entry["vel_x"] = self._data[key]["vel_x"]
                            entry["vel_y"] = self._data[key]["vel_y"]

                    self._data[key] = entry


if __name__ == "__main__":
    vision = SSLVision()
    vision.start_thread()

    while True:
        data = vision.get_data()
        print(data["blue/0"])
