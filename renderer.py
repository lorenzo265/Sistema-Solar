import math

from OpenGL.GL import *
from OpenGL.GLUT import glutBitmapCharacter, GLUT_BITMAP_9_BY_15

from config import CIRCLE_SIDES, FORCE_VECTOR_SCALE, FORCE_VECTOR_COLOR


def clear_screen():
    glClear(GL_COLOR_BUFFER_BIT)


def draw_circle(x, y, radius, color, filled=True):
    r, g, b = color
    glColor3f(r, g, b)

    if filled:
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(x, y)
        for i in range(CIRCLE_SIDES + 1):
            angle = 2 * math.pi * i / CIRCLE_SIDES
            glVertex2f(x + math.cos(angle) * radius,
                       y + math.sin(angle) * radius)
    else:
        glBegin(GL_LINE_LOOP)
        for i in range(CIRCLE_SIDES):
            angle = 2 * math.pi * i / CIRCLE_SIDES
            glVertex2f(x + math.cos(angle) * radius,
                       y + math.sin(angle) * radius)

    glEnd()


def draw_trail(trail, color):
    if len(trail) < 2:
        return

    r, g, b = color
    n = len(trail)

    glBegin(GL_LINE_STRIP)
    for i, point in enumerate(trail):
        alpha = i / n
        glColor4f(r, g, b, alpha)
        glVertex2f(point[0], point[1])
    glEnd()


def draw_text(x, y, text, color=(1.0, 1.0, 1.0)):
    r, g, b = color
    glColor3f(r, g, b)
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(ch))


def draw_arrow(x1, y1, x2, y2, color):
    r, g, b = color
    glColor3f(r, g, b)

    glBegin(GL_LINES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()

    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)
    if length < 1e-3:
        return
    ux, uy = dx / length, dy / length
    head_size = min(8, length * 0.3)

    # Rotacao de ±150 graus em torno da direcao do vetor para formar a ponta
    cos_a = math.cos(math.radians(150))
    sin_a = math.sin(math.radians(150))
    hx1 = ux * cos_a - uy * sin_a
    hy1 = ux * sin_a + uy * cos_a
    hx2 = ux * cos_a - uy * (-sin_a)
    hy2 = ux * (-sin_a) + uy * cos_a

    glBegin(GL_LINES)
    glVertex2f(x2, y2)
    glVertex2f(x2 + hx1 * head_size, y2 + hy1 * head_size)
    glVertex2f(x2, y2)
    glVertex2f(x2 + hx2 * head_size, y2 + hy2 * head_size)
    glEnd()


def draw_force_vectors(bodies, accelerations):
    for body, acc in zip(bodies, accelerations):
        if body.pinned:
            continue
        ax, ay = acc[0] * FORCE_VECTOR_SCALE, acc[1] * FORCE_VECTOR_SCALE
        if abs(ax) < 0.5 and abs(ay) < 0.5:
            continue
        draw_arrow(body.pos[0], body.pos[1],
                   body.pos[0] + ax, body.pos[1] + ay,
                   color=FORCE_VECTOR_COLOR)


def render(bodies):
    clear_screen()

    for body in bodies:
        draw_trail(body.trail, body.color)

    for body in bodies:
        draw_circle(body.pos[0], body.pos[1], body.radius(), body.color)
