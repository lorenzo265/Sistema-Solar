import physics
from config import (
    HUD_LINE_HEIGHT, HUD_MAX_PLANETS, HUD_MARGIN,
    HUD_COLOR_STATUS, HUD_COLOR_INFO, HUD_COLOR_CTRL, HUD_COLOR_EXTRA,
    TIME_SCALES,
)
from renderer import draw_text


def _anchor_of(bodies):
    return max(bodies, key=lambda b: b.mass) if bodies else None


def draw(bodies, height, paused, time_scale_index, show_forces, mission=None):
    y = height - 20

    state = "PAUSADO" if paused else "RODANDO"
    draw_text(HUD_MARGIN, y, f"Estado: {state}", color=HUD_COLOR_STATUS)
    y -= HUD_LINE_HEIGHT

    scale = TIME_SCALES[time_scale_index]
    draw_text(HUD_MARGIN, y, f"Tempo: {scale:.2f}x", color=HUD_COLOR_INFO)
    y -= HUD_LINE_HEIGHT

    forces_state = "ON" if show_forces else "off"
    draw_text(HUD_MARGIN, y,
              f"Corpos: {len(bodies)}   Vetores: {forces_state}",
              color=HUD_COLOR_INFO)
    y -= HUD_LINE_HEIGHT

    anchor = _anchor_of(bodies)
    for i, body in enumerate(bodies[:HUD_MAX_PLANETS]):
        label = "SOL" if body.pinned else f"P{i + 1}"
        line = f"  {label}: m={int(body.mass)}  v={body.speed:.0f}"

        if anchor is not None and body is not anchor:
            info = physics.orbital_info(body, anchor)
            tag = "OK" if info["bound"] else "ESC"
            line += f"  d={info['dist']:.0f} [{tag}]"

        draw_text(HUD_MARGIN, y, line, color=body.color)
        y -= HUD_LINE_HEIGHT

    if len(bodies) > HUD_MAX_PLANETS:
        extras = len(bodies) - HUD_MAX_PLANETS
        draw_text(HUD_MARGIN, y, f"  ... +{extras} outros", color=HUD_COLOR_EXTRA)
        y -= HUD_LINE_HEIGHT

    if mission is not None:
        status_color = (0.4, 1.0, 0.4) if mission.completed else (1.0, 0.7, 0.3)
        prefix = "MISSAO COMPLETA: " if mission.completed else "MISSAO: "
        draw_text(HUD_MARGIN, y - 10, prefix + mission.description,
                  color=status_color)

    draw_text(HUD_MARGIN,  96, "Clique: planeta  |  V: vetores de forca",
              color=HUD_COLOR_CTRL)
    draw_text(HUD_MARGIN,  78, "+/-: velocidade  |  ESPACO: pausar",
              color=HUD_COLOR_CTRL)
    draw_text(HUD_MARGIN,  60, "1: solar  2: binario  3: lua",
              color=HUD_COLOR_CTRL)
    draw_text(HUD_MARGIN,  42, "M: trocar missao  |  R: reiniciar",
              color=HUD_COLOR_CTRL)
    draw_text(HUD_MARGIN,  24, "Q: sair", color=HUD_COLOR_CTRL)
