"""
Shared wooden UI drawing helpers for settings menus across all levels.
"""
import pygame
import math
import random


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_wooden_bar(surface, rect, text, font, selected, tick=0):
    """Draw a single wooden plank button/bar."""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    if selected:
        wood_base = (180, 130, 70)
        wood_hi = (210, 165, 95)
        wood_dk = (130, 90, 45)
        border_col = (255, 220, 100)
    else:
        wood_base = (150, 105, 55)
        wood_hi = (175, 130, 75)
        wood_dk = (110, 75, 35)
        border_col = (100, 70, 35)

    pygame.draw.rect(surface, wood_base, rect, border_radius=8)
    pygame.draw.rect(surface, wood_hi, (x + 4, y + 2, w - 8, 4), border_radius=3)
    pygame.draw.rect(surface, wood_dk, (x + 4, y + h - 5, w - 8, 3), border_radius=2)
    rng = random.Random(rect.y * 31 + rect.x)
    for gi in range(x + 14, x + w - 14, max(18, w // 7)):
        pygame.draw.line(surface, lerp_color(wood_base, wood_dk, 0.15), (gi, y + 5), (gi, y + h - 5), 1)
    for nx, ny in [(x + 10, y + h // 2), (x + w - 10, y + h // 2)]:
        pygame.draw.circle(surface, (90, 65, 30), (nx, ny), 4)
        pygame.draw.circle(surface, wood_hi, (nx - 1, ny - 1), 2)
    pygame.draw.rect(surface, border_col, rect, 2, border_radius=8)
    txt_col = (50, 30, 10) if selected else (60, 40, 18)
    txt = font.render(text, True, txt_col)
    txt_rect = txt.get_rect(center=rect.center)
    shadow = font.render(text, True, (30, 18, 5))
    surface.blit(shadow, (txt_rect.x + 1, txt_rect.y + 2))
    surface.blit(txt, txt_rect)


def draw_wooden_panel(surface, panel_rect, title_text, title_font):
    """Draw a wooden panel background with title plank."""
    px, py, pw, ph = panel_rect.x, panel_rect.y, panel_rect.width, panel_rect.height
    # Dark overlay behind
    ov = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
    ov.fill((10, 8, 5, 200))
    surface.blit(ov, (0, 0))
    # Panel body
    pygame.draw.rect(surface, (70, 45, 25), panel_rect, border_radius=14)
    pygame.draw.rect(surface, (90, 60, 30), (px+3, py+3, pw-6, ph-6), border_radius=12)
    for gi in range(px + 15, px + pw - 15, 22):
        pygame.draw.line(surface, (80, 52, 28), (gi, py + 10), (gi, py + ph - 10), 1)
    pygame.draw.rect(surface, (50, 32, 18), panel_rect, 3, border_radius=14)
    for nx, ny in [(px+12, py+12), (px+pw-12, py+12), (px+12, py+ph-12), (px+pw-12, py+ph-12)]:
        pygame.draw.circle(surface, (60, 45, 25), (nx, ny), 5)
        pygame.draw.circle(surface, (110, 80, 45), (nx-1, ny-1), 2)
    # Title bar
    title_bar = pygame.Rect(px + 30, py + 15, pw - 60, 42)
    draw_wooden_bar(surface, title_bar, title_text, title_font, False)


def draw_wooden_slider(surface, x, y, w, volume, muted, font_tiny):
    """Draw a wooden-styled volume slider. Returns the clickable rect."""
    h = 10
    slider_rect = pygame.Rect(x, y - 6, w, h + 12)
    pygame.draw.rect(surface, (60, 40, 22), (x - 2, y - 2, w + 4, h + 4), border_radius=5)
    pygame.draw.rect(surface, (80, 55, 30), (x, y, w, h), border_radius=4)
    vol_w = int(w * volume)
    if vol_w > 0:
        for px_i in range(vol_w):
            t = px_i / w
            vc = lerp_color((80, 180, 80), (220, 80, 40), t) if not muted else (60, 35, 25)
            pygame.draw.line(surface, vc, (x + px_i, y + 1), (x + px_i, y + h - 2))
    pygame.draw.rect(surface, (50, 32, 18), (x, y, w, h), 1, border_radius=4)
    kx = x + vol_w
    pygame.draw.circle(surface, (200, 150, 80), (kx, y + h // 2), 8)
    pygame.draw.circle(surface, (240, 190, 110), (kx, y + h // 2), 5)
    pygame.draw.circle(surface, (160, 110, 55), (kx, y + h // 2), 8, 2)
    pct = font_tiny.render(f"{int(volume * 100)}%", True, (180, 150, 100))
    surface.blit(pct, (x + w + 14, y - 2))
    return slider_rect
