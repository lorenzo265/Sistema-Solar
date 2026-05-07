from collections import deque
import numpy as np

from config import TRAIL_LENGTH, RADIUS_SCALE, RADIUS_MIN


class Planet:
    def __init__(self, x, y, vx, vy, mass, color, pinned=False):
        self.pos = np.array([x, y], dtype=float)
        self.vel = np.array([vx, vy], dtype=float)
        self.mass = float(mass)
        self.color = self._validate_color(color)
        self.pinned = pinned
        self.trail = deque(maxlen=TRAIL_LENGTH)

    @staticmethod
    def _validate_color(color):
        if len(color) != 3:
            raise ValueError(f"color deve ter 3 componentes (R,G,B), recebeu {color}")
        for c in color:
            if not 0.0 <= c <= 1.0:
                raise ValueError(f"componentes de cor devem estar em [0,1], recebeu {color}")
        return tuple(float(c) for c in color)

    def update_trail(self):
        self.trail.append(self.pos.copy())

    def radius(self):
        return max(RADIUS_MIN, int(self.mass ** RADIUS_SCALE))

    @property
    def speed(self):
        return float(np.linalg.norm(self.vel))

    def __repr__(self):
        return (f"Planet(pos={self.pos.round(1).tolist()}, "
                f"vel={self.vel.round(1).tolist()}, "
                f"mass={self.mass:.0f}, pinned={self.pinned})")
