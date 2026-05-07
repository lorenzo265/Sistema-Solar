import physics


class Mission:
    def __init__(self, description, check_fn):
        self.description = description
        self.check_fn = check_fn
        self.completed = False

    def update(self, bodies):
        if not self.completed and self.check_fn(bodies):
            self.completed = True

    def reset(self):
        self.completed = False


def _orbiting_bodies(bodies):
    return [b for b in bodies if not b.pinned]


def _anchor(bodies):
    return max(bodies, key=lambda b: b.mass) if bodies else None


def _has_bound_orbit(bodies, min_dist=None, max_dist=None):
    a = _anchor(bodies)
    if a is None:
        return False
    for b in _orbiting_bodies(bodies):
        if b is a:
            continue
        info = physics.orbital_info(b, a)
        if not info["bound"]:
            continue
        if min_dist is not None and info["dist"] < min_dist:
            continue
        if max_dist is not None and info["dist"] > max_dist:
            continue
        return True
    return False


def _has_escape(bodies):
    a = _anchor(bodies)
    if a is None:
        return False
    for b in _orbiting_bodies(bodies):
        if b is a:
            continue
        if not physics.orbital_info(b, a)["bound"]:
            return True
    return False


MISSIONS = [
    Mission(
        "Coloque um planeta em orbita ligada a menos de 200px do sol",
        lambda bodies: _has_bound_orbit(bodies, max_dist=200),
    ),
    Mission(
        "Coloque um planeta em orbita ligada alem de 300px do sol",
        lambda bodies: _has_bound_orbit(bodies, min_dist=300),
    ),
    Mission(
        "Faca um corpo escapar do sistema (atingir velocidade de escape)",
        lambda bodies: _has_escape(bodies),
    ),
    Mission(
        "Mantenha 5 corpos simultaneamente em orbita",
        lambda bodies: len(_orbiting_bodies(bodies)) >= 5,
    ),
]


def cycle(current_index):
    return (current_index + 1) % len(MISSIONS)


def get(index):
    template = MISSIONS[index]
    return Mission(template.description, template.check_fn)
