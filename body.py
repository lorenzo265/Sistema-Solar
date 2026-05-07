"""
body.py - Define o que e um planeta na simulacao.

Cada planeta tem:
  - posicao (x, y) em pixels na tela
  - velocidade (vx, vy) em pixels por segundo
  - massa, que determina a forca gravitacional
  - cor para desenhar na tela
  - trilha: fila circular das ultimas posicoes (para desenhar o rastro)
  - pinned: se True, o corpo atrai outros mas nao se move (ex: sol fixo)
"""

from collections import deque
import numpy as np

from config import TRAIL_LENGTH, RADIUS_SCALE, RADIUS_MIN


class Planet:
    def __init__(self, x, y, vx, vy, mass, color, pinned=False):
        # Posicao como array numpy facilita os calculos vetoriais no physics.py
        self.pos = np.array([x, y], dtype=float)
        self.vel = np.array([vx, vy], dtype=float)
        self.mass = float(mass)
        self.color = self._validate_color(color)
        self.pinned = pinned

        # deque com maxlen descarta o elemento mais antigo automaticamente -- O(1)
        self.trail = deque(maxlen=TRAIL_LENGTH)

    @staticmethod
    def _validate_color(color):
        if len(color) != 3:
            raise ValueError(f"color deve ter 3 componentes (R,G,B), recebeu {color}")
        for c in color:
            if not 0.0 <= c <= 1.0:
                raise ValueError(f"componentes de cor devem estar em [0,1], recebeu {color}")
        return tuple(float(c) for c in color)

    def update_trail(self):
        """Salva a posicao atual na trilha. O deque descarta pontos antigos sozinho."""
        self.trail.append(self.pos.copy())

    def radius(self):
        """Raio visual do planeta - planetas maiores aparecem maiores na tela."""
        return max(RADIUS_MIN, int(self.mass ** RADIUS_SCALE))

    @property
    def speed(self):
        """Velocidade escalar (modulo do vetor velocidade)."""
        return float(np.linalg.norm(self.vel))

    def __repr__(self):
        return (f"Planet(pos={self.pos.round(1).tolist()}, "
                f"vel={self.vel.round(1).tolist()}, "
                f"mass={self.mass:.0f}, pinned={self.pinned})")
