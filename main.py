import time
import typing

import numpy as np
from .ssl_vision import SSLVision
from .grsim_client import GrSimClient
from .bang_bang import BangBang2D



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
        # BangBang control
        # bb = BangBang2D()
        # bb.generate(self.pos, [x, y], self.vel, 5, 4)
        # _, vel, __ = bb.get_pos_vel_acc(0.075)

        # P control
        target = np.array([x, y])
        vel = target - self.pos

        return [vel[0], vel[1], 0.0]

    def update(self, t, x, y, vel_x, vel_y, orientation):
        self.pos = np.array([x, y])
        self.vel = np.array([vel_x, vel_y])
        self.orientation = orientation

        return self.goto(t, 0, 0)


class Controller:
    ROBOTS_PER_TEAM = 6
    def __init__(self):
        self.vision = SSLVision()
        self.vision.start_thread()

        self.client = GrSimClient()
        self.data = []
        self.robots: {str: {int: Robot}} = {
            "blue": {i: Robot() for i in range(Controller.ROBOTS_PER_TEAM)},
            "yellow": {i: Robot() for i in range(Controller.ROBOTS_PER_TEAM)}
        }

    def run(self, duration=-1,
            velocity_orders: typing.Callable[[{str: {int: Robot}}], dict[str, dict[int, tuple[float, float]]]] = lambda _: {
                "blue": {0: [0, 0]},
                "yellow": {},
            }):
        """
        Start control of the robots in the simulator
        Optional parameters:
        - duration: unused for control, only for capturing data
        - velocity_orders: Function that takes a dictionary with all robots positions in the form
                           of the following dict
                           > {"blue": {id: [x y]}, "yellow": {id: [x y]}}
                           for each robot (up to Controller.ROBOTS_PER_TEAM).
                           Should return a dictionary of the same format, giving the velocity commands to
                           issue to the robot **in WORLD frame, not robot frame**.
                           To not send any commands to a team, leave an empty array.

                           Example : if the function outputs
                           > {"blue": {0: [2, 2]}, "yellow": {}}
                           or even
                           > {"blue": {0: [2, 2]}}
                           then only blue robot 0 will receive a command.
        """
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
            for team in ["blue", "yellow"]:
                for i in range(Controller.ROBOTS_PER_TEAM):
                    x, y, vel_x, vel_y, orientation = (
                        data[f"{team}/{i}"]["x"],
                        data[f"{team}/{i}"]["y"],
                        data[f"{team}/{i}"]["vel_x"],
                        data[f"{team}/{i}"]["vel_y"],
                        data[f"{team}/{i}"]["orientation"],
                    )
                    self.robots[team][i].update(elapsed, x, y, vel_x, vel_y, orientation)

            vel_commands = velocity_orders(self.robots)

            for team in vel_commands.keys():
                for i in vel_commands[team].keys():
                    robot = self.robots[team][i]
                    vel_x, vel_y, _ = robot.goto(0, *vel_commands[team][i])
                    vel_x, vel_y = robot.R_world_robot().T @ [vel_x, vel_y]
                    self.client.set_target(team, i, vel_x, vel_y, 0.)

            # if duration > 0:
            #     self.data.append((elapsed, x, y, orientation))


            self.client.send()


if __name__ == "__main__":
    controller = Controller()

    controller.run()

    # import matplotlib.pyplot as plt
    #
    # data = np.array(controller.data)
    # ts = data[:, 0]
    # xs = data[:, 1]
    #
    # plt.plot(ts, xs, label="x")
    # plt.grid()
    # plt.xlabel("Time (s)")
    # plt.legend()
    # plt.show()
