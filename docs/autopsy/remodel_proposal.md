# PROPOSTA DE REMODELACAO - simulador_orbitas

---

## ESTRUTURA DE DIRETORIOS ALVO

```
simulador_orbitas/
|
+-- config.py          # NOVO: todas as constantes do projeto em um lugar
+-- body.py            # REFATORAR: adicionar __repr__, validacao de cor
+-- physics.py         # REFATORAR: separar step() de check_collisions()
+-- renderer.py        # REFATORAR: remover acoplamento ao game state
+-- hud.py             # NOVO: HUD separado do renderer grafico
+-- scenarios.py       # NOVO: cenarios iniciais e fabrica de planetas
+-- main.py            # SIMPLIFICAR: so o loop, sem logica de criacao
|
+-- tests/
|   +-- test_physics.py    # NOVO: testes da fisica
|   +-- test_body.py       # NOVO: testes da classe Planet
|   +-- test_collision.py  # NOVO: testes de colisao e fusao
|
+-- docs/
|   +-- autopsy/
+-- requirements.txt
```

---

## 1. config.py (novo arquivo)

Todas as constantes hoje espalhadas por 4 arquivos vao para um lugar so.
Qualquer ajuste de gameplay muda aqui, nao no meio da logica.

```python
# config.py - Todas as constantes da simulacao

# Janela
WIDTH         = 900
HEIGHT        = 700
FPS           = 60
TITLE         = "Simulador de Orbitas"
BG_COLOR      = (0.05, 0.05, 0.1, 1.0)

# Fisica
G             = 500.0    # constante gravitacional (ajustada para pixels)
MIN_DIST      = 10.0     # distancia minima para evitar forca infinita
MAX_SPEED     = 800.0    # velocidade maxima de um corpo (px/s)
DT_CAP        = 1 / 20   # delta time maximo para evitar explosoes em lag

# Visual
TRAIL_LENGTH  = 150      # pontos na trilha
CIRCLE_SIDES  = 64       # lados do poligono que aproxima o circulo
RADIUS_SCALE  = 0.4      # expoente para calcular raio visual: mass^RADIUS_SCALE
RADIUS_MIN    = 4        # raio minimo em pixels

# HUD
HUD_LINE_HEIGHT  = 18
HUD_MAX_PLANETS  = 6
HUD_MARGIN       = 10
HUD_COLOR_STATUS = (1.0, 1.0, 0.3)
HUD_COLOR_INFO   = (0.8, 0.8, 0.8)
HUD_COLOR_CTRL   = (0.4, 0.4, 0.4)

# Orbital (para add_orbital_planet)
ORBIT_VARIATION_MIN = 0.7   # fator minimo de variacao da velocidade orbital
ORBIT_VARIATION_MAX = 1.3   # fator maximo
PLANET_MASS_MIN     = 10
PLANET_MASS_MAX     = 80

# Paleta de cores para novos planetas
COLORS = [
    (0.3, 0.7, 1.0),
    (1.0, 0.6, 0.2),
    (0.4, 1.0, 0.5),
    (1.0, 0.4, 0.4),
    (0.9, 0.9, 0.3),
    (0.8, 0.4, 1.0),
    (0.4, 0.9, 0.9),
]
```

---

## 2. scenarios.py (novo arquivo)

Toda a logica de "quais planetas existem no inicio" e "como criar um planeta orbital"
sai do main.py e vai aqui. main.py deixa de precisar de numpy e de physics.G.

```python
# scenarios.py - Cenarios e fabrica de planetas

import random
import numpy as np
from body import Planet
from config import G, COLORS, ORBIT_VARIATION_MIN, ORBIT_VARIATION_MAX
from config import PLANET_MASS_MIN, PLANET_MASS_MAX, WIDTH, HEIGHT


def orbital_velocity(anchor_mass, distance):
    """Velocidade circular para orbita estavel: v = sqrt(G * M / r)"""
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
    """Cenario avancado: dois sois orbitando entre si."""
    cx, cy = WIDTH / 2, HEIGHT / 2
    r = 120
    v = orbital_velocity(5000, r * 2) * 0.7
    s1 = Planet(cx - r, cy, vx=0, vy=+v, mass=5000, color=(1.0, 0.9, 0.2))
    s2 = Planet(cx + r, cy, vx=0, vy=-v, mass=5000, color=(1.0, 0.6, 0.2))
    return [s1, s2]


def add_orbital_planet(bodies, mouse_x, mouse_y):
    """
    Cria um planeta no ponto clicado com velocidade orbital aproximada.
    A velocidade e tangencial ao raio em relacao ao corpo mais massivo.
    """
    anchor = max(bodies, key=lambda b: b.mass)
    dx = mouse_x - anchor.pos[0]
    dy = mouse_y - anchor.pos[1]
    dist = max(np.linalg.norm([dx, dy]), 50)

    v_orb = orbital_velocity(anchor.mass, dist)
    fator = random.uniform(ORBIT_VARIATION_MIN, ORBIT_VARIATION_MAX)

    # Tangente perpendicular ao raio
    tx = -dy / dist
    ty = +dx / dist

    bodies.append(Planet(
        mouse_x, mouse_y,
        vx=tx * v_orb * fator,
        vy=ty * v_orb * fator,
        mass=random.uniform(PLANET_MASS_MIN, PLANET_MASS_MAX),
        color=random.choice(COLORS)
    ))
```

