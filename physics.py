import numpy as np

from config import G, MIN_DIST, MAX_SPEED


def compute_accelerations(bodies):
    n = len(bodies)
    accelerations = [np.zeros(2) for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            a = bodies[i]
            b = bodies[j]

            delta = b.pos - a.pos
            dist = max(np.linalg.norm(delta), MIN_DIST)
            direction = delta / dist

            force_magnitude = G * a.mass * b.mass / (dist ** 2)
            force = direction * force_magnitude

            accelerations[i] += force / a.mass
            accelerations[j] -= force / b.mass

    return accelerations


def step(bodies, dt):
    accelerations = compute_accelerations(bodies)

    for i, body in enumerate(bodies):
        if not body.pinned:
            body.vel += accelerations[i] * dt
            speed = np.linalg.norm(body.vel)
            if speed > MAX_SPEED:
                body.vel = body.vel / speed * MAX_SPEED
            body.pos += body.vel * dt
        body.update_trail()


def check_collisions(bodies):
    to_remove = set()

    for i in range(len(bodies)):
        if i in to_remove:
            continue

        for j in range(i + 1, len(bodies)):
            if j in to_remove:
                continue

            a = bodies[i]
            b = bodies[j]
            dist = np.linalg.norm(a.pos - b.pos)

            if dist < (a.radius() + b.radius()):
                if a.pinned:
                    to_remove.add(j)
                elif b.pinned:
                    to_remove.add(i)
                    break
                else:
                    total_mass = a.mass + b.mass
                    a.pos = (a.pos * a.mass + b.pos * b.mass) / total_mass
                    a.vel = (a.vel * a.mass + b.vel * b.mass) / total_mass
                    a.mass = total_mass
                    to_remove.add(j)

    return [body for i, body in enumerate(bodies) if i not in to_remove]


def update(bodies, dt):
    step(bodies, dt)
    return check_collisions(bodies)


def orbital_info(planet, anchor):
    dist = max(float(np.linalg.norm(planet.pos - anchor.pos)), MIN_DIST)
    speed = planet.speed
    v_esc = (2 * G * anchor.mass / dist) ** 0.5
    energy = 0.5 * speed ** 2 - G * anchor.mass / dist  # energia mecanica especifica: 1/2 v^2 - GM/r
    return {
        "dist": dist,
        "speed": speed,
        "v_esc": v_esc,
        "bound": speed < v_esc,
        "energy": energy,
    }
