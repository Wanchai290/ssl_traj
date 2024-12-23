import numpy as np


class Signal:
    def __init__(self, ts, xs):
        self.ts = ts
        self.xs = xs

    def smooth(self, k: int, window_size: int = 32, order: int = 3):
        t = self.ts[k]

        ts_around = self.ts[max(k - window_size, 0) : min(k + window_size, len(self.ts))]
        xs_around = self.xs[max(k - window_size, 0) : min(k + window_size, len(self.ts))]

        p = np.polyfit(ts_around, xs_around, order)
        v = np.polyder(p)
        a = np.polyder(v)

        return np.polyval(p, t), np.polyval(v, t), np.polyval(a, t)
    
    def smooth_all(self):
        ps = []
        vs = []
        as_ = []

        for k in range(len(self.ts)):
            p, v, a = self.smooth(k)
            ps.append(p)
            vs.append(v)
            as_.append(a)

        return ps, vs, as_


if __name__ == "__main__":
    ts = np.linspace(0, 1, 1000)
    xs = np.sin(2 * np.pi * ts) + np.random.randn(1000) * 0.05

    s = Signal(ts, xs)

    ps, vs, as_ = s.smooth_all()

    import matplotlib.pyplot as plt

    plt.plot(ts, xs)
    plt.plot(ts, ps)
    plt.grid()
    plt.show()
