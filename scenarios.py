import random
import numpy as np

from body import Planet
from config import (
    G, COLORS, WIDTH, HEIGHT,
    ORBIT_VARIATION_MIN, ORBIT_VARIATION_MAX,
    PLANET_MASS_MIN, PLANET_MASS_MAX, ORBIT_MIN_DIST,
)


def orbital_velocity(anchor_mass, distance):
    return (G * anchor_mass / distance) ** 0.5


def create_solar_system():
    cx, cy = WIDTH / 2, HEIGHT / 2

    sol = Planet(cx, cy, vx=0, vy=0, mass=5000,
                 color=(1.0, 0.9, 0.2), pinned=True)

    r1 = 150
    v1 = orbital_velocity(sol.mass, r1)
    p1 = Planet(cx + r1, cy, vx=0, vy=+v1, mass=30, color=(0.3, 0.7, 1.0))

    r2 = 260
    v2 = orbital_velocity(sol.mass, r2)
    p2 = Planet(cx + r2, cy, vx=0, vy=+v2, mass=60, color=(1.0, 0.5, 0.2))

    return [sol, p1, p2]


def create_binary_stars():
    cx, cy = WIDTH / 2, HEIGHT / 2
    r = 120
    # Para duas massas iguais, cada estrela orbita o centro de massa a metade da separacao (r*2)
    v = orbital_velocity(5000, r * 2) * 0.7

    s1 = Planet(cx - r, cy, vx=0, vy=+v, mass=5000, color=(1.0, 0.9, 0.2))
    s2 = Planet(cx + r, cy, vx=0, vy=-v, mass=5000, color=(1.0, 0.6, 0.2))

    R = 350
    vp = orbital_velocity(10000, R) * 0.9
    p = Planet(cx + R, cy, vx=0, vy=+vp, mass=20, color=(0.4, 0.9, 0.9))

    return [s1, s2, p]


def create_moon_system():
    cx, cy = WIDTH / 2, HEIGHT / 2

    sol = Planet(cx, cy, vx=0, vy=0, mass=5000,
                 color=(1.0, 0.9, 0.2), pinned=True)

    r_planet = 220
    v_planet = orbital_velocity(sol.mass, r_planet)
    planet = Planet(cx + r_planet, cy, vx=0, vy=+v_planet,
                    mass=200, color=(0.4, 1.0, 0.5))

    r_moon = 30
    v_moon_local = orbital_velocity(planet.mass, r_moon)
    # A lua herda a velocidade do planeta e adiciona a sua orbital local
    moon = Planet(cx + r_planet + r_moon, cy,
                  vx=0, vy=+v_planet + v_moon_local,
                  mass=5, color=(0.8, 0.8, 0.8))

    return [sol, planet, moon]


def add_orbital_planet(bodies, mouse_x, mouse_y):
    if not bodies:
        return

    anchor = max(bodies, key=lambda b: b.mass)
    dx = mouse_x - anchor.pos[0]
    dy = mouse_y - anchor.pos[1]
    dist = max(np.linalg.norm([dx, dy]), ORBIT_MIN_DIST)

    v_orb = orbital_velocity(anchor.mass, dist)
    fator = random.uniform(ORBIT_VARIATION_MIN, ORBIT_VARIATION_MAX)

    # Rotacao de 90 graus de (dx,dy) normalizado para obter a tangente ao raio
    tx = -dy / dist
    ty = +dx / dist

    bodies.append(Planet(
        mouse_x, mouse_y,
        vx=tx * v_orb * fator,
        vy=ty * v_orb * fator,
        mass=random.uniform(PLANET_MASS_MIN, PLANET_MASS_MAX),
        color=random.choice(COLORS),
    ))
