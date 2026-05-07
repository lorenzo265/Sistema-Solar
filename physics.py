"""
physics.py - Calcula a gravidade entre os planetas e detecta colisoes.

Lei da Gravitacao Universal de Newton:
    F = G * m1 * m2 / r^2

Funcoes publicas:
  - compute_accelerations(bodies)        -> lista de aceleracoes
  - step(bodies, dt)                     -> integra movimento (sem colisao)
  - check_collisions(bodies)             -> detecta e funde colisoes
  - update(bodies, dt)                   -> step + check_collisions
  - orbital_info(planet, anchor)         -> telemetria orbital (Feature 2)
"""

import numpy as np

from config import G, MIN_DIST, MAX_SPEED


def compute_accelerations(bodies):
    """
    Calcula a aceleracao gravitacional sobre cada corpo.

    Retorna lista de vetores numpy [ax, ay] -- mesma ordem da lista de entrada.
    Funcao pura: nao modifica os corpos. Usada por step() e por
    draw_force_vectors() para visualizar a fisica acontecendo.
    """
    n = len(bodies)
    accelerations = [np.zeros(2) for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            a = bodies[i]
            b = bodies[j]

            delta = b.pos - a.pos
            dist = max(np.linalg.norm(delta), MIN_DIST)
            direction = delta / dist

            # F = G * mA * mB / r^2  -> 3a Lei de Newton: forca igual e oposta
            force_magnitude = G * a.mass * b.mass / (dist ** 2)
            force = direction * force_magnitude

            accelerations[i] += force / a.mass
            accelerations[j] -= force / b.mass

    return accelerations


def step(bodies, dt):
    """
    So a integracao numerica -- sem deteccao de colisao.
    Modifica posicao/velocidade dos corpos in-place.
    """
    accelerations = compute_accelerations(bodies)

    for i, body in enumerate(bodies):
        if not body.pinned:
            body.vel += accelerations[i] * dt
            # Clamp de velocidade -- evita que corpos disparem em ejecoes proximas
            speed = np.linalg.norm(body.vel)
            if speed > MAX_SPEED:
                body.vel = body.vel / speed * MAX_SPEED
            body.pos += body.vel * dt
        body.update_trail()


def check_collisions(bodies):
    """
    Detecta e funde corpos que colidem. Retorna nova lista.

    Regras:
      - Sol (pinned) absorve qualquer corpo que toca nele.
      - Dois corpos normais fundem-se conservando momento linear.
    """
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
    """Fisica completa do frame: step + colisao. Retorna lista atualizada."""
    step(bodies, dt)
    return check_collisions(bodies)


def orbital_info(planet, anchor):
    """
    Telemetria orbital de um planeta em relacao a um corpo ancora.

    Retorna dict com:
      - dist:    distancia atual ao ancora (px)
      - speed:   velocidade escalar do planeta (px/s)
      - v_esc:   velocidade de escape nessa distancia
      - bound:   True se a orbita e fechada (speed < v_escape)
      - energy:  energia mecanica especifica (negativa = orbita ligada)

    Demonstra as Leis de Kepler / conservacao de energia em tempo real.
    """
    dist = max(float(np.linalg.norm(planet.pos - anchor.pos)), MIN_DIST)
    speed = planet.speed
    v_esc = (2 * G * anchor.mass / dist) ** 0.5
    # Energia mecanica especifica: 1/2 v^2 - G*M/r
    energy = 0.5 * speed ** 2 - G * anchor.mass / dist
    return {
        "dist": dist,
        "speed": speed,
        "v_esc": v_esc,
        "bound": speed < v_esc,
        "energy": energy,
    }
