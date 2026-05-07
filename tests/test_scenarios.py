"""Smoke tests dos cenarios e missoes."""

import scenarios
import missions


def test_solar_system_has_pinned_sun():
    bodies = scenarios.create_solar_system()
    assert any(b.pinned for b in bodies)
    assert len(bodies) == 3


def test_binary_stars_two_massive_bodies():
    bodies = scenarios.create_binary_stars()
    massive = [b for b in bodies if b.mass >= 5000]
    assert len(massive) >= 2


def test_moon_system_has_three_bodies():
    bodies = scenarios.create_moon_system()
    assert len(bodies) == 3


def test_add_orbital_planet_increases_count():
    bodies = scenarios.create_solar_system()
    n0 = len(bodies)
    scenarios.add_orbital_planet(bodies, 100, 100)
    assert len(bodies) == n0 + 1


def test_mission_completes_when_predicate_true():
    m = missions.Mission("sempre completa", lambda bodies: True)
    assert m.completed is False
    m.update(scenarios.create_solar_system())
    assert m.completed is True


def test_mission_cycle_wraps():
    n = len(missions.MISSIONS)
    assert missions.cycle(n - 1) == 0


def test_circular_orbit_satisfies_bound_mission():
    """O sistema solar inicial ja tem um corpo em orbita ligada < 200px."""
    bodies = scenarios.create_solar_system()
    m = missions.get(0)  # "ligada a menos de 200px"
    m.update(bodies)
    assert m.completed is True
