import pygame
import sys
from settings import *

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Christmas Pixel Adventure")

clock = pygame.time.Clock()

# Load assets
background = pygame.image.load("assets/backgrounds/Menubackground.png")
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

font_title = pygame.font.Font("assets/fonts/PressStart2P.ttf", 40)
font_menu = pygame.font.Font("assets/fonts/PressStart2P.ttf", 30)
font_small = pygame.font.Font("assets/fonts/PressStart2P.ttf", 20)

# Background music
pygame.mixer.music.load("assets/audio/BackgroundMusic.mp3")
pygame.mixer.music.play(-1)

# Game states
state = "MENU"

menu_options = ["Start Game", "Select Level", "Quit Game"]
level_options = ["Level 1", "Level 2", "Level 3", "Level 4", "Back"]

selected_index = 0
current_level = ""


def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    rect = surface.get_rect(center=(x, y))
    screen.blit(surface, rect)
    return rect


def draw_menu(options, selected):
    boxes = []

    button_width = 420
    button_height = 70
    spacing = 90

    start_y = 300

    for i, option in enumerate(options):

        rect = pygame.Rect(0, 0, button_width, button_height)
        rect.center = (SCREEN_WIDTH // 2, start_y + i * spacing)

        mouse_pos = pygame.mouse.get_pos()

        if rect.collidepoint(mouse_pos):
            selected = i

        if i == selected:
            text_color = (255, 255, 0)
            border = (0, 255, 0)
        else:
            text_color = (255, 255, 255)
            border = (150, 150, 150)

        pygame.draw.rect(screen, (0, 0, 0), rect)
        pygame.draw.rect(screen, border, rect, 3)

        text = font_menu.render(option, True, text_color)
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)

        boxes.append(rect)

    return selected, boxes


running = True

while running:

    screen.blit(background, (0,0))

    if state == "MENU":
        draw_text("Christmas Pixel Adventure", font_title, (255,255,255), SCREEN_WIDTH//2, 150)
        selected_index, boxes = draw_menu(menu_options, selected_index)

    elif state == "LEVEL_SELECT":
        draw_text("Select Level", font_title, (255,255,255), SCREEN_WIDTH//2, 150)
        selected_index, boxes = draw_menu(level_options, selected_index)

    elif state == "LEVEL_PREVIEW":
        draw_text("Level Loaded", font_title, (255,255,255), SCREEN_WIDTH//2, 200)
        draw_text(current_level, font_menu, (255,255,0), SCREEN_WIDTH//2, 350)
        draw_text("Press ESC to return", font_small, (255,255,255), SCREEN_WIDTH//2, 500)

    pygame.display.update()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if state != "LEVEL_PREVIEW":

                if event.key == pygame.K_DOWN:
                    selected_index = (selected_index + 1) % len(menu_options if state == "MENU" else level_options)

                if event.key == pygame.K_UP:
                    selected_index = (selected_index - 1) % len(menu_options if state == "MENU" else level_options)

                if event.key == pygame.K_RETURN:

                    if state == "MENU":

                        if selected_index == 0:
                            current_level = "Start / Continue Game"
                            state = "LEVEL_PREVIEW"

                        elif selected_index == 1:
                            state = "LEVEL_SELECT"
                            selected_index = 0

                        elif selected_index == 2:
                            running = False

                    elif state == "LEVEL_SELECT":

                        if selected_index == 0:
                            current_level = "Level 1"
                            state = "LEVEL_PREVIEW"

                        elif selected_index == 1:
                            current_level = "Level 2"
                            state = "LEVEL_PREVIEW"

                        elif selected_index == 2:
                            current_level = "Level 3"
                            state = "LEVEL_PREVIEW"

                        elif selected_index == 3:
                            current_level = "Level 4"
                            state = "LEVEL_PREVIEW"

                        elif selected_index == 4:
                            state = "MENU"
                            selected_index = 0

            if event.key == pygame.K_ESCAPE:
                state = "MENU"
                selected_index = 0

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_pos = pygame.mouse.get_pos()

            for i, rect in enumerate(boxes):

                if rect.collidepoint(mouse_pos):

                    selected_index = i

                    if state == "MENU":

                        if i == 0:
                            current_level = "Start / Continue Game"
                            state = "LEVEL_PREVIEW"

                        elif i == 1:
                            state = "LEVEL_SELECT"
                            selected_index = 0

                        elif i == 2:
                            running = False

                    elif state == "LEVEL_SELECT":

                        if i == 0:
                            current_level = "Level 1"
                            state = "LEVEL_PREVIEW"

                        elif i == 1:
                            current_level = "Level 2"
                            state = "LEVEL_PREVIEW"

                        elif i == 2:
                            current_level = "Level 3"
                            state = "LEVEL_PREVIEW"

                        elif i == 3:
                            current_level = "Level 4"
                            state = "LEVEL_PREVIEW"

                        elif i == 4:
                            state = "MENU"
                            selected_index = 0

    clock.tick(FPS)

pygame.quit()
sys.exit()