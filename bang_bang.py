import numpy as np


class BangBang1D:
    def __init__(self):
        self.parts = []

    def vel_change_to_zero(self, s0, v0, a_max):
        a = a_max if 0 >= v0 else -a_max
        t = -v0 / a
        return s0 + 0.5 * v0 * t

    def get_duration(self):
        return self.parts[-1][-1]

    def get_pos_vel_acc(self, t):
        t = np.clip(t, 0, self.get_duration())
        t_start = 0

        for part in self.parts:
            if t <= part[-1]:
                t -= t_start
                return (
                    part[0] + part[1] * t + 0.5 * part[2] * t * t,
                    part[1] + part[2] * t,
                    part[2],
                )
            t_start = part[-1]

    def vel_tri_to_zero(self, s0, v0, v1, a_max):
        if v1 >= v0:
            a1 = a_max
            a2 = -a_max
        else:
            a1 = -a_max
            a2 = a_max

        t1 = (v1 - v0) / a1
        s1 = s0 + (0.5 * (v0 + v1) * t1)

        t2 = -v1 / a2
        return s1 + 0.5 * v1 * t2

    def calc_triangular(self, s0, v0, s2, a):
        if a > 0:
            sq = ((a * (s2 - s0)) + (0.5 * v0 * v0)) / (a * a)
        else:
            sq = ((-a * (s0 - s2)) + (0.5 * v0 * v0)) / (a * a)

        if sq > 0:
            t2 = np.sqrt(sq)
        else:
            t2 = 0

        v1 = a * t2
        t1 = (v1 - v0) / a
        s1 = s0 + ((v0 + v1) * 0.5 * t1)

        self.parts = [[s0, v0, a, t1], [s1, v1, -a, t1 + t2]]

    def calc_trapezoidal(self, s0, v0, v1, s3, aMax):
        a1 = -aMax if v0 > v1 else aMax
        a3 = -aMax if v1 > 0 else aMax

        t1 = (v1 - v0) / a1
        v2 = v1
        t3 = -v2 / a3

        s1 = s0 + (0.5 * (v0 + v1) * t1)
        s2 = s3 - (0.5 * v2 * t3)
        t2 = (s2 - s1) / v1

        self.parts = [
            [s0, v0, a1, t1],
            [s1, v1, 0, t1 + t2],
            [s2, v2, a3, t1 + t2 + t3],
        ]

    def generate(self, x0, xd0, x_target, xdMax, xddMax):
        s_max_brake = self.vel_change_to_zero(x0, xd0, xddMax)

        if s_max_brake < x_target:
            s_end = self.vel_tri_to_zero(x0, xd0, xdMax, xddMax)
            if s_end >= x_target:
                self.calc_triangular(x0, xd0, x_target, xddMax)
            else:
                self.calc_trapezoidal(x0, xd0, xdMax, x_target, xddMax)
        else:
            s_end = self.vel_tri_to_zero(x0, xd0, -xdMax, xddMax)
            if s_end <= x_target:
                self.calc_triangular(x0, xd0, x_target, -xddMax)
            else:
                self.calc_trapezoidal(x0, xd0, -xdMax, x_target, xddMax)


class BangBang2D:
    def __init__(self):
        self.x = BangBang1D()
        self.y = BangBang1D()

    def generate(self, s0, s1, v0, vmax, acc, accuracy=1e-2):
        inc = np.pi / 8
        alpha = np.pi / 4

        while inc >= 1e-7:
            c = np.cos(alpha)
            s = np.sin(alpha)

            # print((s0[0], v0[0], s1[0], c * vmax, c * acc))
            self.x.generate(s0[0], v0[0], s1[0], c * vmax, c * acc)
            self.y.generate(s0[1], v0[1], s1[1], s * vmax, s * acc)

            diff = abs(self.x.get_duration() - self.y.get_duration())
            if diff < accuracy:
                break
            else:
                if self.x.get_duration() < self.y.get_duration():
                    alpha += inc
                else:
                    alpha -= inc
                inc /= 2

    def get_duration(self):
        return max(self.x.get_duration(), self.y.get_duration())

    def get_pos_vel_acc(self, t):
        return np.array([self.x.get_pos_vel_acc(t), self.y.get_pos_vel_acc(t)]).T


if __name__ == "__main__":
    bb = BangBang2D()
    bb.generate([0.0, 0.0], [3.0, 3.0], [3.0, 0.0], 2.0, 3.0)

    ts = np.linspace(0, bb.get_duration(), 100)
    xs = [bb.get_pos_vel_acc(t)[0][0] for t in ts]
    ys = [bb.get_pos_vel_acc(t)[0][1] for t in ts]
    
    import matplotlib.pyplot as plt
    
    # plt.plot(ts, xs)
    plt.plot(xs, ys)
    plt.axis("equal")
    plt.grid()
    plt.show()

    bb = BangBang1D()
    bb.generate(0.0, 3.0, 3.0, 0.9999997837782594, 1.499999675667389)

    ts = np.linspace(0, bb.get_duration(), 100)

    import matplotlib.pyplot as plt

    fig, axs = plt.subplots(3)
    fig.suptitle("Position, Velocity and Acceleration")

    axs[0].plot(ts, [bb.get_pos_vel_acc(t)[0] for t in ts], label="x")
    axs[0].legend()
    axs[0].grid()

    axs[1].plot(ts, [bb.get_pos_vel_acc(t)[1] for t in ts], label="dx")
    axs[1].legend()
    axs[1].grid()

    axs[2].plot(ts, [bb.get_pos_vel_acc(t)[2] for t in ts], label="ddx")
    axs[2].legend()
    axs[2].grid()

    plt.show()
