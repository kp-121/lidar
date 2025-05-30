import numpy as np


class LiDARMOG:
    def __init__(self, num_bins: int = 360, num_gaussians: int = 3,
                 learning_rate: float = 0.05, threshold: float = 1.5, var_min: float = 1e-4):
        self.num_bins = num_bins
        self.K = num_gaussians
        self.alpha = learning_rate
        self.threshold = threshold
        self.weights = np.zeros((num_bins, self.K))
        self.means = np.zeros((num_bins, self.K))
        self.vars = np.ones((num_bins, self.K))
        self.initialized = False
        self.last_binned = np.full(self.num_bins, np.nan)
        self.var_min = var_min

    def initialize(self, ranges: np.ndarray):
        for i in range(self.num_bins):
            r = ranges[i]
            if np.isnan(r): continue
            self.means[i, 0] = r
            self.weights[i, 0] = 1.0
        self.initialized = True

    def update(self, points: list):
        if not points:
            return []
        xs = np.array([x for x, y, _ in points])
        ys = np.array([y for x, y, _ in points])
        angles = np.degrees(np.arctan2(ys, xs)) % 360
        ranges = np.hypot(xs, ys)
        bins = angles.astype(int)
        binned = np.full(self.num_bins, np.nan)
        for b in range(self.num_bins):
            mask = bins == b
            if np.any(mask):
                binned[b] = ranges[mask].mean()
        self.last_binned = binned
        if not self.initialized:
            self.initialize(binned)
        fg_bins = []
        for i in range(self.num_bins):
            r = binned[i]
            if np.isnan(r):
                continue
            matched = False
            for k in range(self.K):
                sigma = np.sqrt(self.vars[i, k])
                if abs(r - self.means[i, k]) <= self.threshold * sigma:
                    matched = True
                    w = self.weights[i, k]
                    self.weights[i, k] = (1 - self.alpha) * w + self.alpha
                    rho = self.alpha / self.weights[i, k]
                    delta = r - self.means[i, k]
                    self.means[i, k] += rho * delta
                    self.vars[i,k] = max((1 - rho) * self.vars[i, k] + rho * delta * delta, self.var_min)
                else:
                    self.weights[i, k] *= (1 - self.alpha)
            if not matched:
                fg_bins.append(i)
                kmin = np.argmin(self.weights[i])
                self.means[i, kmin] = r
                self.vars[i, kmin] = 1.0
                self.weights[i, kmin] = self.alpha
            sw = self.weights[i].sum()
            if sw > 0:
                self.weights[i] /= sw
        return fg_bins
