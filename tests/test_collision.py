"""Testes de deteccao e fusao de colisoes."""

import pytest

import physics
from body import Planet


def test_no_collision_far_apart():
    a = Planet(0, 0, 0, 0, mass=10, color=(1, 1, 1))
    b = Planet(500, 0, 0, 0, mass=10, color=(1, 1, 1))
    result = physics.check_collisions([a, b])
    assert len(result) == 2


def test_two_bodies_touching_merge():
    a = Planet(0, 0, vx=10, vy=0, mass=10, color=(1, 1, 1))
    b = Planet(1, 0, vx=-10, vy=0, mass=10, color=(1, 1, 1))
    result = physics.check_collisions([a, b])
    assert len(result) == 1
    merged = result[0]
    assert merged.mass == 20
    # Momento total era zero -> velocidade resultante deve ser zero
    assert abs(merged.vel[0]) < 1e-6


def test_pinned_absorbs_planet():
    sol = Planet(0, 0, 0, 0, mass=5000, color=(1, 1, 0), pinned=True)
    p = Planet(1, 0, 0, 0, mass=10, color=(1, 1, 1))
    result = physics.check_collisions([sol, p])
    assert len(result) == 1
    assert result[0].pinned is True
    # Sol nao ganha massa do planeta absorvido (regra atual da simulacao)
    assert result[0].mass == 5000


def test_momentum_conservation_in_merge():
    a = Planet(0, 0, vx=20, vy=0, mass=30, color=(1, 1, 1))
    b = Planet(1, 0, vx=0, vy=10, mass=10, color=(1, 1, 1))
    # Momento antes: (30*20 + 10*0, 30*0 + 10*10) = (600, 100)
    result = physics.check_collisions([a, b])
    merged = result[0]
    # Velocidade esperada: (600/40, 100/40) = (15, 2.5)
    assert merged.vel[0] == pytest.approx(15.0)
    assert merged.vel[1] == pytest.approx(2.5)
