"""
missions.py - Modo missao (desafio orbital).

Cada missao tem:
  - description: texto exibido no HUD
  - check_fn:    funcao(bodies) -> bool, avaliada a cada frame

Quando a checagem retorna True, a missao e marcada como completa
e o HUD passa a mostrar "MISSAO COMPLETA". O aluno pode trocar
de missao com a tecla M.

Educacional: transforma exploracao livre em aprendizado guiado
com feedback imediato.
"""

import numpy as np

import physics


class Mission:
    def __init__(self, description, check_fn):
        self.description = description
        self.check_fn = check_fn
        self.completed = False

    def update(self, bodies):
        """Avalia o estado atual. Uma vez completa, fica completa."""
        if not self.completed and self.check_fn(bodies):
            self.completed = True

    def reset(self):
        self.completed = False


# ── Predicados auxiliares ────────────────────────────────────────────────

def _orbiting_bodies(bodies):
    """Corpos nao-pinned que sao candidatos a estar em orbita."""
    return [b for b in bodies if not b.pinned]


def _anchor(bodies):
    return max(bodies, key=lambda b: b.mass) if bodies else None


def _has_bound_orbit(bodies, min_dist=None, max_dist=None):
    """Existe pelo menos um corpo em orbita ligada (energia < 0)?"""
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
    """Algum corpo atingiu velocidade de escape?"""
    a = _anchor(bodies)
    if a is None:
        return False
    for b in _orbiting_bodies(bodies):
        if b is a:
            continue
        info = physics.orbital_info(b, a)
        if not info["bound"]:
            return True
    return False


# ── Catalogo de missoes ──────────────────────────────────────────────────

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
    """Avanca para a proxima missao do catalogo (em ciclo)."""
    return (current_index + 1) % len(MISSIONS)


def get(index):
    """Retorna uma instancia nova (zerada) da missao no indice dado."""
    template = MISSIONS[index]
    return Mission(template.description, template.check_fn)