---

## 3. hud.py (novo arquivo)

HUD separado do renderer grafico. renderer.py fica so com primitivas OpenGL puras.
hud.py conhece o game state; renderer.py nao precisa saber nada disso.

```python
# hud.py - Interface de informacoes na tela

import math
from config import HUD_LINE_HEIGHT, HUD_MAX_PLANETS, HUD_MARGIN
from config import HUD_COLOR_STATUS, HUD_COLOR_INFO, HUD_COLOR_CTRL
from renderer import draw_text


def draw(bodies, height, paused):
    """Renderiza o painel de informacoes e os controles."""
    y = height - 20

    state = "PAUSADO" if paused else "RODANDO"
    draw_text(HUD_MARGIN, y, f"Estado: {state}", color=HUD_COLOR_STATUS)
    y -= HUD_LINE_HEIGHT

    draw_text(HUD_MARGIN, y, f"Corpos: {len(bodies)}", color=HUD_COLOR_INFO)
    y -= HUD_LINE_HEIGHT

    for i, body in enumerate(bodies[:HUD_MAX_PLANETS]):
        speed = math.sqrt(body.vel[0] ** 2 + body.vel[1] ** 2)
        label = "SOL" if body.pinned else f"P{i + 1}"
        draw_text(HUD_MARGIN, y,
                  f"  {label}: massa={int(body.mass)}  vel={speed:.0f}",
                  color=body.color)
        y -= HUD_LINE_HEIGHT

    if len(bodies) > HUD_MAX_PLANETS:
        extras = len(bodies) - HUD_MAX_PLANETS
        draw_text(HUD_MARGIN, y, f"  ... +{extras} outros", color=(0.5, 0.5, 0.5))

    draw_text(HUD_MARGIN, 60, "Clique: adicionar planeta", color=HUD_COLOR_CTRL)
    draw_text(HUD_MARGIN, 42, "ESPACO: pausar/continuar", color=HUD_COLOR_CTRL)
    draw_text(HUD_MARGIN, 24, "R: reiniciar  |  Q: sair", color=HUD_COLOR_CTRL)
```

---

## 4. Melhorias em body.py

```python
# adicionar em Planet:

def __repr__(self):
    return (f"Planet(pos={self.pos.round(1)}, mass={self.mass:.0f}, "
            f"pinned={self.pinned})")

@property
def speed(self):
    """Velocidade escalar (modulo do vetor velocidade)."""
    return float(np.linalg.norm(self.vel))
```

---

## 5. Melhorias em physics.py

Separar step() de check_collisions() -- duas funcoes com uma responsabilidade cada.
Adicionar MAX_SPEED para evitar velocidades infinitas.

```python
# physics.py refatorado:

def step(bodies, dt):
    """So a integracao numerica -- sem colisao."""
    ...
    for body in bodies:
        if not body.pinned:
            body.vel += accelerations[i] * dt
            # Clamp de velocidade maxima
            speed = np.linalg.norm(body.vel)
            if speed > MAX_SPEED:
                body.vel = body.vel / speed * MAX_SPEED
            body.pos += body.vel * dt
        body.update_trail()


def update(bodies, dt):
    """Fisica completa: step + colisao. Retorna lista atualizada."""
    step(bodies, dt)
    return check_collisions(bodies)


def check_collisions(bodies):
    """Detecta e funde colisoes. Funcao publica e testavel sozinha."""
    ...
```

---

## 5 NOVAS FUNCOES EDUCATIVAS

