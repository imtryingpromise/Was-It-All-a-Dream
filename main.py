import pygame
import sys
import math
import random
from settings import *
from wood_ui import draw_guide_screen

TITLE_FONT_PATH = "assets/fonts/title_font.ttf"
BTN_FONT_PATH = "assets/fonts/button_font.ttf"

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()

from levels.level1 import launch_game as launch_level1
from levels.level2 import launch_game as launch_level2
from levels.level3 import launch_game as launch_level3
from levels.level4 import launch_game as launch_level4
from levels.level4 import draw_credits_screen, get_credits_max_scroll

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Was It All A Dream?")

clock = pygame.time.Clock()

font_title = pygame.font.Font(TITLE_FONT_PATH, 52)
font_menu  = pygame.font.Font(TITLE_FONT_PATH, 22)
font_small = pygame.font.Font(TITLE_FONT_PATH, 18)
font_tiny  = pygame.font.Font(TITLE_FONT_PATH, 14)

# Background music
music_volume = 0.5
music_muted  = False
pygame.mixer.music.load("assets/audio/BackgroundMusic.mp3")
pygame.mixer.music.set_volume(music_volume)
pygame.mixer.music.play(-1)

# Game states
state = "MENU"

menu_options  = ["Start Game", "Select Level", "Settings", "Credits", "Quit Game"]
level_options = ["Level 1", "Level 2", "Level 3", "Level 4", "Back"]

selected_index = 0
current_level  = ""
tick = 0
_last_mouse_pos = (0, 0)

# --- Settings state ---
settings_cursor = 0
fullscreen = False
settings_items = ["Volume", "Mute", "Fullscreen", "Guide", "Back"]
guide_open = False
_settings_boxes = []
_settings_vol_slider = pygame.Rect(0, 0, 0, 0)

# --- Credits state ---
credits_scroll = 0.0
credits_max_scroll = get_credits_max_scroll()


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def apply_volume():
    pygame.mixer.music.set_volume(0.0 if music_muted else music_volume)


def restore_menu_music():
    pygame.mixer.music.load("assets/audio/BackgroundMusic.mp3")
    pygame.mixer.music.set_volume(0.0 if music_muted else music_volume)
    pygame.mixer.music.play(-1)


def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)
    return rect


