import time
import numpy as np
from ssl_vision import SSLVision
from grsim_client import GrSimClient


class Robot:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.orientation = 0.0

    def R_world_robot(self):
        return np.array(
            [
                [np.cos(self.orientation), -np.sin(self.orientation)],
                [np.sin(self.orientation), np.cos(self.orientation)],
            ]
        )

    def update(self, x, y, orientation):
        self.x = x
        self.y = y
        self.orientation = orientation
        print(orientation)

        error_x = -5 - self.x
        error_y = 0.0 - self.y
        vel_x = 5.0 * error_x
        vel_y = 5.0 * error_y

        vel_x, vel_y = self.R_world_robot().T @ [vel_x, vel_y]
        return vel_x, vel_y, 0.0


class Controller:
    def __init__(self):
        self.vision = SSLVision()
        self.vision.start_thread()

        self.client = GrSimClient()

    def run(self):
        current_t = time.time()
        dt = 0.010
        next_t = current_t + dt
        blue0 = Robot()

        while True:
            # Sleep until next_t
            time.sleep(max(0, next_t - time.time()))
            current_t = next_t
            next_t = current_t + dt

            data = self.vision.get_data()

            x, y, orientation = (
                data["blue/0"]["x"],
                data["blue/0"]["y"],
                data["blue/0"]["orientation"],
            )
            vel_x, vel_y, vel_rot = blue0.update(x, y, orientation)
            self.client.set_target("blue", 0, vel_x, vel_y, vel_rot)
            self.client.send()


if __name__ == "__main__":
    controller = Controller()
    controller.run()
