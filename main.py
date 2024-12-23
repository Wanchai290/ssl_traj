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

    def benchmark_controller(self, t):
        if t < 3:
            return 10, 0, 0
        else:
            return 0, 0, 0
        
    def goto_pid(self, t, x, y):
        error_x = x - self.x
        error_y = y - self.y
        vel_x = 5.0 * error_x
        vel_y = 5.0 * error_y

        return vel_x, vel_y, 0.0

    def update(self, t, x, y, orientation):
        self.x = x
        self.y = y
        self.orientation = orientation

        return self.goto_pid(t, -5, 0)
        # return self.benchmark_controller(t)


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

            # Sleep until next_t
            # time.sleep(max(0, next_t - time.time()))
            # current_t = next_t
            # next_t = current_t + dt
            # elapsed = current_t - t0

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

    controller.run(6)

    import matplotlib.pyplot as plt

    data = np.array(controller.data)
    ts = data[:, 0]
    xs = data[:, 1]

    plt.plot(ts, xs, label="x")
    plt.grid()
    plt.xlabel("Time (s)")
    plt.legend()
    plt.show()

    from signal_analyzer import Signal

    s = Signal(ts, xs)
    ps, vs, as_ = s.smooth_all()

    # Computing derivative of xs using fd
    grad = np.diff(xs) / np.diff(ts)
    grad = np.append(grad, grad[-1])

    # Creating 3 subplots
    fig, axs = plt.subplots(3)
    fig.suptitle("Position, Velocity and Acceleration")

    axs[0].plot(ts, xs, label="x")
    axs[0].plot(ts, ps, label="fitted x")
    axs[0].legend()
    axs[0].grid()

    axs[1].plot(ts, vs, label="fitted v")
    axs[1].plot(ts, grad, label="fd")
    axs[1].legend()
    axs[1].grid()

    axs[2].plot(ts, as_, label="fitted a")
    axs[2].legend()
    axs[2].grid()

    plt.show()
