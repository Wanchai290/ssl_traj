import time
import numpy as np
from ssl_vision import SSLVision
from grsim_client import GrSimClient
from bang_bang import BangBang2D


class Robot:
    def __init__(self):
        self.pos = np.array([0.0, 0.0])
        self.vel = np.array([0.0, 0.0])
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
        _, vel, __ = bb.get_pos_vel_acc(0.075)

        return [vel[0], vel[1], 0.0]

    def update(self, t, x, y, vel_x, vel_y, orientation):
        self.pos = np.array([x, y])
        self.vel = np.array([vel_x, vel_y])
        self.orientation = orientation

        return self.goto(t, 0, 0)


class Controller:
    def __init__(self):
        self.vision = SSLVision()
        self.vision.start_thread()

        self.client = GrSimClient()
        self.data = []

    def run(self, duration=-1):
        t0 = time.time()
        next_t = current_t = t0
        dt = 0.010
        elapsed = 0
        blue0 = Robot()

        while duration < 0 or elapsed < duration:
            # Sleepint until next_t
            time.sleep(max(0, next_t - time.time()))
            current_t = next_t
            next_t = current_t + dt
            elapsed = current_t - t0

            data = self.vision.get_data()

            x, y, vel_x, vel_y, orientation = (
                data["blue/0"]["x"],
                data["blue/0"]["y"],
                data["blue/0"]["vel_x"],
                data["blue/0"]["vel_y"],
                data["blue/0"]["orientation"],
            )
            if duration > 0:
                self.data.append((elapsed, x, y, orientation))
            vel_x, vel_y, vel_rot = blue0.update(elapsed, x, y, vel_x, vel_y, orientation)
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