# ── Build cached background: smooth panorama morning→afternoon→sunset→night ──
def _build_menu_bg():
    bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    W, H = SCREEN_WIDTH, SCREEN_HEIGHT

    # Sky color stops across x (left=morning, right=night) — top and bottom
    # Each entry: (x_fraction, top_color, bottom_color)
    sky_stops = [
        (0.0,  (120, 180, 255), (200, 230, 255)),   # morning — bright blue
        (0.2,  (100, 170, 250), (180, 220, 255)),   # late morning
        (0.4,  (80, 150, 230),  (170, 210, 245)),   # afternoon
        (0.55, (120, 80, 140),  (220, 140, 80)),    # early sunset
        (0.7,  (60, 30, 80),    (255, 130, 50)),    # sunset peak
        (0.82, (25, 15, 55),    (140, 50, 60)),     # late sunset
        (0.92, (12, 8, 40),     (30, 20, 55)),      # dusk
        (1.0,  (6, 4, 30),      (15, 10, 40)),      # deep night
    ]

    def get_sky_col(xt, yt):
        """Get sky color at normalized x,y position."""
        # Find which two stops we're between
        for si in range(len(sky_stops) - 1):
            x0, top0, bot0 = sky_stops[si]
            x1, top1, bot1 = sky_stops[si + 1]
            if xt <= x1:
                t = (xt - x0) / max(0.001, x1 - x0)
                top = lerp_color(top0, top1, t)
                bot = lerp_color(bot0, bot1, t)
                return lerp_color(top, bot, yt)
        return sky_stops[-1][1]

    # Draw sky pixel by pixel (x-step 2 for speed)
    for x in range(0, W, 2):
        xt = x / W
        for y in range(0, H, 2):
            yt = y / H
            c = get_sky_col(xt, yt)
            bg.fill(c, (x, y, 2, 2))

    # Stars in the night section (right side)
    rng_s = random.Random(999)
    for _ in range(60):
        sx = rng_s.randint(int(W * 0.7), W - 5)
        sy = rng_s.randint(10, int(H * 0.5))
        brightness = rng_s.randint(140, 255)
        r = 1 if rng_s.random() > 0.3 else 2
        pygame.draw.circle(bg, (brightness, brightness, brightness - 30), (sx, sy), r)

    # Sun — morning left side
    sun_x, sun_y = int(W * 0.12), 100
    for r in range(45, 25, -3):
        a = (45 - r) / 20
        sc = lerp_color((255, 220, 140), (255, 250, 230), a)
        pygame.draw.circle(bg, sc, (sun_x, sun_y), r)

    # Moon — night right side
    moon_x, moon_y = int(W * 0.9), 80
    pygame.draw.circle(bg, (220, 215, 185), (moon_x, moon_y), 28)
    pygame.draw.circle(bg, (230, 225, 200), (moon_x, moon_y), 22)
    pygame.draw.circle(bg, get_sky_col(0.9, 0.1), (moon_x + 10, moon_y - 7), 24)

    # === Mountains — two ridgelines that transition color smoothly ===
    ground_y = H - 80
    rng = random.Random(42)

    # Back ridge
    for x in range(0, W, 3):
        xt = x / W
        mh = 160 + int(math.sin(x * 0.005) * 50 + math.sin(x * 0.012) * 30)
        mh += rng.randint(-10, 10) if x % 9 == 0 else 0
        mc = lerp_color(
            lerp_color((160, 185, 220), (130, 100, 130), min(1, xt * 1.5)),
            lerp_color((80, 45, 75), (25, 20, 45), max(0, (xt - 0.5) * 2)),
            max(0, min(1, (xt - 0.3) / 0.7))
        )
        pygame.draw.line(bg, mc, (x, ground_y - mh), (x, H))
        pygame.draw.line(bg, mc, (x + 1, ground_y - mh), (x + 1, H))
        pygame.draw.line(bg, mc, (x + 2, ground_y - mh), (x + 2, H))

    # Front ridge (darker, shorter)
    rng2 = random.Random(77)
    for x in range(0, W, 3):
        xt = x / W
        mh = 100 + int(math.sin(x * 0.007 + 1) * 40 + math.sin(x * 0.015 + 2) * 20)
        mh += rng2.randint(-8, 8) if x % 7 == 0 else 0
        mc = lerp_color(
            lerp_color((120, 150, 190), (100, 70, 100), min(1, xt * 1.5)),
            lerp_color((55, 30, 60), (18, 15, 35), max(0, (xt - 0.5) * 2)),
            max(0, min(1, (xt - 0.3) / 0.7))
        )
        # Snow caps on tallest peaks
        peak_y = ground_y - mh
        pygame.draw.line(bg, mc, (x, peak_y + 15), (x, H))
        pygame.draw.line(bg, mc, (x + 1, peak_y + 15), (x + 1, H))
        pygame.draw.line(bg, mc, (x + 2, peak_y + 15), (x + 2, H))
        if mh > 120:
            cap_c = lerp_color((220, 230, 245), (80, 70, 90), min(1, xt * 1.3))
            pygame.draw.line(bg, cap_c, (x, peak_y), (x, peak_y + 15))
            pygame.draw.line(bg, cap_c, (x + 1, peak_y), (x + 1, peak_y + 15))

    # === Pine trees — layered, varied, color transitions ===
    tree_y = ground_y + 15
    rng3 = random.Random(123)
    for tx in range(5, W, 22):
        xt = tx / W
        th = rng3.randint(30, 75)
        tw2 = rng3.randint(10, 20)
        # Color transitions: green morning → dark green afternoon → dark silhouette sunset → near-black night
        if xt < 0.35:
            tc = (40 + rng3.randint(0, 15), 100 + rng3.randint(0, 35), 40 + rng3.randint(0, 15))
        elif xt < 0.6:
            t = (xt - 0.35) / 0.25
            tc = lerp_color((35, 100, 40), (30, 55, 30), t)
        elif xt < 0.8:
            t = (xt - 0.6) / 0.2
            tc = lerp_color((30, 55, 30), (15, 25, 20), t)
        else:
            tc = (8 + rng3.randint(0, 6), 14 + rng3.randint(0, 8), 10 + rng3.randint(0, 5))
        # 3-tier tree
        for tier in range(3):
            frac = tier / 3
            tw_t = int(tw2 * (1.0 - frac * 0.5))
            ty = tree_y - int(th * frac) - int(th * 0.28)
            pts = [(tx, ty - int(th * 0.28)), (tx - tw_t, ty + 4), (tx + tw_t, ty + 4)]
            pygame.draw.polygon(bg, tc, pts)
        # Trunk
        pygame.draw.rect(bg, lerp_color(tc, (50, 30, 15), 0.6), (tx - 2, tree_y - 2, 4, 6))

    # === Snowy ground — smooth color transition ===
    for y in range(tree_y + 4, H):
        depth = (y - tree_y - 4) / max(1, H - tree_y - 4)
        for x in range(0, W, 2):
            xt = x / W
            # Morning snow → afternoon → sunset warm earth → dark night ground
            if xt < 0.4:
                gc = lerp_color((210, 225, 245), (195, 210, 230), depth)
            elif xt < 0.65:
                t = (xt - 0.4) / 0.25
                day_c = lerp_color((195, 210, 230), (160, 140, 120), t)
                gc = lerp_color(day_c, lerp_color((180, 195, 215), (130, 110, 90), t), depth)
            elif xt < 0.85:
                t = (xt - 0.65) / 0.2
                gc = lerp_color(lerp_color((140, 100, 80), (60, 40, 50), t),
                                lerp_color((110, 80, 60), (40, 28, 38), t), depth)
            else:
                t = (xt - 0.85) / 0.15
                gc = lerp_color(lerp_color((40, 35, 55), (20, 18, 35), t),
                                lerp_color((30, 25, 42), (12, 10, 25), t), depth)
            bg.set_at((x, y), gc)
            if x + 1 < W:
                bg.set_at((x + 1, y), gc)

    return bg

