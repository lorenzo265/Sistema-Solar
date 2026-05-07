"""
main.py - Ponto de entrada do simulador de orbitas.

Responsabilidade unica: loop principal (input -> fisica -> render).
Toda a logica de criacao de planetas vive em scenarios.py;
a fisica em physics.py; o HUD em hud.py; primitivas em renderer.py.

Controles:
  - Clique esquerdo : adiciona um planeta orbital no cursor
  - Espaco          : pausa / continua
  - + / -           : aumenta / reduz a velocidade do tempo
  - 1 / 2 / 3       : carrega cenarios pre-definidos
  - V               : alterna desenho dos vetores de forca
  - M               : avanca para a proxima missao
  - R               : reinicia o cenario atual
  - Q / fechar      : encerra
"""

import sys

import pygame
from pygame.locals import (
    QUIT, KEYDOWN, MOUSEBUTTONDOWN,
    K_q, K_r, K_v, K_m, K_SPACE,
    K_1, K_2, K_3,
    K_PLUS, K_MINUS, K_KP_PLUS, K_KP_MINUS, K_EQUALS,
    DOUBLEBUF, OPENGL,
)
from OpenGL.GL import (
    glMatrixMode, glLoadIdentity, glOrtho, glClearColor,
    glEnable, glBlendFunc,
    GL_PROJECTION, GL_MODELVIEW, GL_BLEND,
    GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA,
)
from OpenGL.GLUT import glutInit

import physics
import renderer
import hud
import scenarios
import missions
from config import (
    WIDTH, HEIGHT, FPS, TITLE, BG_COLOR,
    DT_CAP, TIME_SCALES, TIME_SCALE_DEFAULT,
)


SCENARIO_BUILDERS = {
    K_1: scenarios.create_solar_system,
    K_2: scenarios.create_binary_stars,
    K_3: scenarios.create_moon_system,
}


def setup_opengl():
    """Projecao 2D em coordenadas de pixel; GL_BLEND habilitado uma vez."""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, WIDTH, 0, HEIGHT, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    glClearColor(*BG_COLOR)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)


def main():
    pygame.init()
    glutInit(sys.argv)

    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF | OPENGL)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    setup_opengl()

    # Estado da sessao
    bodies = scenarios.create_solar_system()
    current_scenario = scenarios.create_solar_system
    paused = False
    time_scale_index = TIME_SCALE_DEFAULT
    show_forces = False
    mission_index = 0
    mission = missions.get(mission_index)

    while True:
        # Delta time real, com cap para evitar saltos em lag spike
        dt = min(clock.tick(FPS) / 1000.0, DT_CAP)
        dt_sim = dt * TIME_SCALES[time_scale_index]

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_q:
                    pygame.quit()
                    sys.exit()

                elif event.key == K_SPACE:
                    paused = not paused

                elif event.key == K_r:
                    bodies = current_scenario()
                    mission.reset()

                elif event.key == K_v:
                    show_forces = not show_forces

                elif event.key == K_m:
                    mission_index = missions.cycle(mission_index)
                    mission = missions.get(mission_index)

                elif event.key in (K_PLUS, K_KP_PLUS, K_EQUALS):
                    time_scale_index = min(len(TIME_SCALES) - 1,
                                           time_scale_index + 1)

                elif event.key in (K_MINUS, K_KP_MINUS):
                    time_scale_index = max(0, time_scale_index - 1)

                elif event.key in SCENARIO_BUILDERS:
                    current_scenario = SCENARIO_BUILDERS[event.key]
                    bodies = current_scenario()
                    mission.reset()

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                # Pygame Y cresce para baixo; OpenGL Y cresce para cima.
                mx, my = event.pos
                scenarios.add_orbital_planet(bodies, mx, HEIGHT - my)

        if not paused:
            bodies = physics.update(bodies, dt_sim)
            mission.update(bodies)

        renderer.render(bodies)
        if show_forces:
            renderer.draw_force_vectors(bodies, physics.compute_accelerations(bodies))
        hud.draw(bodies, HEIGHT, paused, time_scale_index, show_forces, mission)

        pygame.display.flip()


if __name__ == "__main__":
    main()
