"""Testes da fisica: gravidade, integracao e clamp de velocidade."""

import numpy as np
import pytest

import physics
from body import Planet
from config import G, MAX_SPEED


def test_pinned_body_does_not_move():
    sol = Planet(100, 100, 0, 0, mass=5000, color=(1, 1, 0), pinned=True)
    p = Planet(200, 100, 0, 50, mass=10, color=(1, 1, 1))
    physics.step([sol, p], dt=0.1)
    assert sol.pos[0] == 100 and sol.pos[1] == 100


def test_attraction_pulls_bodies_together():
    a = Planet(0, 0, 0, 0, mass=1000, color=(1, 1, 1))
    b = Planet(100, 0, 0, 0, mass=1000, color=(1, 1, 1))
    accs = physics.compute_accelerations([a, b])
    # a deve acelerar para +x, b para -x
    assert accs[0][0] > 0
    assert accs[1][0] < 0
    # Forca igual e oposta -> aceleracoes simetricas (mesmas massas)
    assert accs[0][0] == pytest.approx(-accs[1][0])


def test_circular_orbit_stays_bounded():
    """Um planeta com velocidade orbital exata deve manter distancia ~estavel."""
    sol = Planet(500, 500, 0, 0, mass=5000, color=(1, 1, 0), pinned=True)
    r = 150
    v = (G * sol.mass / r) ** 0.5
    p = Planet(500 + r, 500, 0, v, mass=10, color=(1, 1, 1))

    bodies = [sol, p]
    initial_dist = np.linalg.norm(p.pos - sol.pos)

    # Simula 5 segundos com dt pequeno
    for _ in range(500):
        physics.step(bodies, dt=0.01)

    final_dist = np.linalg.norm(p.pos - sol.pos)
    # Euler diverge um pouco -- toleramos 30%
    assert 0.7 * initial_dist < final_dist < 1.3 * initial_dist


def test_max_speed_clamp():
    """Mesmo numa orbita rasante, ninguem deve passar de MAX_SPEED."""
    a = Planet(0, 0, 0, MAX_SPEED * 2, mass=10, color=(1, 1, 1))
    physics.step([a], dt=0.001)
    assert a.speed <= MAX_SPEED + 1e-6


def test_min_dist_prevents_infinite_force():
    """Dois corpos colados nao podem gerar aceleracao infinita."""
    a = Planet(0, 0, 0, 0, mass=100, color=(1, 1, 1))
    b = Planet(0, 0, 0, 0, mass=100, color=(1, 1, 1))
    accs = physics.compute_accelerations([a, b])
    assert np.all(np.isfinite(accs[0]))
    assert np.all(np.isfinite(accs[1]))


def test_orbital_info_bound_vs_unbound():
    sol = Planet(0, 0, 0, 0, mass=5000, color=(1, 1, 0), pinned=True)
    # Velocidade orbital circular -> ligada
    r = 200
    v = (G * sol.mass / r) ** 0.5
    bound = Planet(r, 0, 0, v, mass=10, color=(1, 1, 1))
    info_b = physics.orbital_info(bound, sol)
    assert info_b["bound"] is True
    assert info_b["energy"] < 0

    # Velocidade muito acima da escape -> nao ligada
    v_esc = (2 * G * sol.mass / r) ** 0.5
    free = Planet(r, 0, 0, v_esc * 2, mass=10, color=(1, 1, 1))
    info_f = physics.orbital_info(free, sol)
    assert info_f["bound"] is False
    assert info_f["energy"] > 0