menu_bg = _build_menu_bg()


def draw_wooden_button(surface, rect, text, font, selected, tick_val):
    """Draw a wooden plank button like the reference image."""
    x, y, w, h = rect.x, rect.y, rect.width, rect.height
    # Wood plank colors
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

    # Main plank body
    pygame.draw.rect(surface, wood_base, rect, border_radius=8)
    # Top highlight (sunlit edge)
    pygame.draw.rect(surface, wood_hi, (x + 4, y + 2, w - 8, 4), border_radius=3)
    # Bottom shadow
    pygame.draw.rect(surface, wood_dk, (x + 4, y + h - 5, w - 8, 3), border_radius=2)
    # Grain lines
    rng = random.Random(rect.y * 31 + rect.x)
    for gi in range(x + 12, x + w - 12, max(16, w // 8)):
        grain_c = lerp_color(wood_base, wood_dk, 0.15)
        pygame.draw.line(surface, grain_c, (gi, y + 5), (gi, y + h - 5), 1)
    # Nail/bolt details on sides
    for nx, ny in [(x + 10, y + h // 2), (x + w - 10, y + h // 2)]:
        pygame.draw.circle(surface, (90, 65, 30), (nx, ny), 4)
        pygame.draw.circle(surface, wood_hi, (nx - 1, ny - 1), 2)
    # Border
    pygame.draw.rect(surface, border_col, rect, 3, border_radius=8)
    # Slight inner border for depth
    pygame.draw.rect(surface, lerp_color(wood_base, wood_dk, 0.3),
                     (x + 2, y + 2, w - 4, h - 4), 1, border_radius=7)
    # Text with shadow
    txt = font.render(text, True, (50, 30, 10))
    txt_rect = txt.get_rect(center=rect.center)
    # Shadow
    shadow = font.render(text, True, (30, 18, 5))
    surface.blit(shadow, (txt_rect.x + 1, txt_rect.y + 2))
    surface.blit(txt, txt_rect)
    # Highlight shimmer on selected
    if selected:
        hi_txt = font.render(text, True, (80, 50, 20))
        surface.blit(hi_txt, (txt_rect.x, txt_rect.y - 1))


def draw_menu(options, selected):
    global _last_mouse_pos
    boxes = []
    button_width = 380
    button_height = 50
    spacing = 62
    start_y = 280

    mouse_pos = pygame.mouse.get_pos()
    mouse_moved = mouse_pos != _last_mouse_pos
    _last_mouse_pos = mouse_pos

    # Semi-transparent panel behind buttons
    panel_w = button_width + 60
    panel_h = len(options) * spacing + 30
    panel_x = SCREEN_WIDTH // 2 - panel_w // 2
    panel_y = start_y - 20
    panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (0, 0, 0, 80), (0, 0, panel_w, panel_h), border_radius=16)
    screen.blit(panel, (panel_x, panel_y))

    for i, option in enumerate(options):
        rect = pygame.Rect(0, 0, button_width, button_height)
        rect.center = (SCREEN_WIDTH // 2, start_y + i * spacing)

        if mouse_moved and rect.collidepoint(mouse_pos):
            selected = i

        draw_wooden_button(screen, rect, option, font_menu, i == selected, tick)
        boxes.append(rect)

    return selected, boxes


def draw_title(tick_val):
    """Draw the game title matching the credits style."""
    tx, ty = SCREEN_WIDTH // 2, 140
    title_str = "Was It All a Dream?"
    # Same deep navy as credits headings: (30, 30, 80)
    title_col = (30, 30, 80)

    # Shadow behind (same as credits shadow logic)
    shadow_col = tuple(max(0, int(v * 0.25)) for v in title_col)
    draw_text(title_str, font_title, shadow_col, tx + 3, ty + 3)

    # Main title
    draw_text(title_str, font_title, title_col, tx, ty)

    # Subtitle
    sub_font = pygame.font.Font(TITLE_FONT_PATH,14)
    sub = sub_font.render("A Christmas Dream Platformer", True, (80, 70, 100))
    screen.blit(sub, sub.get_rect(center=(tx, ty + 40)))


def draw_settings():
    global tick, _settings_boxes, settings_cursor, _settings_vol_slider
    _settings_boxes = []
    # Dim overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 8, 5, 200))
    screen.blit(overlay, (0, 0))

    # Wooden panel
    panel_w, panel_h = 520, 440
    panel_x = SCREEN_WIDTH // 2 - panel_w // 2
    panel_y = 110
    # Panel body — dark wood
    pygame.draw.rect(screen, (70, 45, 25), (panel_x, panel_y, panel_w, panel_h), border_radius=14)
    pygame.draw.rect(screen, (90, 60, 30), (panel_x+3, panel_y+3, panel_w-6, panel_h-6), border_radius=12)
    # Wood grain on panel
    for gi in range(panel_x+15, panel_x+panel_w-15, 20):
        pygame.draw.line(screen, (80, 52, 28), (gi, panel_y+10), (gi, panel_y+panel_h-10), 1)
    # Border with nails
    pygame.draw.rect(screen, (50, 32, 18), (panel_x, panel_y, panel_w, panel_h), 3, border_radius=14)
    for nx, ny in [(panel_x+12, panel_y+12), (panel_x+panel_w-12, panel_y+12),
                   (panel_x+12, panel_y+panel_h-12), (panel_x+panel_w-12, panel_y+panel_h-12)]:
        pygame.draw.circle(screen, (60, 45, 25), (nx, ny), 5)
        pygame.draw.circle(screen, (110, 80, 45), (nx-1, ny-1), 2)

    # Title on wooden plank
    title_bar = pygame.Rect(panel_x+30, panel_y+15, panel_w-60, 45)
    draw_wooden_button(screen, title_bar, "SETTINGS", font_menu, False, tick)

    is_fs = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)
    items_text = [
        f"Volume:  < {int(music_volume * 100)}% >",
        f"Mute:  {'ON' if music_muted else 'OFF'}",
        f"Fullscreen:  {'ON' if is_fs else 'OFF'}",
        "Guide",
        "Back",
    ]

    start_y = panel_y + 85
    spacing = 58
    bar_w = 420
    bar_h = 44

    mouse_pos = pygame.mouse.get_pos()
    mouse_moved = mouse_pos != _last_mouse_pos

    for i, item in enumerate(items_text):
        y = start_y + i * spacing
        bar_x = SCREEN_WIDTH // 2 - bar_w // 2
        bar = pygame.Rect(bar_x, y, bar_w, bar_h)
        if mouse_moved and bar.collidepoint(mouse_pos):
            settings_cursor = i
        sel = (i == settings_cursor)
        _settings_boxes.append(bar)
        draw_wooden_button(screen, bar, item, font_small, sel, tick)

    # Volume slider — wooden track style
    vbar_x = SCREEN_WIDTH // 2 - 150
    vbar_y = start_y + bar_h + 6
    vbar_w = 300
    vbar_h2 = 10
    _settings_vol_slider = pygame.Rect(vbar_x, vbar_y - 6, vbar_w, vbar_h2 + 12)
    # Track
    pygame.draw.rect(screen, (60, 40, 22), (vbar_x - 2, vbar_y - 2, vbar_w + 4, vbar_h2 + 4), border_radius=5)
    pygame.draw.rect(screen, (80, 55, 30), (vbar_x, vbar_y, vbar_w, vbar_h2), border_radius=4)
    vol_w = int(vbar_w * music_volume)
    # Fill
    if vol_w > 0:
        for px in range(vol_w):
            t2 = px / vbar_w
            vc = lerp_color((80, 180, 80), (220, 80, 40), t2) if not music_muted else (60, 35, 25)
            pygame.draw.line(screen, vc, (vbar_x + px, vbar_y+1), (vbar_x + px, vbar_y + vbar_h2 - 2))
    pygame.draw.rect(screen, (50, 32, 18), (vbar_x, vbar_y, vbar_w, vbar_h2), 1, border_radius=4)
    # Knob
    knob_x = vbar_x + vol_w
    pygame.draw.circle(screen, (200, 150, 80), (knob_x, vbar_y + vbar_h2 // 2), 8)
    pygame.draw.circle(screen, (240, 190, 110), (knob_x, vbar_y + vbar_h2 // 2), 5)
    pygame.draw.circle(screen, (160, 110, 55), (knob_x, vbar_y + vbar_h2 // 2), 8, 2)
    vol_pct = font_tiny.render(f"{int(music_volume * 100)}%", True, (180, 150, 100))
    screen.blit(vol_pct, (vbar_x + vbar_w + 14, vbar_y - 2))

    # Footer
    footer = font_tiny.render("UP/DOWN Navigate    LEFT/RIGHT Adjust    ENTER Select    ESC Back", True, (150, 120, 80))
    screen.blit(footer, footer.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_h - 18)))


def handle_level_select(index):
    global state, current_level, selected_index
    if index == 0:
        launch_level1()
        restore_menu_music()
    elif index == 1:
        launch_level2()
        restore_menu_music()
    elif index == 2:
        launch_level3()
        restore_menu_music()
    elif index == 3:
        launch_level4()
        restore_menu_music()
    elif index == 4:
        state = "MENU"
        selected_index = 0


def enter_credits():
    global state, credits_scroll, selected_index
    state = "CREDITS"
    credits_scroll = 0.0
    selected_index = 0
    pygame.mixer.music.load("assets/audio/credits.mp3")
    pygame.mixer.music.set_volume(0.0 if music_muted else music_volume)
    pygame.mixer.music.play(-1)


def exit_credits():
    global state, credits_scroll, selected_index
    credits_scroll = 0.0
    restore_menu_music()
    state = "MENU"
    selected_index = 0


running = True
boxes   = []

while running:
    tick += 1

    # Draw cached procedural background
    screen.blit(menu_bg, (0, 0))

    if state == "MENU":
        draw_title(tick)
        selected_index, boxes = draw_menu(menu_options, selected_index)

    elif state == "LEVEL_SELECT":
        draw_title(tick)
        # "Select Level" subtitle
        sub = font_small.render("Select Level", True, (255, 240, 180))
        screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 200)))
        selected_index, boxes = draw_menu(level_options, selected_index)

    elif state == "SETTINGS":
        screen.blit(menu_bg, (0, 0))
        if guide_open:
            draw_guide_screen(screen, tick, TITLE_FONT_PATH)
        else:
            draw_settings()

    elif state == "CREDITS":
        if credits_scroll < credits_max_scroll:
            credits_scroll += 0.6
        draw_credits_screen(screen, credits_scroll, tick, credits_max_scroll)

    pygame.display.update()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if state in ("MENU", "LEVEL_SELECT"):

                if event.key == pygame.K_DOWN:
                    options = menu_options if state == "MENU" else level_options
                    selected_index = (selected_index + 1) % len(options)

                if event.key == pygame.K_UP:
                    options = menu_options if state == "MENU" else level_options
                    selected_index = (selected_index - 1) % len(options)

                if event.key == pygame.K_RETURN:

                    if state == "MENU":
                        if selected_index == 0:
                            launch_level1()
                            restore_menu_music()
                        elif selected_index == 1:
                            state = "LEVEL_SELECT"
                            selected_index = 0
                        elif selected_index == 2:
                            state = "SETTINGS"
                            settings_cursor = 0
                        elif selected_index == 3:
                            enter_credits()
                        elif selected_index == 4:
                            running = False

                    elif state == "LEVEL_SELECT":
                        handle_level_select(selected_index)

            elif state == "SETTINGS":
                if guide_open:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        guide_open = False
                else:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        settings_cursor = (settings_cursor - 1) % len(settings_items)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        settings_cursor = (settings_cursor + 1) % len(settings_items)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        if settings_cursor == 0:
                            music_volume = max(0.0, round(music_volume - 0.1, 1))
                            apply_volume()
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        if settings_cursor == 0:
                            music_volume = min(1.0, round(music_volume + 0.1, 1))
                            apply_volume()
                    elif event.key == pygame.K_RETURN:
                        if settings_cursor == 1:
                            music_muted = not music_muted
                            apply_volume()
                        elif settings_cursor == 2:
                            pygame.display.toggle_fullscreen()
                        elif settings_cursor == 3:
                            guide_open = True
                        elif settings_cursor == 4:
                            state = "MENU"
                            selected_index = 0

            elif state == "CREDITS":
                if event.key == pygame.K_RETURN:
                    exit_credits()

            if event.key == pygame.K_ESCAPE:
                if state == "SETTINGS" and guide_open:
                    pass  # handled above
                elif state == "CREDITS":
                    exit_credits()
                else:
                    state = "MENU"
                    selected_index = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if state in ("MENU", "LEVEL_SELECT"):
                for i, rect in enumerate(boxes):
                    if rect.collidepoint(mouse_pos):
                        selected_index = i
                        if state == "MENU":
                            if i == 0:
                                launch_level1()
                                restore_menu_music()
                            elif i == 1:
                                state = "LEVEL_SELECT"
                                selected_index = 0
                            elif i == 2:
                                state = "SETTINGS"
                                settings_cursor = 0
                            elif i == 3:
                                enter_credits()
                            elif i == 4:
                                running = False
                        elif state == "LEVEL_SELECT":
                            handle_level_select(i)
            elif state == "SETTINGS":
                if guide_open:
                    guide_open = False
                elif _settings_vol_slider.collidepoint(mouse_pos):
                    music_volume = max(0.0, min(1.0, round((mouse_pos[0] - _settings_vol_slider.x) / _settings_vol_slider.width, 2)))
                    apply_volume()
                    settings_cursor = 0
                else:
                    for i, rect in enumerate(_settings_boxes):
                        if rect.collidepoint(mouse_pos):
                            settings_cursor = i
                            if i == 1:
                                music_muted = not music_muted
                                apply_volume()
                            elif i == 2:
                                pygame.display.toggle_fullscreen()
                            elif i == 3:
                                guide_open = True
                            elif i == 4:
                                state = "MENU"
                                selected_index = 0

    clock.tick(FPS)

pygame.quit()
sys.exit()
