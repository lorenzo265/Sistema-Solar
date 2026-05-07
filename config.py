"""
config.py - Todas as constantes da simulacao em um unico lugar.

Qualquer ajuste de gameplay, fisica, visual ou HUD muda aqui,
nao no meio da logica. Isso facilita experimentar parametros e
mantem o resto do codigo focado em comportamento, nao em numeros magicos.
"""

# ── Janela ────────────────────────────────────────────────────────────────
WIDTH    = 900
HEIGHT   = 700
FPS      = 60
TITLE    = "Simulador de Orbitas - PyOpenGL"
BG_COLOR = (0.05, 0.05, 0.1, 1.0)

# ── Fisica ────────────────────────────────────────────────────────────────
G         = 500.0    # constante gravitacional ajustada para pixels
MIN_DIST  = 10.0     # distancia minima para evitar forca infinita
MAX_SPEED = 800.0    # velocidade maxima de um corpo (px/s)
DT_CAP    = 1 / 20   # delta time maximo para evitar explosoes em lag spike

# ── Visual ────────────────────────────────────────────────────────────────
TRAIL_LENGTH = 150   # pontos guardados na trilha de cada planeta
CIRCLE_SIDES = 64    # lados do poligono que aproxima o circulo
RADIUS_SCALE = 0.4   # expoente para calcular raio visual: mass^RADIUS_SCALE
RADIUS_MIN   = 4     # raio minimo em pixels

# ── HUD ───────────────────────────────────────────────────────────────────
HUD_LINE_HEIGHT  = 18
HUD_MAX_PLANETS  = 6
HUD_MARGIN       = 10
HUD_COLOR_STATUS = (1.0, 1.0, 0.3)
HUD_COLOR_INFO   = (0.8, 0.8, 0.8)
HUD_COLOR_CTRL   = (0.4, 0.4, 0.4)
HUD_COLOR_EXTRA  = (0.5, 0.5, 0.5)

# ── Orbital (para add_orbital_planet) ─────────────────────────────────────
ORBIT_VARIATION_MIN = 0.7
ORBIT_VARIATION_MAX = 1.3
PLANET_MASS_MIN     = 10
PLANET_MASS_MAX     = 80
ORBIT_MIN_DIST      = 50  # distancia minima do clique ao corpo ancora

# ── Velocidade do tempo (Feature 1) ───────────────────────────────────────
TIME_SCALES        = [0.25, 0.5, 1.0, 2.0, 4.0]
TIME_SCALE_DEFAULT = 2  # indice em TIME_SCALES que comeca em 1.0x

# ── Vetores de forca (Feature 4) ──────────────────────────────────────────
FORCE_VECTOR_SCALE = 0.5
FORCE_VECTOR_COLOR = (1.0, 0.3, 0.3)

# ── Paleta de cores para novos planetas ───────────────────────────────────
COLORS = [
    (0.3, 0.7, 1.0),   # azul
    (1.0, 0.6, 0.2),   # laranja
    (0.4, 1.0, 0.5),   # verde
    (1.0, 0.4, 0.4),   # vermelho
    (0.9, 0.9, 0.3),   # amarelo
    (0.8, 0.4, 1.0),   # roxo
    (0.4, 0.9, 0.9),   # ciano
]
