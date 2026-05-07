"""
scenarios.py - Cenarios iniciais e fabrica de planetas.

Toda a logica de "quais planetas existem no inicio" e "como criar um
planeta orbital" vive aqui. main.py deixa de precisar de numpy ou de
constantes fisicas.

Cenarios disponiveis (Feature 3 - teclas 1, 2, 3):
  - create_solar_system:  sol fixo + dois planetas em orbita
  - create_binary_stars:  duas estrelas orbitando entre si
  - create_moon_system:   planeta com lua orbitando ao redor
"""

import random
import numpy as np

from body import Planet
from config import (
    G, COLORS, WIDTH, HEIGHT,
    ORBIT_VARIATION_MIN, ORBIT_VARIATION_MAX,
    PLANET_MASS_MIN, PLANET_MASS_MAX, ORBIT_MIN_DIST,
)


def orbital_velocity(anchor_mass, distance):
    """Velocidade circular para orbita estavel: v = sqrt(G * M / r)."""
    return (G * anchor_mass / distance) ** 0.5


def create_solar_system():
    """Cenario padrao: sol fixo + dois planetas em orbita circular."""
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
    """Cenario avancado: duas estrelas orbitando entre si + um planeta circumbinario."""
    cx, cy = WIDTH / 2, HEIGHT / 2
    r = 120
    # Velocidade orbital de cada estrela em relacao ao centro de massa.
    # Para duas massas iguais, cada uma orbita o centro a metade da distancia.
    v = orbital_velocity(5000, r * 2) * 0.7

    s1 = Planet(cx - r, cy, vx=0, vy=+v, mass=5000, color=(1.0, 0.9, 0.2))
    s2 = Planet(cx + r, cy, vx=0, vy=-v, mass=5000, color=(1.0, 0.6, 0.2))

    # Planeta longe orbitando o sistema todo
    R = 350
    vp = orbital_velocity(10000, R) * 0.9
    p = Planet(cx + R, cy, vx=0, vy=+vp, mass=20, color=(0.4, 0.9, 0.9))

    return [s1, s2, p]


def create_moon_system():
    """Sol + planeta grande + lua orbitando o planeta."""
    cx, cy = WIDTH / 2, HEIGHT / 2

    sol = Planet(cx, cy, vx=0, vy=0, mass=5000,
                 color=(1.0, 0.9, 0.2), pinned=True)

    # Planeta em orbita ao redor do sol
    r_planet = 220
    v_planet = orbital_velocity(sol.mass, r_planet)
    planet = Planet(cx + r_planet, cy, vx=0, vy=+v_planet,
                    mass=200, color=(0.4, 1.0, 0.5))

    # Lua orbitando o planeta -- velocidade = velocidade do planeta + orbital local
    r_moon = 30
    v_moon_local = orbital_velocity(planet.mass, r_moon)
    moon = Planet(cx + r_planet + r_moon, cy,
                  vx=0, vy=+v_planet + v_moon_local,
                  mass=5, color=(0.8, 0.8, 0.8))

    return [sol, planet, moon]


def add_orbital_planet(bodies, mouse_x, mouse_y):
    """
    Cria um planeta no ponto clicado com velocidade orbital aproximada.

    Em vez de velocidade aleatoria (que sempre cairia no sol), calculamos
    a tangente perpendicular ao raio em relacao ao corpo mais massivo.
    Variacao de +-30% gera orbitas eliticas variadas.
    """
    if not bodies:
        return

    anchor = max(bodies, key=lambda b: b.mass)
    dx = mouse_x - anchor.pos[0]
    dy = mouse_y - anchor.pos[1]
    dist = max(np.linalg.norm([dx, dy]), ORBIT_MIN_DIST)

    v_orb = orbital_velocity(anchor.mass, dist)
    fator = random.uniform(ORBIT_VARIATION_MIN, ORBIT_VARIATION_MAX)

    # Tangente ao raio: rotacao de 90 graus do vetor (dx,dy) normalizado
    tx = -dy / dist
    ty = +dx / dist

    bodies.append(Planet(
        mouse_x, mouse_y,
        vx=tx * v_orb * fator,
        vy=ty * v_orb * fator,
        mass=random.uniform(PLANET_MASS_MIN, PLANET_MASS_MAX),
        color=random.choice(COLORS),
    ))
