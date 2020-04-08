try:
    from pymethods import arrays as ent, pyplot as plt
except ImportError:
    from .. import arrays as ent
import numpy as np


class Disk(ent.Pointsurface):
    @classmethod
    def spiral(cls, r=1, n_pts=100):
        indices = np.arange(0, n_pts, dtype=np.float) + 0.5
        r = (np.sqrt(indices/n_pts)) * r
        theta = np.pi * (1 + 5**0.5) * I
        xy = np.array([r * np.cos(theta), r * np.sin(theta)])
        return cls(xy)


if __name__ == "__main__":
    disk = Disk.spiral(r=2)
    disk.plot3d()
    plt.show()
