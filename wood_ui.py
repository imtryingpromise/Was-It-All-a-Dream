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


_GUIDE_MAIN = [
    ("CONTROLS", [
        "WASD / Arrow Keys - Move",
        "SPACE / W / UP - Jump",
        "SHIFT - Sprint / Dash",
        "E - Talk to NPCs",
        "R - Respawn / Restart",
        "ESC - Settings Menu",
        "LEFT CLICK - Shoot (Level 2, 3 & 4)",
    ]),
    ("GAMEPLAY", [
        "Four dream realms to conquer",
        "Each realm has unique mechanics",
        "Reach checkpoints to save progress",
        "Find the exit gate to clear the realm",
    ]),
    ("TIPS", [
        "Talk to NPCs for story and hints",
        "Try different difficulties in settings",
        "Each level gets harder - good luck!",
    ]),
]

_GUIDE_L1 = [
    ("CONTROLS", [
        "WASD / Arrow Keys - Move",
        "SPACE / W - Jump (double jump!)",
        "E - Talk to NPCs",
        "R - Restart Level",
        "ESC - Settings Menu",
    ]),
    ("PLATFORMS", [
        "Ice platforms shrink when you stand",
        "Wood platforms fall after landing",
        "Phantom platforms blink in and out",
        "Countdown platforms need timing",
        "Zigzag sections test precision",
    ]),
    ("TIPS", [
        "Double jump to reach higher areas",
        "Grab the balloon for a boost",
        "Watch the countdown timer on blue platforms",
        "Checkpoints save your progress",
    ]),
]

_GUIDE_L2 = [
    ("CONTROLS", [
        "WASD / Arrow Keys - Move",
        "SPACE / W - Jump (double jump!)",
        "SHIFT - Sprint",
        "LEFT CLICK - Fire ice arrow",
        "E - Talk to NPCs",
        "ESC - Settings Menu",
    ]),
    ("COMBAT", [
        "Stomp mushrooms by landing on top",
        "Shoot enemies with ice arrows",
        "Watch out for the Santa boss!",
        "Arrows can hit multiple targets",
    ]),
    ("TIPS", [
        "Sprint to build speed for long gaps",
        "Stomp chains give combo bonuses",
        "Use arrows from a safe distance",
        "Boss fights need patience and aim",
    ]),
]

_GUIDE_L3 = [
    ("CONTROLS", [
        "WASD / Arrow Keys - Move",
        "SPACE - Jump (single jump)",
        "SHIFT - Sprint / Airborne Dash",
        "LEFT CLICK - Throw snowball",
        "E - Talk to NPCs",
        "R - Respawn",
        "ESC - Settings Menu",
    ]),
    ("MECHANICS", [
        "Dash mid-air for extra distance",
        "Wall slide by pressing into walls",
        "Wall jump off walls with SPACE",
        "Stomp flying monsters from above",
        "Snowball bosses at checkpoints",
    ]),
    ("TIPS", [
        "Dash is key for crossing big gaps",
        "Wall jump between narrow walls",
        "Bosses retreat past checkpoints",
        "Collapsing platforms reset on death",
    ]),
]

_GUIDE_L4 = [
    ("CONTROLS", [
        "WASD / Arrow Keys - Move",
        "SPACE - Jump (double jump!)",
        "SHIFT - Sprint / Dash",
        "LEFT CLICK - Shoot",
        "F / X - Shoot (alternate)",
        "E - Talk to NPCs",
        "ESC - Settings Menu",
    ]),
    ("COMBAT & HAZARDS", [
        "Stomp mushrooms from above",
        "Shoot or stomp bomb enemies",
        "Dodge saw blades and icicles",
        "Collect ornaments to unlock exit",
        "Survive the final meteor run!",
    ]),
    ("TIPS", [
        "Wall jump between narrow walls",
        "Dash mid-air to dodge hazards",
        "Heart pickups restore health",
        "The final path tests everything",
    ]),
]


def draw_guide_screen(surface, tick, font_title_path, sections=None):
    """Draw a fullscreen game guide overlay. Pass sections for level-specific guide."""
    if sections is None:
        sections = _GUIDE_MAIN
    W, H = surface.get_width(), surface.get_height()

    # Dark overlay
    ov = pygame.Surface((W, H), pygame.SRCALPHA)
    ov.fill((10, 8, 5, 220))
    surface.blit(ov, (0, 0))

    # Wooden panel
    panel_w = min(600, W - 40)
    panel_h = min(560, H - 40)
    panel_x = W // 2 - panel_w // 2
    panel_y = H // 2 - panel_h // 2
    panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
    title_font = pygame.font.Font(font_title_path, 22)
    draw_wooden_panel(surface, panel_rect, "GAME GUIDE", title_font)

    header_font = pygame.font.Font(font_title_path, 18)
    body_font = pygame.font.Font(font_title_path, 13)

    header_col = (220, 180, 60)
    body_col = (200, 190, 170)
    shadow_col = (20, 15, 10)

    cx = W // 2
    y = panel_y + 65

    for sec_title, lines in sections:
        sh = header_font.render(sec_title, True, shadow_col)
        surface.blit(sh, sh.get_rect(center=(cx + 1, y + 1)))
        ht = header_font.render(sec_title, True, header_col)
        surface.blit(ht, ht.get_rect(center=(cx, y)))
        y += 22
        for line in lines:
            bs = body_font.render(line, True, shadow_col)
            surface.blit(bs, bs.get_rect(center=(cx + 1, y + 1)))
            bt = body_font.render(line, True, body_col)
            surface.blit(bt, bt.get_rect(center=(cx, y)))
            y += 16
        y += 8

    close_font = pygame.font.Font(font_title_path, 13)
    cs = close_font.render("Press ESC or ENTER to close", True, shadow_col)
    surface.blit(cs, cs.get_rect(center=(cx + 1, panel_y + panel_h - 18)))
    ct = close_font.render("Press ESC or ENTER to close", True, header_col)
    surface.blit(ct, ct.get_rect(center=(cx, panel_y + panel_h - 20)))

    return True
