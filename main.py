import pygame
import sys
import math
from settings import *

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

# Load assets
background = pygame.image.load("assets/backgrounds/Menubackground.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

font_title = pygame.font.Font("assets/fonts/PressStart2P.ttf", 40)
font_menu  = pygame.font.Font("assets/fonts/PressStart2P.ttf", 30)
font_small = pygame.font.Font("assets/fonts/PressStart2P.ttf", 20)
font_tiny  = pygame.font.SysFont("consolas", 14)

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
_last_mouse_pos = (0, 0)  # track mouse movement for hover detection

# --- Settings state ---
settings_cursor = 0
settings_items = ["Volume", "Mute", "Back"]
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


def draw_menu(options, selected):
    global _last_mouse_pos
    boxes = []
    button_width  = 420
    button_height = 60
    spacing       = 75
    start_y       = 260

    mouse_pos = pygame.mouse.get_pos()
    mouse_moved = mouse_pos != _last_mouse_pos
    _last_mouse_pos = mouse_pos

    for i, option in enumerate(options):
        rect = pygame.Rect(0, 0, button_width, button_height)
        rect.center = (SCREEN_WIDTH // 2, start_y + i * spacing)

        if mouse_moved and rect.collidepoint(mouse_pos):
            selected = i

        if i == selected:
            text_color = (255, 255, 0)
            border     = (0, 255, 0)
        else:
            text_color = (255, 255, 255)
            border     = (150, 150, 150)

        pygame.draw.rect(screen, (0, 0, 0), rect)
        pygame.draw.rect(screen, border, rect, 3)

        text      = font_menu.render(option, True, text_color)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
        boxes.append(rect)

    return selected, boxes


def draw_settings():
    global tick, _settings_boxes, settings_cursor, _settings_vol_slider
    _settings_boxes = []
    # Dark overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((15, 15, 25, 210))
    screen.blit(overlay, (0, 0))

    # Main panel
    panel_w, panel_h = 500, 360
    panel_x = SCREEN_WIDTH // 2 - panel_w // 2
    panel_y = 120
    panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, (25, 25, 40, 200), (0, 0, panel_w, panel_h), border_radius=16)
    pygame.draw.rect(panel_surf, (80, 80, 100, 120), (0, 0, panel_w, panel_h), 2, border_radius=16)
    screen.blit(panel_surf, (panel_x, panel_y))

    # Title
    title_surf = font_title.render("Settings", True, (255, 255, 0))
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, panel_y + 45))
    glow_s = pygame.Surface((title_rect.width + 40, title_rect.height + 20), pygame.SRCALPHA)
    glow_a = int(abs(math.sin(tick * 0.04)) * 30) + 25
    pygame.draw.rect(glow_s, (255, 200, 50, glow_a), (0, 0, glow_s.get_width(), glow_s.get_height()), border_radius=12)
    screen.blit(glow_s, (title_rect.x - 20, title_rect.y - 10))
    screen.blit(title_surf, title_rect)

    # Items
    items_text = [
        f"Volume:  < {int(music_volume * 100)}% >",
        f"Mute:  {'ON' if music_muted else 'OFF'}",
        "Back",
    ]
    item_colors = [(255, 255, 255), (255, 255, 255), (0, 255, 0)]

    start_y = panel_y + 100
    spacing = 60
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
        bar_surf = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
        if sel:
            pygame.draw.rect(bar_surf, (50, 45, 30, 180), (0, 0, bar_w, bar_h), border_radius=8)
            screen.blit(bar_surf, bar.topleft)
            pygame.draw.rect(screen, (220, 180, 60), bar, 2, border_radius=8)
            color = item_colors[i]
        else:
            pygame.draw.rect(bar_surf, (35, 35, 50, 140), (0, 0, bar_w, bar_h), border_radius=8)
            screen.blit(bar_surf, bar.topleft)
            pygame.draw.rect(screen, (70, 70, 90, 80), bar, 1, border_radius=8)
            color = (180, 180, 195)

        # Icons
        icon_x = bar_x + 18
        icon_cy = y + bar_h // 2
        if i == 0:
            pygame.draw.rect(screen, color, (icon_x, icon_cy - 4, 6, 8))
            pygame.draw.polygon(screen, color, [(icon_x + 6, icon_cy - 4), (icon_x + 12, icon_cy - 8),
                                                (icon_x + 12, icon_cy + 8), (icon_x + 6, icon_cy + 4)])
            for sw in range(2):
                arc_r = 5 + sw * 4
                pygame.draw.arc(screen, color, (icon_x + 13, icon_cy - arc_r, arc_r * 2, arc_r * 2), -0.6, 0.6, 1)
        elif i == 1:
            pygame.draw.rect(screen, color, (icon_x, icon_cy - 4, 6, 8))
            pygame.draw.polygon(screen, color, [(icon_x + 6, icon_cy - 4), (icon_x + 12, icon_cy - 8),
                                                (icon_x + 12, icon_cy + 8), (icon_x + 6, icon_cy + 4)])
            if music_muted:
                pygame.draw.line(screen, (220, 60, 60), (icon_x + 15, icon_cy - 5), (icon_x + 22, icon_cy + 5), 2)
                pygame.draw.line(screen, (220, 60, 60), (icon_x + 22, icon_cy - 5), (icon_x + 15, icon_cy + 5), 2)
        elif i == 2:
            pygame.draw.polygon(screen, color, [(icon_x + 12, icon_cy - 7), (icon_x + 3, icon_cy), (icon_x + 12, icon_cy + 7)])

        txt = font_small.render(item, True, color)
        screen.blit(txt, (bar_x + 42, y + (bar_h - txt.get_height()) // 2))

    # Volume slider below volume item
    vbar_x = SCREEN_WIDTH // 2 - 150
    vbar_y = start_y + bar_h + 4
    vbar_w = 300
    vbar_h2 = 10
    _settings_vol_slider = pygame.Rect(vbar_x, vbar_y - 6, vbar_w, vbar_h2 + 12)
    pygame.draw.rect(screen, (40, 40, 55), (vbar_x - 2, vbar_y - 2, vbar_w + 4, vbar_h2 + 4), border_radius=5)
    vol_w = int(vbar_w * music_volume)
    for px in range(vol_w):
        t2 = px / vbar_w
        vc = lerp_color((0, 255, 0), (255, 0, 0), t2) if not music_muted else (80, 30, 30)
        pygame.draw.line(screen, vc, (vbar_x + px, vbar_y), (vbar_x + px, vbar_y + vbar_h2 - 1))
    pygame.draw.rect(screen, (100, 100, 120), (vbar_x, vbar_y, vbar_w, vbar_h2), 1, border_radius=4)
    knob_x = vbar_x + vol_w
    pygame.draw.circle(screen, (255, 255, 255), (knob_x, vbar_y + vbar_h2 // 2), 8)
    pygame.draw.circle(screen, (255, 255, 0), (knob_x, vbar_y + vbar_h2 // 2), 5)
    vol_pct = font_tiny.render(f"{int(music_volume * 100)}%", True, (160, 160, 180))
    screen.blit(vol_pct, (vbar_x + vbar_w + 14, vbar_y - 2))

    # Footer
    footer = font_tiny.render("UP/DOWN Navigate    LEFT/RIGHT Adjust    ENTER Select    ESC Back", True, (120, 120, 140))
    screen.blit(footer, footer.get_rect(center=(SCREEN_WIDTH // 2, panel_y + panel_h - 20)))


def handle_level_select(index):
    """Launch a level by its menu index, or go back."""
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

    screen.blit(background, (0, 0))

    if state == "MENU":
        # Title with outline for readability
        tx, ty = SCREEN_WIDTH // 2, 150
        title_str = "Was It All a Dream?"
        outline_color = (255, 255, 255)
        title_color = (30, 30, 80)
        for ox, oy in [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)]:
            draw_text(title_str, font_title, outline_color, tx + ox, ty + oy)
        draw_text(title_str, font_title, title_color, tx, ty)
        selected_index, boxes = draw_menu(menu_options, selected_index)

    elif state == "LEVEL_SELECT":
        draw_text("Select Level", font_title,
                  (255, 255, 255), SCREEN_WIDTH // 2, 150)
        selected_index, boxes = draw_menu(level_options, selected_index)

    elif state == "LEVEL_PREVIEW":
        draw_text("Level Loaded", font_title,
                  (255, 255, 255), SCREEN_WIDTH // 2, 200)
        draw_text(current_level, font_menu,
                  (255, 255, 0), SCREEN_WIDTH // 2, 350)
        draw_text("Press ESC to return", font_small,
                  (255, 255, 255), SCREEN_WIDTH // 2, 500)

    elif state == "SETTINGS":
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
                        state = "MENU"
                        selected_index = 0

            elif state == "CREDITS":
                if event.key == pygame.K_RETURN:
                    exit_credits()

            if event.key == pygame.K_ESCAPE:
                if state == "CREDITS":
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
                # Click on volume slider to set volume
                if _settings_vol_slider.collidepoint(mouse_pos):
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
                                state = "MENU"
                                selected_index = 0

    clock.tick(FPS)

pygame.quit()
sys.exit()