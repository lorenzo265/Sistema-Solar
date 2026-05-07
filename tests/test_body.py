"""Testes da classe Planet."""

import numpy as np
import pytest

from body import Planet


def test_speed_is_magnitude_of_velocity():
    p = Planet(0, 0, vx=3, vy=4, mass=10, color=(1, 0, 0))
    assert p.speed == pytest.approx(5.0)


def test_repr_contains_essential_fields():
    p = Planet(10, 20, vx=0, vy=0, mass=100, color=(1, 1, 1), pinned=True)
    r = repr(p)
    assert "mass=100" in r
    assert "pinned=True" in r


def test_radius_grows_with_mass():
    small = Planet(0, 0, 0, 0, mass=10, color=(1, 1, 1))
    big = Planet(0, 0, 0, 0, mass=1000, color=(1, 1, 1))
    assert big.radius() > small.radius()


def test_radius_has_minimum_floor():
    tiny = Planet(0, 0, 0, 0, mass=0.01, color=(1, 1, 1))
    assert tiny.radius() >= 4


def test_invalid_color_rejected():
    with pytest.raises(ValueError):
        Planet(0, 0, 0, 0, mass=10, color=(1.0, 2.0, 0.0))
    with pytest.raises(ValueError):
        Planet(0, 0, 0, 0, mass=10, color=(1.0, 0.0))


def test_update_trail_appends_position_copy():
    p = Planet(5, 5, 0, 0, mass=10, color=(1, 1, 1))
    p.update_trail()
    p.pos += np.array([1.0, 0.0])
    p.update_trail()
    # Primeiro ponto deve ter ficado em (5,5) -- nao seguiu a posicao
    assert list(p.trail)[0][0] == 5.0
    assert list(p.trail)[1][0] == 6.0
