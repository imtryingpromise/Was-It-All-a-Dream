import pygame
import sys

from levels import level1
from levels import level2
from levels import level3
from levels import level4

pygame.init()

WIDTH, HEIGHT = 1280, 720

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("North Pole Protocol")

clock = pygame.time.Clock()

title_font = pygame.font.SysFont("arial",70)
button_font = pygame.font.SysFont("arial",35)

STATE_MENU = "menu"
STATE_LEVEL_SELECT = "level_select"
STATE_LEVEL = "level"

current_state = STATE_MENU
active_level = 0


def draw_button(rect,text):

    mx,my = pygame.mouse.get_pos()

    color = (0,200,0)

    if rect.collidepoint(mx,my):
        color = (0,255,120)

    pygame.draw.rect(screen,color,rect,border_radius=12)

    label = button_font.render(text,True,(0,0,0))

    screen.blit(label,(rect.x+rect.width//2-label.get_width()//2,
                       rect.y+rect.height//2-label.get_height()//2))


running = True

while running:

    screen.fill((15,20,40))

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            mx,my = pygame.mouse.get_pos()

            if current_state == STATE_MENU:

                if start_btn.collidepoint(mx,my):
                    current_state = STATE_LEVEL_SELECT

            elif current_state == STATE_LEVEL_SELECT:

                for i,rect in enumerate(level_buttons):

                    if rect.collidepoint(mx,my):

                        active_level = i+1
                        current_state = STATE_LEVEL

                if back_btn.collidepoint(mx,my):
                    current_state = STATE_MENU

            elif current_state == STATE_LEVEL:

                if back_btn.collidepoint(mx,my):
                    current_state = STATE_LEVEL_SELECT


    # ---------- MENU ----------

    if current_state == STATE_MENU:

        title = title_font.render("NORTH POLE PROTOCOL",True,(255,255,255))

        screen.blit(title,(WIDTH//2-title.get_width()//2,180))

        start_btn = pygame.Rect(WIDTH//2-120,400,240,70)

        draw_button(start_btn,"START GAME")


    # ---------- LEVEL SELECT ----------

    elif current_state == STATE_LEVEL_SELECT:

        title = title_font.render("SELECT LEVEL",True,(255,255,255))

        screen.blit(title,(WIDTH//2-title.get_width()//2,120))

        level_buttons = []

        for i in range(4):

            rect = pygame.Rect(260+i*200,350,140,70)

            level_buttons.append(rect)

            draw_button(rect,f"LEVEL {i+1}")

        back_btn = pygame.Rect(20,20,120,50)

        draw_button(back_btn,"BACK")


    # ---------- LEVEL ----------

    elif current_state == STATE_LEVEL:

        if active_level == 1:
            level1.run(screen)

        elif active_level == 2:
            level2.run(screen)

        elif active_level == 3:
            level3.run(screen)

        elif active_level == 4:
            level4.run(screen)

        back_btn = pygame.Rect(20,20,120,50)

        draw_button(back_btn,"BACK")


    pygame.display.flip()

    clock.tick(60)

pygame.quit()