### Feature 1 -- Velocidade do tempo (tecla +/-)
**Onde:** main.py + config.py
**O que faz:** Multiplica o DT por um fator (0.25x, 0.5x, 1x, 2x, 4x).
Permite ver orbitas em fast-forward ou slow-motion.
**Educacional:** demonstra que as leis fisicas sao independentes da escala de tempo.
```python
TIME_SCALES = [0.25, 0.5, 1.0, 2.0, 4.0]
time_scale_index = 2  # comeca em 1.0x
# K_PLUS -> time_scale_index = min(4, index+1)
# K_MINUS -> time_scale_index = max(0, index-1)
dt_real = dt * TIME_SCALES[time_scale_index]
```

### Feature 2 -- Telemetria orbital no HUD
**Onde:** hud.py + nova funcao orbital_info() em physics.py
**O que faz:** Para cada planeta, calcula e exibe:
  - Excentricidade da orbita (0 = circular, >1 = hiperbole)
  - Periodo orbital estimado
  - Distancia atual ao sol
**Educacional:** demonstra as Leis de Kepler diretamente na tela.
```python
def orbital_info(planet, anchor):
    dist = np.linalg.norm(planet.pos - anchor.pos)
    speed = planet.speed
    v_escape = (2 * G * anchor.mass / dist) ** 0.5
    bound = speed < v_escape  # True = orbita fechada
    return {"dist": dist, "speed": speed, "bound": bound}
```

### Feature 3 -- Cenarios pre-definidos (teclas 1, 2, 3)
**Onde:** scenarios.py + main.py
**O que faz:** Tecla 1 = sistema solar simples, Tecla 2 = estrelas binarias,
Tecla 3 = sistema com lua (planeta + satelite).
**Educacional:** permite comparar comportamentos orbitais diferentes instantaneamente.
```python
SCENARIOS = {
    pygame.K_1: scenarios.create_solar_system,
    pygame.K_2: scenarios.create_binary_stars,
    pygame.K_3: scenarios.create_moon_system,
}
```

### Feature 4 -- Rastro de vetores de forca
**Onde:** renderer.py + nova funcao draw_force_vectors()
**O que faz:** Quando ativado (tecla V), desenha setas mostrando a direcao
e magnitude da forca gravitacional atuando em cada planeta.
**Educacional:** torna a forca invisivel visivel -- o aluno ve a fisica acontecendo.
```python
def draw_force_vector(body, acceleration):
    scale = 0.5  # ajustar para tamanho visivel
    ax, ay = acceleration * scale
    draw_arrow(body.pos[0], body.pos[1],
               body.pos[0] + ax, body.pos[1] + ay,
               color=(1.0, 0.3, 0.3))
```

### Feature 5 -- Modo missao (desafio orbital)
**Onde:** missions.py (novo arquivo)
**O que faz:** Define objetivos como "coloque um planeta em orbita circular
a menos de 200px do sol". O codigo checa a condicao a cada frame e exibe
"MISSAO COMPLETA" quando o aluno acerta.
**Educacional:** transforma a exploracao livre em aprendizado guiado com feedback imediato.
```python
class Mission:
    def __init__(self, description, check_fn):
        self.description = description  # texto exibido no HUD
        self.check_fn = check_fn        # funcao(bodies) -> bool

MISSION_CIRCULAR = Mission(
    "Coloque um planeta em orbita quase circular (excentricidade < 0.15)",
    lambda bodies: any(orbital_eccentricity(b, bodies[0]) < 0.15
                       for b in bodies[1:] if not b.pinned)
)
```

---

## PLANO DE MIGRACAO

### Fase A -- Esta semana (impacto imediato, risco zero)
1. Criar config.py com todas as constantes
2. Adicionar __repr__ e speed em body.py
3. Separar step() de check_collisions() em physics.py
4. Criar tests/test_physics.py com os 5 testes ja escritos

### Fase B -- Proxima semana (refatoracao limpa)
5. Criar scenarios.py e mover create_initial_bodies + add_orbital_planet
6. Criar hud.py e mover draw_hud para la
7. Limpar main.py: remover imports desnecessarios (GLU, numpy, OpenGL direto)
8. Limpar renderer.py: remover draw_hud, tornar puro de primitivas

### Fase C -- Features educativas (um por vez)
9. Feature 1: velocidade do tempo (+/-)
10. Feature 2: telemetria orbital no HUD
11. Feature 3: cenarios com teclas 1/2/3
12. Feature 4: vetores de forca (tecla V)
13. Feature 5: modo missao
