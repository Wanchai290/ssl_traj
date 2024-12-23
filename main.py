import time
import numpy as np
from ssl_vision import SSLVision
from grsim_client import GrSimClient
from bang_bang import BangBang2D


class Robot:
    def __init__(self):
        self.pos = np.array([0.0, 0.0])
        self.vel = np.array([0.0, 0.0])
        self.last_t = None
        self.orientation = 0.0

    def R_world_robot(self):
        return np.array(
            [
                [np.cos(self.orientation), -np.sin(self.orientation)],
                [np.sin(self.orientation), np.cos(self.orientation)],
            ]
        )

    def goto(self, t, x, y):
        bb = BangBang2D()
        bb.generate(self.pos, [x, y], self.vel, 5, 4)
        _, vel, __ = bb.get_pos_vel_acc(0.05)

        return [vel[0], vel[1], 0.0]

    def update(self, t, x, y, orientation):
        new_pos = np.array([x, y])
        if self.last_t is not None and self.last_t < t:
            dt = t - self.last_t
            self.vel = (new_pos - self.pos) / dt
        self.pos = new_pos
        self.last_t = t
        self.orientation = orientation

        return self.goto(t, 0, 0)


class Controller:
    def __init__(self):
        self.vision = SSLVision()
        self.vision.start_thread()

        self.client = GrSimClient()
        self.data = []

    def run(self, duration=-1):
        t0 = self.vision.t_capture
        elapsed = 0
        blue0 = Robot()

        while duration < 0 or elapsed < duration:
            self.vision.wait_for_data()

            data = self.vision.get_data()
            elapsed = self.vision.t_capture - t0

            x, y, orientation = (
                data["blue/0"]["x"],
                data["blue/0"]["y"],
                data["blue/0"]["orientation"],
            )
            if duration > 0:
                self.data.append((elapsed, x, y, orientation))
            vel_x, vel_y, vel_rot = blue0.update(elapsed, x, y, orientation)
            vel_x, vel_y = blue0.R_world_robot().T @ [vel_x, vel_y]
            self.client.set_target("blue", 0, vel_x, vel_y, vel_rot)
            self.client.send()


if __name__ == "__main__":
    controller = Controller()

    controller.run()

    import matplotlib.pyplot as plt

    data = np.array(controller.data)
    ts = data[:, 0]
    xs = data[:, 1]

    plt.plot(ts, xs, label="x")
    plt.grid()
    plt.xlabel("Time (s)")
    plt.legend()
    plt.show()
