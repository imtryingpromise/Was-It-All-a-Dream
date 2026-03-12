import pygame
from settings import *

def run_level4(screen):

    clock = pygame.time.Clock()

    pygame.mixer.music.stop()
    pygame.mixer.music.load("assets/audio/Level4Music.mp3")
    pygame.mixer.music.play(-1)

    player = pygame.Rect(120,520,40,60)

    vel_y = 0
    on_ground = False

    glitch_state = 0
    section = 1

    spawn = (120,520)

    portal = pygame.Rect(1050,500,70,90)

    running = True

    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_ESCAPE]:
            running = False

        if keys[pygame.K_a]:
            player.x -= PLAYER_SPEED

        if keys[pygame.K_d]:
            player.x += PLAYER_SPEED

        if keys[pygame.K_w] and on_ground:
            vel_y = JUMP_FORCE
            glitch_state = 1 - glitch_state

        vel_y += GRAVITY
        player.y += vel_y

        on_ground = False

        # ---------- PUZZLE DEFINITIONS ----------

        if section == 1:

            spawn = (120,520)

            permanent = [pygame.Rect(0,580,200,40)]

            platforms_A = [
                pygame.Rect(300,520,120,20),
                pygame.Rect(520,480,120,20)
            ]

            platforms_B = [
                pygame.Rect(220,540,120,20),
                pygame.Rect(450,500,120,20)
            ]

            spikes = []

        elif section == 2:

            spawn = (120,520)

            permanent = [pygame.Rect(0,580,200,40)]

            platforms_A = [
                pygame.Rect(320,520,110,20),
                pygame.Rect(540,470,110,20),
                pygame.Rect(760,430,110,20)
            ]

            platforms_B = [
                pygame.Rect(240,540,110,20),
                pygame.Rect(470,500,110,20),
                pygame.Rect(690,460,110,20)
            ]

            spikes = [pygame.Rect(400,580,80,20)]

        elif section == 3:

            spawn = (120,520)

            permanent = [pygame.Rect(0,580,200,40)]

            platforms_A = [
                pygame.Rect(350,520,90,20),
                pygame.Rect(560,480,90,20),
                pygame.Rect(770,440,90,20)
            ]

            platforms_B = [
                pygame.Rect(260,540,90,20),
                pygame.Rect(470,500,90,20),
                pygame.Rect(680,460,90,20)
            ]

            spikes = [
                pygame.Rect(420,580,70,20),
                pygame.Rect(620,580,70,20)
            ]

        elif section == 4:

            spawn = (120,520)

            permanent = [pygame.Rect(0,580,200,40)]

            platforms_A = [
                pygame.Rect(380,520,80,20),
                pygame.Rect(560,480,80,20),
                pygame.Rect(740,440,80,20),
                pygame.Rect(920,400,80,20)
            ]

            platforms_B = [
                pygame.Rect(280,540,80,20),
                pygame.Rect(470,500,80,20),
                pygame.Rect(660,460,80,20),
                pygame.Rect(850,420,80,20)
            ]

            spikes = [pygame.Rect(500,580,90,20)]

        else:

            spawn = (120,520)

            permanent = [pygame.Rect(0,580,200,40)]

            platforms_A = [
                pygame.Rect(420,520,80,20),
                pygame.Rect(620,480,80,20),
                pygame.Rect(820,440,80,20),
                pygame.Rect(1000,400,80,20)
            ]

            platforms_B = [
                pygame.Rect(320,540,80,20),
                pygame.Rect(520,500,80,20),
                pygame.Rect(720,460,80,20),
                pygame.Rect(920,420,80,20)
            ]

            spikes = [
                pygame.Rect(450,580,80,20),
                pygame.Rect(650,580,80,20)
            ]

        active = platforms_A if glitch_state == 0 else platforms_B

        # ----- COLLISIONS -----

        for p in permanent:
            if player.colliderect(p) and vel_y > 0:
                player.bottom = p.top
                vel_y = 0
                on_ground = True

        for p in active:
            if player.colliderect(p) and vel_y > 0:
                player.bottom = p.top
                vel_y = 0
                on_ground = True

        for s in spikes:
            if player.colliderect(s):
                player.x,player.y = spawn
                vel_y = 0

        # ----- FALL DETECTION -----

        if player.y > SCREEN_HEIGHT:

            section += 1

            if section > 5:
                section = 5

            player.x,player.y = spawn
            vel_y = 0

        # ----- EXIT -----

        if section == 5 and player.colliderect(portal):
            running = False

        # ----- DRAW -----

        screen.fill((230,190,40))

        for p in permanent:
            pygame.draw.rect(screen,(30,30,30),p)

        if glitch_state == 0:
            for p in platforms_A:
                pygame.draw.rect(screen,(60,60,60),p)

        if glitch_state == 1:
            for p in platforms_B:
                pygame.draw.rect(screen,(120,120,120),p)

        for s in spikes:
            pygame.draw.rect(screen,(255,255,255),s)

        if section == 5:
            pygame.draw.rect(screen,(255,255,0),portal)

        pygame.draw.rect(screen,(0,0,0),player)

        pygame.display.update()
        clock.tick(FPS)